"""Management command to create admin user."""
from django.core.management.base import BaseCommand
from contributions.storages import employee_storage


class Command(BaseCommand):
    help = 'Creates an admin user for administrative operations'
    
    def handle(self, *args, **options):
        employee_code = 'ADMIN001'
        name = 'Admin User'
        email = 'admin@example.com'
        role = 'ADMIN'
        
        # Admin doesn't need department/pod assignment
        admin = employee_storage.get_or_create_employee(
            employee_code=employee_code,
            name=name,
            email=email,
            department_id=None,
            pod_id=None,
            role=role
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Successfully created/updated admin user: {employee_code}')
        )
        self.stdout.write(f'   Employee Code: {admin.employee_code}')
        self.stdout.write(f'   Name: {admin.name}')
        self.stdout.write(f'   Email: {admin.email}')
        self.stdout.write(f'   Role: {admin.role}')
        self.stdout.write(f'   Department: {admin.department_name or "None"}')
        self.stdout.write(f'   Pod: {admin.pod_name or "None"}')
        self.stdout.write(self.style.SUCCESS('\n📝 Login with: {"employee_code": "ADMIN001"}'))

