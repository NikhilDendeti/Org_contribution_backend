"""Storage layer for Pod entities."""
from core.models import Pod
from .storage_dto import PodDTO
from ..exceptions import EntityNotFoundException


def get_pod_by_id(pod_id: int) -> PodDTO:
    """Get pod by ID."""
    try:
        pod = Pod.objects.select_related('department').get(id=pod_id)
        return PodDTO(
            id=pod.id,
            name=pod.name,
            department_id=pod.department_id,
            department_name=pod.department.name,
            created_at=pod.created_at,
            updated_at=pod.updated_at,
        )
    except Pod.DoesNotExist:
        raise EntityNotFoundException(f"Pod with id {pod_id} not found")


def get_or_create_pod(name: str, department_id: int) -> PodDTO:
    """Get or create a pod."""
    pod, _ = Pod.objects.get_or_create(
        name=name,
        department_id=department_id,
        defaults={'department_id': department_id}
    )
    pod.refresh_from_db()
    pod.department.refresh_from_db()
    return PodDTO(
        id=pod.id,
        name=pod.name,
        department_id=pod.department_id,
        department_name=pod.department.name,
        created_at=pod.created_at,
        updated_at=pod.updated_at,
    )


def list_pods_by_department(department_id: int) -> list[PodDTO]:
    """List pods by department."""
    pods = Pod.objects.filter(department_id=department_id).select_related('department').order_by('name')
    return [
        PodDTO(
            id=pod.id,
            name=pod.name,
            department_id=pod.department_id,
            department_name=pod.department.name,
            created_at=pod.created_at,
            updated_at=pod.updated_at,
        )
        for pod in pods
    ]

