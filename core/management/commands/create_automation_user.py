"""Management command to create automation user."""
from django.core.management.base import BaseCommand
from core.models import Employee


class Command(BaseCommand):
    help = 'Creates an automation user for system operations'
    
    def handle(self, *args, **options):
        employee_code = 'AUTO001'
        name = 'Automation User'
        email = 'automation@example.com'
        role = 'AUTOMATION'
        
        employee, created = Employee.objects.get_or_create(
            employee_code=employee_code,
            defaults={
                'name': name,
                'email': email,
                'role': role,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created automation user: {employee_code}')
            )
        else:
            # Update existing user
            employee.name = name
            employee.email = email
            employee.role = role
            employee.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated automation user: {employee_code}')
            )
        
        self.stdout.write(f'Employee Code: {employee.employee_code}')
        self.stdout.write(f'Name: {employee.name}')
        self.stdout.write(f'Email: {employee.email}')
        self.stdout.write(f'Role: {employee.role}')

