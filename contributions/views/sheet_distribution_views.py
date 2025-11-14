"""Views for sheet distribution."""
from rest_framework.views import APIView
from rest_framework.request import Request
from contributions.interactors.feature_csv_upload_interactor import UploadFeatureCSVInteractor
from contributions.presenters.error_presenter import present_error
from contributions.common.response import success_response
from contributions.utils.auth_middleware import get_employee_from_request
from contributions.exceptions import DomainException, PermissionDeniedException
from django.conf import settings
from pathlib import Path


class GenerateAllPodSheetsView(APIView):
    """View for generating sheets for all pods."""
    
    def post(self, request: Request):
        """Generate allocation sheets for all pods."""
        try:
            # Get employee from token
            employee = get_employee_from_request(request)
            
            # Check admin/CEO permission
            if not (employee.role == 'ADMIN' or employee.role == 'CEO'):
                raise PermissionDeniedException("Only ADMIN or CEO can generate sheets")
            
            # Get month parameter (from query params or body)
            month = request.query_params.get('month') or request.data.get('month')
            if not month:
                return success_response(
                    data={'error': 'month parameter is required (as query param ?month=YYYY-MM or in request body)'},
                    message='Missing required parameter',
                    status_code=400
                )
            
            # Get file path (optional - if not provided, use existing feature data)
            file_path = request.data.get('file_path')
            
            if file_path:
                # Use provided file path
                if not Path(file_path).is_absolute():
                    file_path = Path(settings.BASE_DIR) / file_path
                else:
                    file_path = Path(file_path)
                
                if not file_path.exists():
                    return success_response(
                        data={'error': f'File not found: {file_path}'},
                        message='File not found',
                        status_code=404
                    )
                
                # Execute upload interactor
                interactor = UploadFeatureCSVInteractor(str(file_path), month)
                result = interactor.execute()
                
                return success_response(
                    data=result,
                    message='Sheets generated successfully for all pods'
                )
            else:
                # Generate sheets from existing allocations
                from contributions.storages import (
                    pod_lead_allocation_storage, pod_storage, department_storage, employee_storage
                )
                from contributions.services import sheet_generation_service
                from datetime import datetime, date
                
                month_date = datetime.strptime(month, '%Y-%m').date()
                month_date = date(month_date.year, month_date.month, 1)
                
                # Get all pods and generate sheets
                departments = department_storage.list_departments()
                generated_sheets = []
                
                for dept in departments:
                    pods = pod_storage.list_pods_by_department(dept.id)
                    
                    for pod in pods:
                        # Get Pod Lead
                        employees = employee_storage.list_employees_by_pod(pod.id)
                        pod_lead = None
                        for emp in employees:
                            if emp.role == 'POD_LEAD':
                                pod_lead = emp
                                break
                        
                        if not pod_lead:
                            continue
                        
                        # Get allocations to extract features
                        allocations = pod_lead_allocation_storage.get_allocations_by_pod_lead(
                            pod_lead.id, month_date
                        )
                        
                        # Build employee features dict
                        employee_features = {}
                        for alloc in allocations:
                            if alloc.features_text:
                                employee_features[alloc.employee_code] = alloc.features_text
                        
                        # Generate sheet
                        sheet_path = sheet_generation_service.generate_pod_lead_allocation_sheets(
                            pod.id,
                            month_date,
                            employee_features
                        )
                        
                        generated_sheets.append({
                            'pod_id': pod.id,
                            'pod_name': pod.name,
                            'pod_lead_code': pod_lead.employee_code,
                            'sheet_path': str(sheet_path.relative_to(Path(settings.MEDIA_ROOT))),
                            'download_url': sheet_generation_service.get_sheet_download_url(sheet_path)
                        })
                
                return success_response(
                    data={
                        'summary': {
                            'generated_sheets': len(generated_sheets),
                            'month': month
                        },
                        'sheets': generated_sheets
                    },
                    message='Sheets generated successfully for all pods'
                )
        
        except PermissionDeniedException as e:
            return present_error(e)
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to generate sheets: {str(e)}"))

