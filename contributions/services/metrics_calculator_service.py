"""Metrics calculation service with robust percentage calculations."""
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict
from django.db.models import Sum
from contributions.models import ContributionRecord
from contributions.storages.storage_dto import (
    OrgMetricsDTO, DepartmentMetricsDTO, PodMetricsDTO, EmployeeMetricsDTO,
    ProductBreakdownDTO, PodBreakdownDTO, EmployeeBreakdownDTO, FeatureBreakdownDTO,
    DepartmentBreakdownDTO
)
from contributions.storages import contribution_storage


def calculate_percentages(items: List[Dict], total_hours: Decimal) -> List[Dict]:
    """
    Calculate percentages for a list of items with hours.
    
    Args:
        items: List of dicts with 'hours' key (Decimal)
        total_hours: Total hours (Decimal)
    
    Returns:
        List of dicts with 'percent' field added (Decimal, 2 decimal places)
    """
    if total_hours == 0:
        return [{**item, 'percent': Decimal('0.00')} for item in items]
    
    result = []
    for item in items:
        hours = item.get('hours', Decimal('0'))
        if hours == 0:
            percent = Decimal('0.00')
        else:
            percent = (hours / total_hours) * Decimal('100')
            percent = percent.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        result.append({**item, 'percent': percent})
    
    # Ensure percentages sum to 100%
    total_percent = sum(item['percent'] for item in result)
    if total_percent != Decimal('100.00'):
        # Adjust last item to make sum exactly 100%
        diff = Decimal('100.00') - total_percent
        if result:
            result[-1]['percent'] += diff
            result[-1]['percent'] = result[-1]['percent'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return result


def calculate_org_metrics(month: date) -> OrgMetricsDTO:
    """Calculate organization-level metrics."""
    # Get total org hours
    total_hours = contribution_storage.get_total_hours_by_month(month)
    
    # Group by product
    product_aggregates = ContributionRecord.objects.filter(
        contribution_month=month
    ).values('product_id', 'product__name').annotate(
        hours=Sum('effort_hours')
    ).order_by('-hours')
    
    products = []
    for agg in product_aggregates:
        products.append({
            'product_id': agg['product_id'],
            'product_name': agg['product__name'],
            'hours': agg['hours'] or Decimal('0'),
        })
    
    # Calculate percentages
    products_with_percent = calculate_percentages(products, total_hours)
    
    product_breakdowns = [
        ProductBreakdownDTO(
            product_id=item['product_id'],
            product_name=item['product_name'],
            hours=item['hours'],
            percent=item['percent'],
        )
        for item in products_with_percent
    ]
    
    # Get top departments
    dept_aggregates = ContributionRecord.objects.filter(
        contribution_month=month
    ).values('department_id', 'department__name').annotate(
        hours=Sum('effort_hours')
    ).order_by('-hours')[:10]
    
    top_departments = [
        {
            'department_id': agg['department_id'],
            'department_name': agg['department__name'],
            'hours': float(agg['hours'] or 0),
        }
        for agg in dept_aggregates
    ]
    
    # Get top pods with department information and percentage
    pod_aggregates = ContributionRecord.objects.filter(
        contribution_month=month
    ).values('pod_id', 'pod__name', 'department_id', 'department__name').annotate(
        hours=Sum('effort_hours')
    ).order_by('-hours')[:10]
    
    top_pods = [
        {
            'pod_id': agg['pod_id'],
            'pod_name': agg['pod__name'],
            'department_id': agg['department_id'],
            'department_name': agg['department__name'],
            'hours': float(agg['hours'] or 0),
            'percent': float((Decimal(str(agg['hours'] or 0)) / total_hours * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
        }
        for agg in pod_aggregates
    ]
    
    # Calculate department breakdown with product distribution
    # Get all departments with their product breakdowns
    dept_product_aggregates = ContributionRecord.objects.filter(
        contribution_month=month
    ).values('department_id', 'department__name', 'product_id', 'product__name').annotate(
        hours=Sum('effort_hours')
    ).order_by('department_id', 'product_id')
    
    # Group by department
    department_breakdowns = []
    current_dept_id = None
    current_dept_name = None
    current_dept_products = []
    current_dept_total = Decimal('0')
    
    for agg in dept_product_aggregates:
        dept_id = agg['department_id']
        dept_name = agg['department__name']
        product_id = agg['product_id']
        product_name = agg['product__name']
        hours = Decimal(str(agg['hours'] or 0))
        
        if current_dept_id is None or current_dept_id != dept_id:
            # Save previous department if exists
            if current_dept_id is not None:
                # Calculate percentages for this department's products
                dept_products_with_percent = calculate_percentages(
                    current_dept_products, current_dept_total
                )
                department_breakdowns.append(
                    DepartmentBreakdownDTO(
                        department_id=current_dept_id,
                        department_name=current_dept_name,
                        total_hours=current_dept_total,
                        products=[
                            ProductBreakdownDTO(
                                product_id=item['product_id'],
                                product_name=item['product_name'],
                                hours=item['hours'],
                                percent=item['percent'],
                            )
                            for item in dept_products_with_percent
                        ],
                    )
                )
            
            # Start new department
            current_dept_id = dept_id
            current_dept_name = dept_name
            current_dept_products = []
            current_dept_total = Decimal('0')
        
        current_dept_products.append({
            'product_id': product_id,
            'product_name': product_name,
            'hours': hours,
        })
        current_dept_total += hours
    
    # Don't forget the last department
    if current_dept_id is not None:
        dept_products_with_percent = calculate_percentages(
            current_dept_products, current_dept_total
        )
        department_breakdowns.append(
            DepartmentBreakdownDTO(
                department_id=current_dept_id,
                department_name=current_dept_name,
                total_hours=current_dept_total,
                products=[
                    ProductBreakdownDTO(
                        product_id=item['product_id'],
                        product_name=item['product_name'],
                        hours=item['hours'],
                        percent=item['percent'],
                    )
                    for item in dept_products_with_percent
                ],
            )
        )
    
    return OrgMetricsDTO(
        month=month.strftime('%Y-%m'),
        total_hours=total_hours,
        products=product_breakdowns,
        top_departments=top_departments,
        top_pods=top_pods,
        department_breakdown=department_breakdowns,
    )


def calculate_product_metrics(product_id: int, month: date) -> Dict:
    """Calculate product-level metrics."""
    total_hours = contribution_storage.get_total_hours_by_product(product_id, month)
    
    # Group by department
    dept_aggregates = ContributionRecord.objects.filter(
        product_id=product_id,
        contribution_month=month
    ).values('department_id', 'department__name').annotate(
        hours=Sum('effort_hours')
    ).order_by('-hours')
    
    departments = []
    for agg in dept_aggregates:
        departments.append({
            'department_id': agg['department_id'],
            'department_name': agg['department__name'],
            'hours': agg['hours'] or Decimal('0'),
        })
    
    departments_with_percent = calculate_percentages(departments, total_hours)
    
    # Group by pod
    pod_aggregates = ContributionRecord.objects.filter(
        product_id=product_id,
        contribution_month=month
    ).values('pod_id', 'pod__name').annotate(
        hours=Sum('effort_hours')
    ).order_by('-hours')
    
    pods = []
    for agg in pod_aggregates:
        pods.append({
            'pod_id': agg['pod_id'],
            'pod_name': agg['pod__name'],
            'hours': agg['hours'] or Decimal('0'),
        })
    
    pods_with_percent = calculate_percentages(pods, total_hours)
    
    return {
        'product_id': product_id,
        'month': month.strftime('%Y-%m'),
        'total_hours': total_hours,
        'departments': [
            {
                'department_id': item['department_id'],
                'department_name': item['department_name'],
                'hours': item['hours'],
                'percent': item['percent'],
            }
            for item in departments_with_percent
        ],
        'pods': [
            {
                'pod_id': item['pod_id'],
                'pod_name': item['pod_name'],
                'hours': item['hours'],
                'percent': item['percent'],
            }
            for item in pods_with_percent
        ],
    }


def calculate_department_metrics(department_id: int, month: date) -> DepartmentMetricsDTO:
    """Calculate department-level metrics."""
    total_hours = contribution_storage.get_total_hours_by_department(department_id, month)
    
    # Get pod breakdowns with product distribution
    pod_aggregates = ContributionRecord.objects.filter(
        department_id=department_id,
        contribution_month=month
    ).values('pod_id', 'pod__name').distinct()
    
    pods = []
    for pod_agg in pod_aggregates:
        pod_id = pod_agg['pod_id']
        pod_name = pod_agg['pod__name']
        
        # Get product breakdown for this pod
        product_aggregates = ContributionRecord.objects.filter(
            department_id=department_id,
            pod_id=pod_id,
            contribution_month=month
        ).values('product_id', 'product__name').annotate(
            hours=Sum('effort_hours')
        ).order_by('-hours')
        
        pod_total_hours = contribution_storage.get_total_hours_by_pod(pod_id, month)
        
        products = []
        for prod_agg in product_aggregates:
            products.append({
                'product_id': prod_agg['product_id'],
                'product_name': prod_agg['product__name'],
                'hours': prod_agg['hours'] or Decimal('0'),
            })
        
        products_with_percent = calculate_percentages(products, pod_total_hours)
        
        pods.append(PodBreakdownDTO(
            pod_id=pod_id,
            pod_name=pod_name,
            total_hours=pod_total_hours,
            products=[
                ProductBreakdownDTO(
                    product_id=item['product_id'],
                    product_name=item['product_name'],
                    hours=item['hours'],
                    percent=item['percent'],
                )
                for item in products_with_percent
            ],
        ))
    
    # Get product distribution for department
    product_aggregates = ContributionRecord.objects.filter(
        department_id=department_id,
        contribution_month=month
    ).values('product_id', 'product__name').annotate(
        hours=Sum('effort_hours')
    ).order_by('-hours')
    
    products = []
    for agg in product_aggregates:
        products.append({
            'product_id': agg['product_id'],
            'product_name': agg['product__name'],
            'hours': agg['hours'] or Decimal('0'),
        })
    
    products_with_percent = calculate_percentages(products, total_hours)
    
    # Get department name
    from contributions.storages import department_storage
    dept = department_storage.get_department_by_id(department_id)
    
    return DepartmentMetricsDTO(
        department_id=department_id,
        department_name=dept.name,
        month=month.strftime('%Y-%m'),
        total_hours=total_hours,
        pods=pods,
        product_distribution=[
            ProductBreakdownDTO(
                product_id=item['product_id'],
                product_name=item['product_name'],
                hours=item['hours'],
                percent=item['percent'],
            )
            for item in products_with_percent
        ],
    )


def calculate_pod_metrics(pod_id: int, month: date) -> PodMetricsDTO:
    """Calculate pod-level metrics."""
    total_hours = contribution_storage.get_total_hours_by_pod(pod_id, month)
    
    # Group by product
    product_aggregates = ContributionRecord.objects.filter(
        pod_id=pod_id,
        contribution_month=month
    ).values('product_id', 'product__name').annotate(
        hours=Sum('effort_hours')
    ).order_by('-hours')
    
    products = []
    for agg in product_aggregates:
        products.append({
            'product_id': agg['product_id'],
            'product_name': agg['product__name'],
            'hours': agg['hours'] or Decimal('0'),
        })
    
    products_with_percent = calculate_percentages(products, total_hours)
    
    # Group by employee
    employee_aggregates = ContributionRecord.objects.filter(
        pod_id=pod_id,
        contribution_month=month
    ).values('employee_id', 'employee__employee_code', 'employee__name').annotate(
        hours=Sum('effort_hours')
    ).order_by('-hours')
    
    employees = []
    for agg in employee_aggregates:
        employees.append({
            'employee_id': agg['employee_id'],
            'employee_code': agg['employee__employee_code'],
            'employee_name': agg['employee__name'],
            'hours': agg['hours'] or Decimal('0'),
        })
    
    employees_with_percent = calculate_percentages(employees, total_hours)
    
    # Get employee product breakdowns
    employee_breakdowns = []
    for emp_agg in employee_aggregates:
        emp_id = emp_agg['employee_id']
        emp_total = contribution_storage.get_total_hours_by_employee(emp_id, month)
        
        emp_product_aggregates = ContributionRecord.objects.filter(
            pod_id=pod_id,
            employee_id=emp_id,
            contribution_month=month
        ).values('product_id', 'product__name').annotate(
            hours=Sum('effort_hours')
        ).order_by('-hours')
        
        emp_products = []
        for prod_agg in emp_product_aggregates:
            emp_products.append({
                'product_id': prod_agg['product_id'],
                'product_name': prod_agg['product__name'],
                'hours': prod_agg['hours'] or Decimal('0'),
            })
        
        emp_products_with_percent = calculate_percentages(emp_products, emp_total)
        
        employee_breakdowns.append(EmployeeBreakdownDTO(
            employee_id=emp_id,
            employee_code=emp_agg['employee__employee_code'],
            employee_name=emp_agg['employee__name'],
            total_hours=emp_total,
            products=[
                ProductBreakdownDTO(
                    product_id=item['product_id'],
                    product_name=item['product_name'],
                    hours=item['hours'],
                    percent=item['percent'],
                )
                for item in emp_products_with_percent
            ],
        ))
    
    # Get pod name
    from contributions.storages import pod_storage
    pod = pod_storage.get_pod_by_id(pod_id)
    
    return PodMetricsDTO(
        pod_id=pod_id,
        pod_name=pod.name,
        month=month.strftime('%Y-%m'),
        total_hours=total_hours,
        products=[
            ProductBreakdownDTO(
                product_id=item['product_id'],
                product_name=item['product_name'],
                hours=item['hours'],
                percent=item['percent'],
            )
            for item in products_with_percent
        ],
        employees=employee_breakdowns,
    )


def calculate_employee_metrics(employee_id: int, month: date) -> EmployeeMetricsDTO:
    """Calculate employee-level metrics."""
    total_hours = contribution_storage.get_total_hours_by_employee(employee_id, month)
    
    # Group by product
    product_aggregates = ContributionRecord.objects.filter(
        employee_id=employee_id,
        contribution_month=month
    ).values('product_id', 'product__name').annotate(
        hours=Sum('effort_hours')
    ).order_by('-hours')
    
    products = []
    for agg in product_aggregates:
        products.append({
            'product_id': agg['product_id'],
            'product_name': agg['product__name'],
            'hours': agg['hours'] or Decimal('0'),
        })
    
    products_with_percent = calculate_percentages(products, total_hours)
    
    # Group by feature
    feature_aggregates = ContributionRecord.objects.filter(
        employee_id=employee_id,
        contribution_month=month
    ).values('feature_id', 'feature__name', 'description').annotate(
        hours=Sum('effort_hours')
    ).order_by('-hours')
    
    features = []
    for agg in feature_aggregates:
        features.append({
            'feature_id': agg['feature_id'],
            'feature_name': agg['feature__name'],
            'hours': agg['hours'] or Decimal('0'),
            'description': agg.get('description'),
        })
    
    features_with_percent = calculate_percentages(features, total_hours)
    
    # Get employee info
    from contributions.storages import employee_storage
    employee = employee_storage.get_employee_by_id(employee_id)
    
    return EmployeeMetricsDTO(
        employee_id=employee_id,
        employee_code=employee.employee_code,
        employee_name=employee.name,
        month=month.strftime('%Y-%m'),
        total_hours=total_hours,
        products=[
            ProductBreakdownDTO(
                product_id=item['product_id'],
                product_name=item['product_name'],
                hours=item['hours'],
                percent=item['percent'],
            )
            for item in products_with_percent
        ],
        features=[
            FeatureBreakdownDTO(
                feature_id=item['feature_id'],
                feature_name=item['feature_name'],
                hours=item['hours'],
                percent=item['percent'],
                description=item.get('description'),
            )
            for item in features_with_percent
        ],
    )

