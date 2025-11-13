"""Metrics interactors for dashboard data."""
from datetime import datetime, date
from contributions.services import metrics_calculator_service, permission_service
from contributions.storages.storage_dto import OrgMetricsDTO, DepartmentMetricsDTO, PodMetricsDTO, EmployeeMetricsDTO
from contributions.exceptions import ValidationException, PermissionDeniedException


class GetOrgMetricsInteractor:
    """Interactor for getting organization-level metrics."""
    
    def __init__(self, month: str, employee_id: int):
        self.month = month
        self.employee_id = employee_id
    
    def execute(self) -> OrgMetricsDTO:
        """Execute the metrics calculation."""
        # Validate month format
        try:
            month_date = datetime.strptime(self.month, '%Y-%m').date()
            month_date = date(month_date.year, month_date.month, 1)
        except ValueError:
            raise ValidationException(f"Invalid month format: {self.month}. Expected YYYY-MM")
        
        # Check CEO permission with better error message
        try:
            permission_service.check_ceo_permission(self.employee_id)
        except PermissionDeniedException as e:
            # Add employee info to error for debugging
            from contributions.storages import employee_storage
            try:
                employee = employee_storage.get_employee_by_id(self.employee_id)
                raise PermissionDeniedException(
                    f"CEO access required. Current user: {employee.employee_code} (Role: {employee.role})"
                )
            except:
                raise e
        
        # Calculate metrics
        return metrics_calculator_service.calculate_org_metrics(month_date)


class GetDepartmentMetricsInteractor:
    """Interactor for getting department-level metrics."""
    
    def __init__(self, department_id: int, month: str, employee_id: int):
        self.department_id = department_id
        self.month = month
        self.employee_id = employee_id
    
    def execute(self) -> DepartmentMetricsDTO:
        """Execute the metrics calculation."""
        # Validate month format
        try:
            month_date = datetime.strptime(self.month, '%Y-%m').date()
            month_date = date(month_date.year, month_date.month, 1)
        except ValueError:
            raise ValidationException(f"Invalid month format: {self.month}. Expected YYYY-MM")
        
        # Check HOD permission
        permission_service.check_hod_permission(self.employee_id, self.department_id)
        
        # Calculate metrics
        return metrics_calculator_service.calculate_department_metrics(self.department_id, month_date)


class GetPodMetricsInteractor:
    """Interactor for getting pod-level metrics."""
    
    def __init__(self, pod_id: int, month: str, employee_id: int):
        self.pod_id = pod_id
        self.month = month
        self.employee_id = employee_id
    
    def execute(self) -> PodMetricsDTO:
        """Execute the metrics calculation."""
        # Validate month format
        try:
            month_date = datetime.strptime(self.month, '%Y-%m').date()
            month_date = date(month_date.year, month_date.month, 1)
        except ValueError:
            raise ValidationException(f"Invalid month format: {self.month}. Expected YYYY-MM")
        
        # Check Pod Lead permission
        permission_service.check_pod_lead_permission(self.employee_id, self.pod_id)
        
        # Calculate metrics
        return metrics_calculator_service.calculate_pod_metrics(self.pod_id, month_date)


class GetEmployeeMetricsInteractor:
    """Interactor for getting employee-level metrics."""
    
    def __init__(self, employee_id: int, month: str, requesting_employee_id: int):
        self.employee_id = employee_id
        self.month = month
        self.requesting_employee_id = requesting_employee_id
    
    def execute(self) -> EmployeeMetricsDTO:
        """Execute the metrics calculation."""
        # Validate month format
        try:
            month_date = datetime.strptime(self.month, '%Y-%m').date()
            month_date = date(month_date.year, month_date.month, 1)
        except ValueError:
            raise ValidationException(f"Invalid month format: {self.month}. Expected YYYY-MM")
        
        # Check employee permission
        permission_service.check_employee_permission(self.requesting_employee_id, self.employee_id)
        
        # Calculate metrics
        return metrics_calculator_service.calculate_employee_metrics(self.employee_id, month_date)

