"""Management command to generate Pod Lead allocation sheets."""
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from contributions.interactors.feature_csv_upload_interactor import UploadFeatureCSVInteractor
from contributions.exceptions import DomainException


class Command(BaseCommand):
    help = 'Generate Pod Lead allocation sheets from feature CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=str,
            required=True,
            help='Month in YYYY-MM format'
        )
        parser.add_argument(
            '--feature-csv',
            type=str,
            help='Path to feature CSV file (optional if allocations already exist)'
        )

    def handle(self, *args, **options):
        month = options['month']
        feature_csv = options.get('feature_csv')
        
        if feature_csv:
            # Resolve file path
            if not Path(feature_csv).is_absolute():
                feature_csv = Path(settings.BASE_DIR) / feature_csv
            else:
                feature_csv = Path(feature_csv)
            
            if not feature_csv.exists():
                self.stdout.write(self.style.ERROR(f'File not found: {feature_csv}'))
                return
            
            try:
                self.stdout.write(f'Generating Pod Lead allocation sheets for {month}...')
                interactor = UploadFeatureCSVInteractor(str(feature_csv), month)
                result = interactor.execute()
                
                summary = result['summary']
                self.stdout.write(self.style.SUCCESS('✓ Sheets generated successfully!'))
                self.stdout.write(f'  Generated sheets: {summary["generated_sheets"]}')
                self.stdout.write(f'  Created allocations: {summary["created_allocations"]}')
                
                if result.get('has_errors'):
                    self.stdout.write(self.style.WARNING(f'  Errors: {len(result["errors"])}'))
            except DomainException as e:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))
        else:
            self.stdout.write(self.style.WARNING('No feature CSV provided. Use --feature-csv option.'))

