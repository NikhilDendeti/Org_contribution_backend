"""Interactor for uploading initial XLSX and generating Pod Lead allocation sheets."""
from datetime import datetime, date
from pathlib import Path
from django.conf import settings
from contributions.services import initial_xlsx_parser_service, sheet_generation_service
from contributions.storages import (
    pod_lead_allocation_storage, employee_storage, pod_storage, department_storage
)
from contributions.exceptions import ValidationException, DomainException
from decimal import Decimal


class InitialXLSXUploadInteractor:
    """Interactor for uploading initial XLSX and generating Pod Lead sheets."""
    
    def __init__(self, file_path: str, month: str):
        self.file_path = file_path
        self.month = month
    
    def execute(self) -> dict:
        """Execute the upload and sheet generation process."""
        # Validate month format
        try:
            month_date = datetime.strptime(self.month, '%Y-%m').date()
            month_date = date(month_date.year, month_date.month, 1)
        except ValueError:
            raise ValidationException(f"Invalid month format: {self.month}. Expected YYYY-MM")
        
        # Resolve file path
        if not Path(self.file_path).is_absolute():
            file_path = Path(settings.BASE_DIR) / self.file_path
        else:
            file_path = Path(self.file_path)
        
        if not file_path.exists():
            raise DomainException(f"File not found: {file_path}")
        
        # Parse initial XLSX (only processes sub-sheets: Tech, Finance, Sales, Marketing, Business)
        # Master sheet is automatically skipped
        employee_data, errors = initial_xlsx_parser_service.parse_initial_xlsx(str(file_path))
        
        if errors and not employee_data:
            raise ValidationException("Failed to parse initial XLSX", errors={'rows': errors})
        
        # Group employees by pod/team FROM THE FILE ONLY
        # This ensures we only process pods/teams that exist in the uploaded file
        pod_employee_map = {}  # {pod_name: {dept_name: [employee_data]}}
        
        for emp_code, emp_info in employee_data.items():
            pod_name = emp_info.get('pod', '').strip()
            dept_name = emp_info.get('department', '').strip()
            
            if not pod_name or not dept_name:
                continue
            
            if pod_name not in pod_employee_map:
                pod_employee_map[pod_name] = {}
            
            if dept_name not in pod_employee_map[pod_name]:
                pod_employee_map[pod_name][dept_name] = []
            
            pod_employee_map[pod_name][dept_name].append(emp_info)
        
        # Group by department/sub-sheet for response
        department_sheets = {}  # {dept_name: {'pods': [], 'skipped_pods': []}}
        created_allocations = 0
        
        # Process ONLY pods/teams from the file (not all pods in database)
        # Iterate through pods found in the uploaded file
        for pod_name, dept_map in pod_employee_map.items():
            # Get department (should be same for all employees in a pod)
            dept_name = list(dept_map.keys())[0] if dept_map else None
            if not dept_name:
                continue
            
            # Initialize department entry if not exists
            if dept_name not in department_sheets:
                department_sheets[dept_name] = {
                    'department': dept_name,
                    'pods': [],
                    'skipped_pods': []
                }
            
            # Get or create department
            dept = department_storage.get_or_create_department(dept_name)
            
            # Get or create pod
            pod = pod_storage.get_or_create_pod(pod_name, dept.id)
            
            # Get Pod Lead for this pod
            employees = employee_storage.list_employees_by_pod(pod.id)
            pod_lead = None
            for emp in employees:
                if emp.role == 'POD_LEAD':
                    pod_lead = emp
                    break
            
            if not pod_lead:
                # Skip pods without Pod Lead - add to skipped_pods for this department
                department_sheets[dept_name]['skipped_pods'].append({
                    'pod_name': pod_name,
                    'employee_count': sum(len(emp_list) for emp_list in dept_map.values()),
                    'reason': 'No Pod Lead assigned'
                })
                continue
            
            # Get employees from file for this pod
            pod_employee_data = {}
            for emp_info_list in dept_map.values():
                for emp_info in emp_info_list:
                    emp_code = emp_info['employee_code']
                    
                    # Get or create employee
                    try:
                        employee = employee_storage.get_employee_by_code(emp_code)
                        # Update employee's pod/department if needed
                        if employee.pod_id != pod.id or employee.department_id != dept.id:
                            from core.models import Employee
                            emp_model = Employee.objects.get(id=employee.id)
                            emp_model.pod_id = pod.id
                            emp_model.department_id = dept.id
                            emp_model.save()
                    except:
                        # Employee doesn't exist, create it
                        employee = employee_storage.get_or_create_employee(
                            employee_code=emp_code,
                            name=emp_info.get('employee_name', ''),
                            email=emp_info.get('email', ''),
                            department_id=dept.id,
                            pod_id=pod.id,
                            role='EMPLOYEE'
                        )
                    
                    # Convert to format expected by sheet generation
                    pod_employee_data[emp_code] = emp_info['products']
            
            if not pod_employee_data:
                continue
            
            # Create allocation records (one per product per employee)
            for emp_code, products in pod_employee_data.items():
                # Get employee (already created/updated above)
                try:
                    employee = employee_storage.get_employee_by_code(emp_code)
                except:
                    continue
                
                # Get employee baseline hours
                from core.models import Employee
                emp_model = Employee.objects.get(id=employee.id)
                baseline_hours = emp_model.monthly_baseline_hours or Decimal('160.00')
                
                for product_data in products:
                    # Check if allocation already exists
                    existing = pod_lead_allocation_storage.get_allocation_by_employee_product_month(
                        employee.id,
                        product_data['product'],
                        month_date
                    )
                    
                    if not existing:
                        pod_lead_allocation_storage.create_allocation(
                            employee_id=employee.id,
                            pod_lead_id=pod_lead.id,
                            contribution_month=month_date,
                            product=product_data['product'],
                            product_description=product_data['description'],
                            baseline_hours=baseline_hours,
                            status='PENDING'
                        )
                        created_allocations += 1
            
            # Generate sheet for this pod
            sheet_path = sheet_generation_service.generate_pod_lead_allocation_sheets(
                pod.id,
                month_date,
                pod_employee_data
            )
            
            # Generate API download URL (use API endpoint instead of direct media URL)
            from django.urls import reverse
            api_download_url = reverse('contributions:download_allocation_sheet', kwargs={'pod_id': pod.id})
            api_download_url = f"{api_download_url}?month={self.month}"
            
            # Add pod sheet to department
            department_sheets[dept_name]['pods'].append({
                'pod_id': pod.id,
                'pod_name': pod.name,
                'pod_lead_code': pod_lead.employee_code,
                'sheet_path': str(sheet_path.relative_to(Path(settings.MEDIA_ROOT))),
                'download_url': api_download_url,  # API endpoint URL
                'media_url': sheet_generation_service.get_sheet_download_url(sheet_path)  # Direct media URL (fallback)
            })
        
        # Convert to list format for response
        teams = []
        total_sheets = 0
        total_skipped_pods = 0
        teams_with_sheets = 0  # Count of teams/departments that have at least one sheet
        
        for dept_name, dept_data in sorted(department_sheets.items()):
            pods_count = len(dept_data['pods'])
            skipped_count = len(dept_data['skipped_pods'])
            total_sheets += pods_count
            total_skipped_pods += skipped_count
            
            # Count teams that have at least one sheet
            if pods_count > 0:
                teams_with_sheets += 1
            
            teams.append({
                'department': dept_name,
                'pods_with_sheets': pods_count,
                'pods_skipped': skipped_count,
                'pods': dept_data['pods'],
                'skipped_pods': dept_data['skipped_pods']
            })
        
        return {
            'summary': {
                'generated_sheets': total_sheets,  # Total pod sheets generated (3)
                'created_allocations': created_allocations,
                'month': self.month,
                'total_employees': len(employee_data),
                'total_pods_in_file': len(pod_employee_map),
                'pods_with_sheets': total_sheets,  # Same as generated_sheets
                'pods_skipped': total_skipped_pods,
                'teams_processed': len(teams),  # Total teams/departments processed (5)
                'teams_with_sheets': teams_with_sheets  # Teams that have at least one sheet (2)
            },
            'teams': teams,
            'errors': errors if errors else [],
            'has_errors': len(errors) > 0
        }

