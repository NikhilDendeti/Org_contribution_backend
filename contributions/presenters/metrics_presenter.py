"""Presenter for metrics responses."""
from contributions.storages.storage_dto import (
    OrgMetricsDTO, DepartmentMetricsDTO, PodMetricsDTO, EmployeeMetricsDTO
)


def present_org_metrics(metrics: OrgMetricsDTO) -> dict:
    """Present organization metrics."""
    return {
        'month': metrics.month,
        'total_hours': float(metrics.total_hours),
        'products': [
            {
                'product_id': p.product_id,
                'product_name': p.product_name,
                'hours': float(p.hours),
                'percent': float(p.percent),
            }
            for p in metrics.products
        ],
        'top_departments': metrics.top_departments,
        'top_pods': metrics.top_pods,
    }


def present_department_metrics(metrics: DepartmentMetricsDTO) -> dict:
    """Present department metrics."""
    return {
        'department_id': metrics.department_id,
        'department_name': metrics.department_name,
        'month': metrics.month,
        'total_hours': float(metrics.total_hours),
        'pods': [
            {
                'pod_id': p.pod_id,
                'pod_name': p.pod_name,
                'total_hours': float(p.total_hours),
                'products': [
                    {
                        'product_id': prod.product_id,
                        'product_name': prod.product_name,
                        'hours': float(prod.hours),
                        'percent': float(prod.percent),
                    }
                    for prod in p.products
                ],
            }
            for p in metrics.pods
        ],
        'product_distribution': [
            {
                'product_id': p.product_id,
                'product_name': p.product_name,
                'hours': float(p.hours),
                'percent': float(p.percent),
            }
            for p in metrics.product_distribution
        ],
    }


def present_pod_metrics(metrics: PodMetricsDTO) -> dict:
    """Present pod metrics."""
    return {
        'pod_id': metrics.pod_id,
        'pod_name': metrics.pod_name,
        'month': metrics.month,
        'total_hours': float(metrics.total_hours),
        'products': [
            {
                'product_id': p.product_id,
                'product_name': p.product_name,
                'hours': float(p.hours),
                'percent': float(p.percent),
            }
            for p in metrics.products
        ],
        'employees': [
            {
                'employee_id': e.employee_id,
                'employee_code': e.employee_code,
                'employee_name': e.employee_name,
                'total_hours': float(e.total_hours),
                'products': [
                    {
                        'product_id': p.product_id,
                        'product_name': p.product_name,
                        'hours': float(p.hours),
                        'percent': float(p.percent),
                    }
                    for p in e.products
                ],
            }
            for e in metrics.employees
        ],
    }


def present_employee_metrics(metrics: EmployeeMetricsDTO) -> dict:
    """Present employee metrics."""
    return {
        'employee_id': metrics.employee_id,
        'employee_code': metrics.employee_code,
        'employee_name': metrics.employee_name,
        'month': metrics.month,
        'total_hours': float(metrics.total_hours),
        'products': [
            {
                'product_id': p.product_id,
                'product_name': p.product_name,
                'hours': float(p.hours),
                'percent': float(p.percent),
            }
            for p in metrics.products
        ],
        'features': [
            {
                'feature_id': f.feature_id,
                'feature_name': f.feature_name,
                'hours': float(f.hours),
                'percent': float(f.percent),
                'description': f.description,
            }
            for f in metrics.features
        ],
    }

