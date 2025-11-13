"""Permission service for role-based access control."""
from contributions.storages import employee_storage
from contributions.exceptions import PermissionDeniedException, EntityNotFoundException


def check_ceo_permission(employee_id: int) -> bool:
    """Check if employee has CEO role."""
    try:
        employee = employee_storage.get_employee_by_id(employee_id)
        if employee.role != 'CEO':
            raise PermissionDeniedException("CEO access required")
        return True
    except EntityNotFoundException:
        raise EntityNotFoundException(f"Employee with id {employee_id} not found")


def check_hod_permission(employee_id: int, department_id: int = None) -> bool:
    """Check if employee has HOD role and optionally department access."""
    try:
        employee = employee_storage.get_employee_by_id(employee_id)
        if employee.role != 'HOD':
            raise PermissionDeniedException("HOD access required")
        if department_id and employee.department_id != department_id:
            raise PermissionDeniedException("Access denied to this department")
        return True
    except EntityNotFoundException:
        raise EntityNotFoundException(f"Employee with id {employee_id} not found")


def check_pod_lead_permission(employee_id: int, pod_id: int = None) -> bool:
    """Check if employee has Pod Lead role and optionally pod access."""
    try:
        employee = employee_storage.get_employee_by_id(employee_id)
        if employee.role not in ['POD_LEAD', 'HOD', 'CEO', 'ADMIN']:
            raise PermissionDeniedException("Pod Lead access required")
        if pod_id and employee.pod_id != pod_id and employee.role not in ['HOD', 'CEO', 'ADMIN']:
            raise PermissionDeniedException("Access denied to this pod")
        return True
    except EntityNotFoundException:
        raise EntityNotFoundException(f"Employee with id {employee_id} not found")


def check_employee_permission(employee_id: int, target_employee_id: int) -> bool:
    """Check if employee can access target employee's data."""
    try:
        employee = employee_storage.get_employee_by_id(employee_id)
        # Employees can access their own data
        if employee_id == target_employee_id:
            return True
        # HOD, CEO, ADMIN can access any employee's data
        if employee.role in ['HOD', 'CEO', 'ADMIN']:
            return True
        # Pod Leads can access their pod members' data
        if employee.role == 'POD_LEAD':
            target_employee = employee_storage.get_employee_by_id(target_employee_id)
            if target_employee.pod_id == employee.pod_id:
                return True
        raise PermissionDeniedException("Access denied to this employee's data")
    except EntityNotFoundException:
        raise EntityNotFoundException(f"Employee not found")


def check_admin_permission(employee_id: int) -> bool:
    """Check if employee has Admin role."""
    try:
        employee = employee_storage.get_employee_by_id(employee_id)
        if employee.role != 'ADMIN':
            raise PermissionDeniedException("Admin access required")
        return True
    except EntityNotFoundException:
        raise EntityNotFoundException(f"Employee with id {employee_id} not found")


def can_upload_file(employee_id: int) -> bool:
    """Check if employee can upload files (HOD or Admin)."""
    try:
        employee = employee_storage.get_employee_by_id(employee_id)
        if employee.role in ['HOD', 'ADMIN', 'CEO']:
            return True
        raise PermissionDeniedException("File upload requires HOD, Admin, or CEO role")
    except EntityNotFoundException:
        raise EntityNotFoundException(f"Employee with id {employee_id} not found")

