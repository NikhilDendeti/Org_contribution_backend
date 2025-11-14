"""Management command to create Pod Leads for all pods that don't have one."""
from django.core.management.base import BaseCommand
from core.models import Pod, Employee
from contributions.storages import (
    department_storage, pod_storage, employee_storage
)


class Command(BaseCommand):
    help = 'Create Pod Leads for all pods that don\'t have one'

    def handle(self, *args, **options):
        # Pod Lead assignments: {pod_name: (employee_code, name, email)}
        pod_lead_assignments = {
            # Tech pods
            'Platform Pod': ('PL006', 'Platform Pod Lead', 'platform_pl@example.com'),
            'Infra Pod': ('PL007', 'Infra Pod Lead', 'infra_pl@example.com'),
            'Mobile Pod': ('PL008', 'Mobile Pod Lead', 'mobile_pl@example.com'),
            'Backend Pod': ('PL009', 'Backend Pod Lead', 'backend_pl@example.com'),
            
            # Marketing pods
            'Growth': ('PL010', 'Growth Pod Lead', 'growth_pl@example.com'),
            'Content': ('PL011', 'Content Pod Lead', 'content_pl@example.com'),
            
            # Sales pods
            'Field Sales': ('PL012', 'Field Sales Pod Lead', 'field_sales_pl@example.com'),
            'Inside Sales': ('PL013', 'Inside Sales Pod Lead', 'inside_sales_pl@example.com'),
            
            # Finance pods
            'Payroll': ('PL014', 'Payroll Pod Lead', 'payroll_pl@example.com'),
        }
        
        created_count = 0
        skipped_count = 0
        
        # Get all pods
        all_pods = Pod.objects.all()
        
        for pod in all_pods:
            # Check if pod already has a Pod Lead
            existing_pl = Employee.objects.filter(pod_id=pod.id, role='POD_LEAD').first()
            
            if existing_pl:
                self.stdout.write(
                    self.style.WARNING(f'Pod "{pod.name}" already has Pod Lead: {existing_pl.employee_code}')
                )
                skipped_count += 1
                continue
            
            # Check if we have an assignment for this pod
            if pod.name not in pod_lead_assignments:
                self.stdout.write(
                    self.style.WARNING(f'No Pod Lead assignment defined for pod: {pod.name}')
                )
                skipped_count += 1
                continue
            
            # Get assignment details
            emp_code, name, email = pod_lead_assignments[pod.name]
            
            # Create Pod Lead
            pod_lead = employee_storage.get_or_create_employee(
                employee_code=emp_code,
                name=name,
                email=email,
                department_id=pod.department_id,
                pod_id=pod.id,
                role='POD_LEAD'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created Pod Lead: {pod_lead.employee_code} ({pod_lead.name}) '
                    f'for pod "{pod.name}" (Dept: {pod.department.name if pod.department else "None"})'
                )
            )
            created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n=== Summary ==='))
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count} Pod Leads'))
        self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count} pods (already have Pod Leads or no assignment)'))
        
        # List all Pod Leads
        self.stdout.write(self.style.SUCCESS(f'\n=== All Pod Leads ==='))
        all_pod_leads = Employee.objects.filter(role='POD_LEAD').order_by('employee_code')
        for pl in all_pod_leads:
            pod_name = pl.pod.name if pl.pod else 'No Pod'
            dept_name = pl.department.name if pl.department else 'No Dept'
            self.stdout.write(
                f'{pl.employee_code}: {pl.name} - Pod: {pod_name} ({dept_name})'
            )

