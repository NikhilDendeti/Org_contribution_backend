"""Storage layer for ContributionRecord entities."""
from datetime import date
from decimal import Decimal
from django.db.models import Sum, Q
from django.db import transaction
from contributions.models import ContributionRecord
from .storage_dto import ContributionRecordDTO
from ..exceptions import EntityNotFoundException


def create_contribution_record(
    employee_id: int,
    department_id: int,
    pod_id: int,
    product_id: int,
    contribution_month: date,
    effort_hours: Decimal,
    source_file_id: int,
    feature_id: int = None,
    description: str = None
) -> ContributionRecordDTO:
    """Create a single contribution record."""
    record = ContributionRecord.objects.create(
        employee_id=employee_id,
        department_id=department_id,
        pod_id=pod_id,
        product_id=product_id,
        feature_id=feature_id,
        contribution_month=contribution_month,
        effort_hours=effort_hours,
        description=description,
        source_file_id=source_file_id,
    )
    record.refresh_from_db()
    return ContributionRecordDTO(
        id=record.id,
        employee_id=record.employee_id,
        department_id=record.department_id,
        pod_id=record.pod_id,
        product_id=record.product_id,
        feature_id=record.feature_id,
        contribution_month=record.contribution_month,
        effort_hours=record.effort_hours,
        description=record.description,
        source_file_id=record.source_file_id,
    )


def bulk_create_contributions(records: list[ContributionRecordDTO], source_file_id: int) -> int:
    """Bulk create contribution records."""
    contribution_records = []
    for record_dto in records:
        contribution_records.append(
            ContributionRecord(
                employee_id=record_dto.employee_id,
                department_id=record_dto.department_id,
                pod_id=record_dto.pod_id,
                product_id=record_dto.product_id,
                feature_id=record_dto.feature_id,
                contribution_month=record_dto.contribution_month,
                effort_hours=record_dto.effort_hours,
                description=record_dto.description,
                source_file_id=source_file_id,
            )
        )
    
    with transaction.atomic():
        created = ContributionRecord.objects.bulk_create(contribution_records, batch_size=1000)
    return len(created)


def get_contributions_by_month(month: date) -> list[ContributionRecordDTO]:
    """Get contributions by month."""
    contributions = ContributionRecord.objects.filter(
        contribution_month=month
    ).select_related(
        'employee', 'department', 'pod', 'product', 'feature'
    ).order_by('employee', 'product')
    
    return [
        ContributionRecordDTO(
            id=contrib.id,
            employee_id=contrib.employee_id,
            department_id=contrib.department_id,
            pod_id=contrib.pod_id,
            product_id=contrib.product_id,
            feature_id=contrib.feature_id,
            contribution_month=contrib.contribution_month,
            effort_hours=contrib.effort_hours,
            description=contrib.description,
            source_file_id=contrib.source_file_id,
            employee_code=contrib.employee.employee_code,
            employee_name=contrib.employee.name,
            department_name=contrib.department.name,
            pod_name=contrib.pod.name,
            product_name=contrib.product.name,
            feature_name=contrib.feature.name if contrib.feature else None,
            created_at=contrib.created_at,
            updated_at=contrib.updated_at,
        )
        for contrib in contributions
    ]


def get_contributions_by_employee(employee_id: int, month: date) -> list[ContributionRecordDTO]:
    """Get contributions by employee and month."""
    contributions = ContributionRecord.objects.filter(
        employee_id=employee_id,
        contribution_month=month
    ).select_related(
        'employee', 'department', 'pod', 'product', 'feature'
    ).order_by('product', 'feature')
    
    return [
        ContributionRecordDTO(
            id=contrib.id,
            employee_id=contrib.employee_id,
            department_id=contrib.department_id,
            pod_id=contrib.pod_id,
            product_id=contrib.product_id,
            feature_id=contrib.feature_id,
            contribution_month=contrib.contribution_month,
            effort_hours=contrib.effort_hours,
            description=contrib.description,
            source_file_id=contrib.source_file_id,
            employee_code=contrib.employee.employee_code,
            employee_name=contrib.employee.name,
            department_name=contrib.department.name,
            pod_name=contrib.pod.name,
            product_name=contrib.product.name,
            feature_name=contrib.feature.name if contrib.feature else None,
            created_at=contrib.created_at,
            updated_at=contrib.updated_at,
        )
        for contrib in contributions
    ]


