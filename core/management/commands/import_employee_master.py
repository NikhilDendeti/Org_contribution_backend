"""Management command to import employee master CSV."""
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from contributions.interactors.employee_master_import_interactor import ImportEmployeeMasterInteractor
from contributions.exceptions import DomainException


class Command(BaseCommand):
    help = 'Import employee master CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to employee master CSV file'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        # Resolve file path
        if not Path(csv_file).is_absolute():
            csv_file = Path(settings.BASE_DIR) / csv_file
        else:
            csv_file = Path(csv_file)
        
        if not csv_file.exists():
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
            return
        
        try:
            self.stdout.write('Importing employee master CSV...')
            interactor = ImportEmployeeMasterInteractor(str(csv_file))
            result = interactor.execute()
            
            summary = result['summary']
            self.stdout.write(self.style.SUCCESS('✓ Employee master imported successfully!'))
            self.stdout.write(f'  Total rows: {summary["total_rows"]}')
            self.stdout.write(f'  Created employees: {summary["created_employees"]}')
            self.stdout.write(f'  Updated employees: {summary["updated_employees"]}')
            self.stdout.write(f'  Created departments: {summary["created_departments"]}')
            self.stdout.write(f'  Created pods: {summary["created_pods"]}')
            
            if result.get('has_errors'):
                self.stdout.write(self.style.WARNING(f'  Errors: {len(result["errors"])}'))
                for error in result['errors'][:10]:  # Show first 10 errors
                    self.stdout.write(f'    Row {error.get("row", "?")}: {error.get("message", "Unknown error")}')
        except DomainException as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))

