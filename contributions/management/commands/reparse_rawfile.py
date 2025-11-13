"""Management command to reparse a raw file."""
from django.core.management.base import BaseCommand
from contributions.interactors.upload_interactor import UploadContributionFileInteractor
from contributions.services.file_storage_service import get_file_path_by_id
from contributions.storages import raw_file_storage, contribution_storage
from contributions.models import ContributionRecord


class Command(BaseCommand):
    help = 'Reparse a raw file'

    def add_arguments(self, parser):
        parser.add_argument('raw_file_id', type=int, help='Raw file ID to reparse')
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            help='Delete existing contribution records before reparsing',
        )

    def handle(self, *args, **options):
        raw_file_id = options['raw_file_id']
        delete_existing = options['delete_existing']
        
        try:
            raw_file = raw_file_storage.get_raw_file_by_id(raw_file_id)
            
            if delete_existing:
                # Delete existing records
                deleted_count = ContributionRecord.objects.filter(source_file_id=raw_file_id).delete()[0]
                self.stdout.write(
                    self.style.WARNING(f'Deleted {deleted_count} existing contribution records')
                )
            
            # Get file path
            file_path = get_file_path_by_id(raw_file_id)
            
            if not file_path.exists():
                self.stdout.write(self.style.ERROR(f'File not found at: {file_path}'))
                return
            
            # Create a file-like object for the interactor
            from django.core.files.uploadedfile import InMemoryUploadedFile
            from io import BytesIO
            
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            file_obj = BytesIO(file_content)
            mock_file = InMemoryUploadedFile(
                file_obj, None, raw_file.file_name, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                len(file_content), None
            )
            
            # Reparse (skip file saving since it already exists)
            # We need to modify the interactor to accept an existing file path
            # For now, let's parse directly
            from contributions.services import file_parser_service
            from contributions.services.file_parser_service import normalize_month
            from contributions.storages import (
                department_storage, pod_storage, product_storage, feature_storage,
                employee_storage, contribution_storage
            )
            from contributions.storages.storage_dto import ContributionRecordDTO
            from decimal import Decimal
            from django.db import transaction
            
            parsed_rows, errors = file_parser_service.parse_excel_file(str(file_path))
            
            created_records = []
            with transaction.atomic():
                for row in parsed_rows:
                    dept = department_storage.get_or_create_department(row['department'])
                    pod = pod_storage.get_or_create_pod(row['pod'], dept.id)
                    product = product_storage.get_or_create_product(row['product'])
                    feature = None
                    if row.get('feature_name') and row['feature_name'].strip():
                        feature = feature_storage.get_or_create_feature(
                            row['feature_name'], product.id, row.get('description', '')
                        )
                    employee = employee_storage.get_or_create_employee(
                        employee_code=row['employee_code'],
                        name=row['employee_name'],
                        email=row['email'],
                        department_id=dept.id,
                        pod_id=pod.id,
                    )
                    contribution_month = normalize_month(row['contribution_month'])
                    effort_hours = Decimal(str(row['effort_hours']))
                    record = ContributionRecordDTO(
                        employee_id=employee.id,
                        department_id=dept.id,
                        pod_id=pod.id,
                        product_id=product.id,
                        feature_id=feature.id if feature else None,
                        contribution_month=contribution_month,
                        effort_hours=effort_hours,
                        description=row.get('description', ''),
                        source_file_id=raw_file_id,
                    )
                    created_records.append(record)
                
                records_created = contribution_storage.bulk_create_contributions(created_records, raw_file_id)
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully reparsed file. Created {records_created} records')
            )
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