def get_contributions_by_pod(pod_id: int, month: date) -> list[ContributionRecordDTO]:
    """Get contributions by pod and month."""
    contributions = ContributionRecord.objects.filter(
        pod_id=pod_id,
        contribution_month=month
    ).select_related(
        'employee', 'department', 'pod', 'product', 'feature'
    ).order_by('employee', 'product')
    
    return [
        ContributionRecordDTO(
            id=contrib.id,
            employee_id=contrib.employee_id,
            department_id=contrib.department_id,
            pod_id=contrib.pod_id,
            product_id=contrib.product_id,
            feature_id=contrib.feature_id,
            contribution_month=contrib.contribution_month,
            effort_hours=contrib.effort_hours,
            description=contrib.description,
            source_file_id=contrib.source_file_id,
            employee_code=contrib.employee.employee_code,
            employee_name=contrib.employee.name,
            department_name=contrib.department.name,
            pod_name=contrib.pod.name,
            product_name=contrib.product.name,
            feature_name=contrib.feature.name if contrib.feature else None,
            created_at=contrib.created_at,
            updated_at=contrib.updated_at,
        )
        for contrib in contributions
    ]


def get_contributions_by_department(department_id: int, month: date) -> list[ContributionRecordDTO]:
    """Get contributions by department and month."""
    contributions = ContributionRecord.objects.filter(
        department_id=department_id,
        contribution_month=month
    ).select_related(
        'employee', 'department', 'pod', 'product', 'feature'
    ).order_by('pod', 'employee', 'product')
    
    return [
        ContributionRecordDTO(
            id=contrib.id,
            employee_id=contrib.employee_id,
            department_id=contrib.department_id,
            pod_id=contrib.pod_id,
            product_id=contrib.product_id,
            feature_id=contrib.feature_id,
            contribution_month=contrib.contribution_month,
            effort_hours=contrib.effort_hours,
            description=contrib.description,
            source_file_id=contrib.source_file_id,
            employee_code=contrib.employee.employee_code,
            employee_name=contrib.employee.name,
            department_name=contrib.department.name,
            pod_name=contrib.pod.name,
            product_name=contrib.product.name,
            feature_name=contrib.feature.name if contrib.feature else None,
            created_at=contrib.created_at,
            updated_at=contrib.updated_at,
        )
        for contrib in contributions
    ]


def get_contributions_by_product(product_id: int, month: date) -> list[ContributionRecordDTO]:
    """Get contributions by product and month."""
    contributions = ContributionRecord.objects.filter(
        product_id=product_id,
        contribution_month=month
    ).select_related(
        'employee', 'department', 'pod', 'product', 'feature'
    ).order_by('department', 'pod', 'employee')
    
    return [
        ContributionRecordDTO(
            id=contrib.id,
            employee_id=contrib.employee_id,
            department_id=contrib.department_id,
            pod_id=contrib.pod_id,
            product_id=contrib.product_id,
            feature_id=contrib.feature_id,
            contribution_month=contrib.contribution_month,
            effort_hours=contrib.effort_hours,
            description=contrib.description,
            source_file_id=contrib.source_file_id,
            employee_code=contrib.employee.employee_code,
            employee_name=contrib.employee.name,
            department_name=contrib.department.name,
            pod_name=contrib.pod.name,
            product_name=contrib.product.name,
            feature_name=contrib.feature.name if contrib.feature else None,
            created_at=contrib.created_at,
            updated_at=contrib.updated_at,
        )
        for contrib in contributions
    ]


def get_total_hours_by_month(month: date) -> Decimal:
    """Get total hours for a month across all contributions."""
    result = ContributionRecord.objects.filter(
        contribution_month=month
    ).aggregate(total=Sum('effort_hours'))
    return result['total'] or Decimal('0')


def get_total_hours_by_product(product_id: int, month: date) -> Decimal:
    """Get total hours for a product in a month."""
    result = ContributionRecord.objects.filter(
        product_id=product_id,
        contribution_month=month
    ).aggregate(total=Sum('effort_hours'))
    return result['total'] or Decimal('0')


def get_total_hours_by_department(department_id: int, month: date) -> Decimal:
    """Get total hours for a department in a month."""
    result = ContributionRecord.objects.filter(
        department_id=department_id,
        contribution_month=month
    ).aggregate(total=Sum('effort_hours'))
    return result['total'] or Decimal('0')


def get_total_hours_by_pod(pod_id: int, month: date) -> Decimal:
    """Get total hours for a pod in a month."""
    result = ContributionRecord.objects.filter(
        pod_id=pod_id,
        contribution_month=month
    ).aggregate(total=Sum('effort_hours'))
    return result['total'] or Decimal('0')


def get_total_hours_by_employee(employee_id: int, month: date) -> Decimal:
    """Get total hours for an employee in a month."""
    result = ContributionRecord.objects.filter(
        employee_id=employee_id,
        contribution_month=month
    ).aggregate(total=Sum('effort_hours'))
    return result['total'] or Decimal('0')

