"""Storage layer for Department entities."""
from core.models import Department
from .storage_dto import DepartmentDTO
from ..exceptions import EntityNotFoundException


def get_department_by_id(department_id: int) -> DepartmentDTO:
    """Get department by ID."""
    try:
        dept = Department.objects.get(id=department_id)
        return DepartmentDTO(
            id=dept.id,
            name=dept.name,
            created_at=dept.created_at,
            updated_at=dept.updated_at,
        )
    except Department.DoesNotExist:
        raise EntityNotFoundException(f"Department with id {department_id} not found")


def get_or_create_department(name: str) -> DepartmentDTO:
    """Get or create a department."""
    dept, _ = Department.objects.get_or_create(name=name)
    return DepartmentDTO(
        id=dept.id,
        name=dept.name,
        created_at=dept.created_at,
        updated_at=dept.updated_at,
    )


def list_departments() -> list[DepartmentDTO]:
    """List all departments."""
    departments = Department.objects.all().order_by('name')
    return [
        DepartmentDTO(
            id=dept.id,
            name=dept.name,
            created_at=dept.created_at,
            updated_at=dept.updated_at,
        )
        for dept in departments
    ]

