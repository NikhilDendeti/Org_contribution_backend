"""Storage layer for Employee entities."""
from core.models import Employee
from .storage_dto import EmployeeDTO
from ..exceptions import EntityNotFoundException


def get_employee_by_code(employee_code: str) -> EmployeeDTO:
    """Get employee by employee code."""
    try:
        employee = Employee.objects.select_related('department', 'pod').get(employee_code=employee_code)
        return EmployeeDTO(
            id=employee.id,
            employee_code=employee.employee_code,
            name=employee.name,
            email=employee.email,
            department_id=employee.department_id,
            pod_id=employee.pod_id,
            role=employee.role,
            department_name=employee.department.name if employee.department else None,
            pod_name=employee.pod.name if employee.pod else None,
            created_at=employee.created_at,
            updated_at=employee.updated_at,
        )
    except Employee.DoesNotExist:
        raise EntityNotFoundException(f"Employee with code {employee_code} not found")


def get_employee_by_id(employee_id: int) -> EmployeeDTO:
    """Get employee by ID."""
    try:
        employee = Employee.objects.select_related('department', 'pod').get(id=employee_id)
        return EmployeeDTO(
            id=employee.id,
            employee_code=employee.employee_code,
            name=employee.name,
            email=employee.email,
            department_id=employee.department_id,
            pod_id=employee.pod_id,
            role=employee.role,
            department_name=employee.department.name if employee.department else None,
            pod_name=employee.pod.name if employee.pod else None,
            created_at=employee.created_at,
            updated_at=employee.updated_at,
        )
    except Employee.DoesNotExist:
        raise EntityNotFoundException(f"Employee with id {employee_id} not found")


def get_or_create_employee(
    employee_code: str,
    name: str,
    email: str,
    department_id: int = None,
    pod_id: int = None,
    pod_head_id: int = None,
    role: str = 'EMPLOYEE'
) -> EmployeeDTO:
    """Get or create an employee."""
    employee, created = Employee.objects.get_or_create(
        employee_code=employee_code,
        defaults={
            'name': name,
            'email': email,
            'department_id': department_id,
            'pod_id': pod_id,
            'pod_head_id': pod_head_id,
            'role': role,
        }
    )
    if not created:
        # Update fields if employee exists
        employee.name = name
        employee.email = email
        if department_id:
            employee.department_id = department_id
        if pod_id:
            employee.pod_id = pod_id
        if pod_head_id is not None:
            employee.pod_head_id = pod_head_id
        employee.role = role
        employee.save()
    
    employee.refresh_from_db()
    if employee.department:
        employee.department.refresh_from_db()
    if employee.pod:
        employee.pod.refresh_from_db()
    
    return EmployeeDTO(
        id=employee.id,
        employee_code=employee.employee_code,
        name=employee.name,
        email=employee.email,
        department_id=employee.department_id,
        pod_id=employee.pod_id,
        role=employee.role,
        department_name=employee.department.name if employee.department else None,
        pod_name=employee.pod.name if employee.pod else None,
        created_at=employee.created_at,
        updated_at=employee.updated_at,
    )


def list_employees_by_pod(pod_id: int) -> list[EmployeeDTO]:
    """List employees by pod."""
    employees = Employee.objects.filter(pod_id=pod_id).select_related('department', 'pod').order_by('name')
    return [
        EmployeeDTO(
            id=emp.id,
            employee_code=emp.employee_code,
            name=emp.name,
            email=emp.email,
            department_id=emp.department_id,
            pod_id=emp.pod_id,
            role=emp.role,
            department_name=emp.department.name if emp.department else None,
            pod_name=emp.pod.name if emp.pod else None,
            created_at=emp.created_at,
            updated_at=emp.updated_at,
        )
        for emp in employees
    ]

