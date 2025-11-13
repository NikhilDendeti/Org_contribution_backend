"""Management command to create test users for each role."""
from django.core.management.base import BaseCommand
from contributions.storages import (
    department_storage, pod_storage, employee_storage
)


class Command(BaseCommand):
    help = 'Create test users for each role (CEO, HOD, Pod Lead, Employee)'

    def handle(self, *args, **options):
        # Create a test department
        dept = department_storage.get_or_create_department('Tech')
        self.stdout.write(self.style.SUCCESS(f'Created/retrieved department: {dept.name}'))
        
        # Create a test pod
        pod = pod_storage.get_or_create_pod('Platform Pod', dept.id)
        self.stdout.write(self.style.SUCCESS(f'Created/retrieved pod: {pod.name}'))
        
        # Create CEO user
        ceo = employee_storage.get_or_create_employee(
            employee_code='CEO001',
            name='CEO User',
            email='ceo@example.com',
            department_id=dept.id,
            pod_id=pod.id,
            role='CEO'
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created CEO user: {ceo.employee_code} - {ceo.name} (Role: {ceo.role})')
        )
        
        # Create HOD user
        hod = employee_storage.get_or_create_employee(
            employee_code='HOD001',
            name='HOD User',
            email='hod@example.com',
            department_id=dept.id,
            pod_id=pod.id,
            role='HOD'
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created HOD user: {hod.employee_code} - {hod.name} (Role: {hod.role})')
        )
        
        # Create Pod Lead user
        pod_lead = employee_storage.get_or_create_employee(
            employee_code='PL001',
            name='Pod Lead User',
            email='podlead@example.com',
            department_id=dept.id,
            pod_id=pod.id,
            role='POD_LEAD'
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created Pod Lead user: {pod_lead.employee_code} - {pod_lead.name} (Role: {pod_lead.role})')
        )
        
        # Create Employee user
        employee = employee_storage.get_or_create_employee(
            employee_code='EMP001',
            name='Employee User',
            email='employee@example.com',
            department_id=dept.id,
            pod_id=pod.id,
            role='EMPLOYEE'
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created Employee user: {employee.employee_code} - {employee.name} (Role: {employee.role})')
        )
        
        self.stdout.write(self.style.SUCCESS('\n=== Test Users Created ==='))
        self.stdout.write(self.style.SUCCESS('CEO:    CEO001'))
        self.stdout.write(self.style.SUCCESS('HOD:    HOD001'))
        self.stdout.write(self.style.SUCCESS('Pod Lead: PL001'))
        self.stdout.write(self.style.SUCCESS('Employee: EMP001'))
        self.stdout.write(self.style.SUCCESS('\nUse these employee_code values to get JWT tokens from /api/token/'))

