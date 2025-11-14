"""Storage layer for Pod Lead Allocation operations."""
from datetime import date
from decimal import Decimal
from typing import List, Optional
from django.db import transaction
from contributions.models import PodLeadAllocation
from contributions.storages.storage_dto import PodLeadAllocationDTO
from contributions.exceptions import EntityNotFoundException


def create_allocation(
    employee_id: int,
    pod_lead_id: int,
    contribution_month: date,
    product: Optional[str] = None,
    product_description: Optional[str] = None,
    academy_percent: Decimal = Decimal('0.00'),
    intensive_percent: Decimal = Decimal('0.00'),
    niat_percent: Decimal = Decimal('0.00'),
    features_text: Optional[str] = None,
    is_verified_description: bool = False,
    baseline_hours: Decimal = Decimal('160.00'),
    status: str = 'PENDING'
) -> PodLeadAllocationDTO:
    """Create a new Pod Lead allocation record."""
    allocation = PodLeadAllocation.objects.create(
        employee_id=employee_id,
        pod_lead_id=pod_lead_id,
        contribution_month=contribution_month,
        product=product,
        product_description=product_description,
        academy_percent=academy_percent,
        intensive_percent=intensive_percent,
        niat_percent=niat_percent,
        features_text=features_text,
        is_verified_description=is_verified_description,
        baseline_hours=baseline_hours,
        status=status,
    )
    return convert_to_dto(allocation)


def update_allocation(
    allocation_id: int,
    academy_percent: Optional[Decimal] = None,
    intensive_percent: Optional[Decimal] = None,
    niat_percent: Optional[Decimal] = None,
    features_text: Optional[str] = None,
    is_verified_description: Optional[bool] = None,
    status: Optional[str] = None
) -> PodLeadAllocationDTO:
    """Update an existing allocation."""
    allocation = PodLeadAllocation.objects.get(id=allocation_id)
    
    if academy_percent is not None:
        allocation.academy_percent = academy_percent
    if intensive_percent is not None:
        allocation.intensive_percent = intensive_percent
    if niat_percent is not None:
        allocation.niat_percent = niat_percent
    if features_text is not None:
        allocation.features_text = features_text
    if is_verified_description is not None:
        allocation.is_verified_description = is_verified_description
    if status is not None:
        allocation.status = status
    
    allocation.save()
    return convert_to_dto(allocation)


def get_allocation_by_id(allocation_id: int) -> PodLeadAllocationDTO:
    """Get allocation by ID."""
    try:
        allocation = PodLeadAllocation.objects.select_related('employee', 'pod_lead').get(id=allocation_id)
        return convert_to_dto(allocation)
    except PodLeadAllocation.DoesNotExist:
        raise EntityNotFoundException(f"Allocation with id {allocation_id} not found")


def get_allocations_by_pod_lead(pod_lead_id: int, month: date) -> List[PodLeadAllocationDTO]:
    """Get all allocations for a Pod Lead for a specific month."""
    allocations = PodLeadAllocation.objects.filter(
        pod_lead_id=pod_lead_id,
        contribution_month=month
    ).select_related('employee', 'pod_lead').order_by('employee__name')
    
    return [convert_to_dto(alloc) for alloc in allocations]


def get_allocations_by_employee_and_month(employee_id: int, month: date) -> List[PodLeadAllocationDTO]:
    """Get all allocations for an employee and month."""
    allocations = PodLeadAllocation.objects.filter(
        employee_id=employee_id,
        contribution_month=month
    ).select_related('employee', 'pod_lead').order_by('product')
    
    return [convert_to_dto(alloc) for alloc in allocations]


def get_allocation_by_employee_product_month(
    employee_id: int,
    product: str,
    month: date
) -> Optional[PodLeadAllocationDTO]:
    """Get allocation for specific employee-product-month combination."""
    try:
        allocation = PodLeadAllocation.objects.select_related('employee', 'pod_lead').get(
            employee_id=employee_id,
            product=product,
            contribution_month=month
        )
        return convert_to_dto(allocation)
    except PodLeadAllocation.DoesNotExist:
        return None


def get_processed_allocations_by_month(month: date) -> List[PodLeadAllocationDTO]:
    """Get all processed allocations for a month."""
    allocations = PodLeadAllocation.objects.filter(
        contribution_month=month,
        status='PROCESSED'
    ).select_related('employee', 'pod_lead').order_by('employee__name', 'product')
    
    return [convert_to_dto(alloc) for alloc in allocations]


def get_pending_allocations_by_pod(pod_id: int, month: date) -> List[PodLeadAllocationDTO]:
    """Get pending allocations for a pod."""
    allocations = PodLeadAllocation.objects.filter(
        employee__pod_id=pod_id,
        contribution_month=month,
        status='PENDING'
    ).select_related('employee', 'pod_lead').order_by('employee__name')
    
    return [convert_to_dto(alloc) for alloc in allocations]


def get_submitted_allocations_by_pod(pod_id: int, month: date) -> List[PodLeadAllocationDTO]:
    """Get submitted allocations for a pod."""
    allocations = PodLeadAllocation.objects.filter(
        employee__pod_id=pod_id,
        contribution_month=month,
        status='SUBMITTED'
    ).select_related('employee', 'pod_lead').order_by('employee__name')
    
    return [convert_to_dto(alloc) for alloc in allocations]


def mark_allocation_submitted(allocation_id: int) -> PodLeadAllocationDTO:
    """Mark allocation as submitted."""
    allocation = PodLeadAllocation.objects.get(id=allocation_id)
    allocation.status = 'SUBMITTED'
    allocation.save()
    return convert_to_dto(allocation)


def mark_allocation_processed(allocation_id: int) -> PodLeadAllocationDTO:
    """Mark allocation as processed."""
    allocation = PodLeadAllocation.objects.get(id=allocation_id)
    allocation.status = 'PROCESSED'
    allocation.save()
    return convert_to_dto(allocation)


def convert_to_dto(allocation: PodLeadAllocation) -> PodLeadAllocationDTO:
    """Convert ORM object to DTO."""
    return PodLeadAllocationDTO(
        id=allocation.id,
        employee_id=allocation.employee_id,
        pod_lead_id=allocation.pod_lead_id,
        contribution_month=allocation.contribution_month,
        product=allocation.product,
        product_description=allocation.product_description,
        academy_percent=allocation.academy_percent,
        intensive_percent=allocation.intensive_percent,
        niat_percent=allocation.niat_percent,
        features_text=allocation.features_text,
        is_verified_description=allocation.is_verified_description,
        baseline_hours=allocation.baseline_hours,
        status=allocation.status,
        employee_code=allocation.employee.employee_code if allocation.employee else None,
        employee_name=allocation.employee.name if allocation.employee else None,
        pod_lead_code=allocation.pod_lead.employee_code if allocation.pod_lead else None,
        pod_lead_name=allocation.pod_lead.name if allocation.pod_lead else None,
        created_at=allocation.created_at.date() if allocation.created_at else None,
        updated_at=allocation.updated_at.date() if allocation.updated_at else None,
    )

