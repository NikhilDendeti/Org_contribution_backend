"""Data Transfer Objects for storage layer."""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import Optional, List, Dict


@dataclass
class DepartmentDTO:
    """Department Data Transfer Object."""
    id: int
    name: str
    created_at: Optional[date] = None
    updated_at: Optional[date] = None


@dataclass
class PodDTO:
    """Pod Data Transfer Object."""
    id: int
    name: str
    department_id: int
    department_name: Optional[str] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None


@dataclass
class ProductDTO:
    """Product Data Transfer Object."""
    id: int
    name: str
    created_at: Optional[date] = None
    updated_at: Optional[date] = None


@dataclass
class FeatureDTO:
    """Feature Data Transfer Object."""
    id: int
    name: str
    product_id: int
    product_name: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None


@dataclass
class EmployeeDTO:
    """Employee Data Transfer Object."""
    id: int
    employee_code: str
    name: str
    email: str
    department_id: Optional[int] = None
    pod_id: Optional[int] = None
    role: str = 'EMPLOYEE'
    department_name: Optional[str] = None
    pod_name: Optional[str] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None


@dataclass
class RawFileDTO:
    """RawFile Data Transfer Object."""
    id: int
    file_name: str
    uploaded_by_id: Optional[int] = None
    uploaded_at: Optional[date] = None
    storage_path: str = ''
    file_size: int = 0
    checksum: Optional[str] = None
    parse_summary: Optional[Dict] = None


@dataclass
class ContributionRecordDTO:
    """ContributionRecord Data Transfer Object."""
    id: Optional[int] = None
    employee_id: Optional[int] = None
    department_id: Optional[int] = None
    pod_id: Optional[int] = None
    product_id: Optional[int] = None
    contribution_month: Optional[date] = None
    effort_hours: Optional[Decimal] = None
    source_file_id: Optional[int] = None
    feature_id: Optional[int] = None
    description: Optional[str] = None
    # Denormalized fields for convenience
    employee_code: Optional[str] = None
    employee_name: Optional[str] = None
    department_name: Optional[str] = None
    pod_name: Optional[str] = None
    product_name: Optional[str] = None
    feature_name: Optional[str] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None


@dataclass
class ProductBreakdownDTO:
    """Product breakdown with hours and percentage."""
    product_id: int
    product_name: str
    hours: Decimal
    percent: Decimal


@dataclass
class DepartmentBreakdownDTO:
    """Department breakdown with product distribution."""
    department_id: int
    department_name: str
    total_hours: Decimal
    products: List[ProductBreakdownDTO]


@dataclass
class OrgMetricsDTO:
    """Organization-level metrics DTO."""
    month: str
    total_hours: Decimal
    products: List[ProductBreakdownDTO]
    top_departments: List[Dict]
    top_pods: List[Dict]
    department_breakdown: List[DepartmentBreakdownDTO]


@dataclass
class PodBreakdownDTO:
    """Pod breakdown with product distribution."""
    pod_id: int
    pod_name: str
    total_hours: Decimal
    products: List[ProductBreakdownDTO]


@dataclass
class DepartmentMetricsDTO:
    """Department-level metrics DTO."""
    department_id: int
    department_name: str
    month: str
    total_hours: Decimal
    pods: List[PodBreakdownDTO]
    product_distribution: List[ProductBreakdownDTO]


@dataclass
class EmployeeBreakdownDTO:
    """Employee breakdown with product distribution."""
    employee_id: int
    employee_code: str
    employee_name: str
    total_hours: Decimal
    products: List[ProductBreakdownDTO]


@dataclass
class PodMetricsDTO:
    """Pod-level metrics DTO."""
    pod_id: int
    pod_name: str
    month: str
    total_hours: Decimal
    products: List[ProductBreakdownDTO]
    employees: List[EmployeeBreakdownDTO]


@dataclass
class FeatureBreakdownDTO:
    """Feature breakdown with hours and percentage."""
    feature_id: Optional[int]
    feature_name: Optional[str]
    hours: Decimal
    percent: Decimal
    description: Optional[str] = None


@dataclass
class EmployeeMetricsDTO:
    """Employee-level metrics DTO."""
    employee_id: int
    employee_code: str
    employee_name: str
    month: str
    total_hours: Decimal
    products: List[ProductBreakdownDTO]
    features: List[FeatureBreakdownDTO]

