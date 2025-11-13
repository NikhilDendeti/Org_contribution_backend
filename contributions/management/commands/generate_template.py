"""Management command to generate Excel template."""
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import pandas as pd


class Command(BaseCommand):
    help = 'Generate canonical Excel template'

    def handle(self, *args, **options):
        # Create template directory
        template_dir = Path(settings.MEDIA_ROOT) / 'templates'
        template_dir.mkdir(parents=True, exist_ok=True)
        
        # Define headers
        headers = [
            'employee_code', 'employee_name', 'email', 'department', 'pod',
            'product', 'feature_name', 'contribution_month', 'effort_hours',
            'description', 'reported_by', 'source'
        ]
        
        # Create sample data
        sample_data = [
            {
                'employee_code': 'EMP001',
                'employee_name': 'John Doe',
                'email': 'john.doe@example.com',
                'department': 'Tech',
                'pod': 'Platform Pod',
                'product': 'Academy',
                'feature_name': 'Content Review',
                'contribution_month': '2025-10',
                'effort_hours': 16,
                'description': 'Worked on Content Review for Academy',
                'reported_by': 'hod_tech@example.com',
                'source': 'darwinbox_export_v1.csv'
            },
            {
                'employee_code': 'EMP001',
                'employee_name': 'John Doe',
                'email': 'john.doe@example.com',
                'department': 'Tech',
                'pod': 'Platform Pod',
                'product': 'Intensive',
                'feature_name': 'Reports',
                'contribution_month': '2025-10',
                'effort_hours': 32,
                'description': 'Worked on Reports for Intensive',
                'reported_by': 'hod_tech@example.com',
                'source': 'darwinbox_export_v1.csv'
            }
        ]
        
        # Create DataFrame
        df = pd.DataFrame(sample_data, columns=headers)
        
        # Save to Excel
        template_path = template_dir / 'contribution_template.xlsx'
        with pd.ExcelWriter(template_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Master', index=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'Template generated at: {template_path}')
        )

