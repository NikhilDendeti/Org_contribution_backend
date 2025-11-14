"""Management command to load the default CSV file."""
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from contributions.interactors.upload_interactor import UploadContributionFileInteractor
from contributions.storages import employee_storage
from contributions.exceptions import DomainException


class Command(BaseCommand):
    help = 'Load the default CSV/Excel file (updatedorganization_contributions_2025-10_all_sheets_normalized.xlsx)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Specific CSV/Excel file to load (relative to project root or media/uploads/)',
            default=None
        )
        parser.add_argument(
            '--uploaded-by',
            type=str,
            help='Employee code of the user uploading (default: CEO001)',
            default='CEO001'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reload even if data exists',
        )

    def handle(self, *args, **options):
        # Find the file (CSV or Excel)
        project_root = Path(settings.BASE_DIR)
        
        if options['file']:
            # Check if it's an absolute path or relative
            if Path(options['file']).is_absolute():
                data_file = Path(options['file'])
            elif (project_root / options['file']).exists():
                data_file = project_root / options['file']
            else:
                uploads_dir = Path(settings.MEDIA_ROOT) / 'uploads'
                data_file = uploads_dir / options['file']
            
            if not data_file.exists():
                self.stdout.write(self.style.ERROR(f'File not found: {data_file}'))
                return
        else:
            # First try to find updatedorganization_contributions_2025-10_all_sheets_normalized.xlsx in project root
            excel_file = project_root / 'updatedorganization_contributions_2025-10_all_sheets_normalized.xlsx'
            if excel_file.exists():
                data_file = excel_file
                self.stdout.write(f'Using file: {excel_file.name}')
            else:
                # Find the most recent CSV/Excel file in uploads
                uploads_dir = Path(settings.MEDIA_ROOT) / 'uploads'
                csv_files = list(uploads_dir.glob('*.csv')) + list(uploads_dir.glob('*.xlsx'))
                if not csv_files:
                    self.stdout.write(self.style.ERROR('No CSV/Excel files found'))
                    return
                data_file = max(csv_files, key=lambda p: p.stat().st_mtime)
                self.stdout.write(f'Using file: {data_file.name}')

        # Get uploaded_by employee
        try:
            uploaded_by = employee_storage.get_employee_by_code(options['uploaded_by'])
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Employee not found: {options["uploaded_by"]}'))
            return

        # Check if we should skip (if data exists and --force not set)
        if not options['force']:
            from contributions.models import ContributionRecord
            from datetime import date
            # Check if there's already data for October 2025
            existing = ContributionRecord.objects.filter(contribution_month=date(2025, 10, 1)).exists()
            if existing:
                self.stdout.write(self.style.WARNING('Data already exists for 2025-10. Use --force to reload.'))
                return

        try:
            self.stdout.write('Loading file...')
            # Pass the file path as string to the interactor
            interactor = UploadContributionFileInteractor(str(data_file), uploaded_by.id)
            result = interactor.execute()
            
            summary = result['summary']
            self.stdout.write(self.style.SUCCESS('✓ File loaded successfully!'))
            self.stdout.write(f'  Total rows: {summary["total_rows"]}')
            self.stdout.write(f'  Created records: {summary["created_records"]}')
            self.stdout.write(f'  Created employees: {summary["created_employees"]}')
            self.stdout.write(f'  Created departments: {summary["created_departments"]}')
            self.stdout.write(f'  Created pods: {summary["created_pods"]}')
            self.stdout.write(f'  Created products: {summary["created_products"]}')
            self.stdout.write(f'  Created features: {summary["created_features"]}')
            if summary['error_count'] > 0:
                self.stdout.write(self.style.WARNING(f'  Errors: {summary["error_count"]}'))
        except DomainException as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))

