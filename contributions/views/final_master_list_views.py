"""Views for final master list generation."""
from rest_framework.views import APIView
from rest_framework.request import Request
from datetime import datetime, date
from pathlib import Path
from django.conf import settings
from contributions.utils.auth_middleware import get_employee_from_request
from contributions.services.permission_service import check_admin_permission, check_ceo_permission
from contributions.services.final_master_list_service import generate_final_master_list
from contributions.storages import pod_lead_allocation_storage
from contributions.common.response import success_response
from contributions.exceptions import ValidationException, DomainException


class GenerateFinalMasterListView(APIView):
    """View for generating final master list."""
    
    def post(self, request: Request):
        """Generate final master list after all Pod Leads have submitted."""
        try:
            # Get employee from token
            employee = get_employee_from_request(request)
            
            # Check admin or CEO permission
            try:
                check_admin_permission(employee.id)
            except:
                try:
                    check_ceo_permission(employee.id)
                except:
                    return success_response(
                        data={'error': 'Admin or CEO access required'},
                        message='Permission denied',
                        status_code=403
                    )
            
            # Get month parameter
            month = request.query_params.get('month') or request.data.get('month')
            if not month:
                return success_response(
                    data={'error': 'Month parameter is required'},
                    message='Month is required (format: YYYY-MM)',
                    status_code=400
                )
            
            # Validate month format
            try:
                month_date = datetime.strptime(month, '%Y-%m').date()
                month_date = date(month_date.year, month_date.month, 1)
            except ValueError:
                return success_response(
                    data={'error': f'Invalid month format: {month}. Expected YYYY-MM'},
                    message='Invalid month format',
                    status_code=400
                )
            
            # Check if all Pod Leads have submitted
            # Get all pending allocations for this month
            from contributions.models import PodLeadAllocation
            pending_count = PodLeadAllocation.objects.filter(
                contribution_month=month_date,
                status__in=['PENDING']
            ).count()
            
            if pending_count > 0:
                return success_response(
                    data={
                        'error': f'There are {pending_count} pending allocations. All Pod Leads must submit before generating final master list.',
                        'pending_count': pending_count
                    },
                    message='Pending allocations exist',
                    status_code=400
                )
            
            # Generate final master list
            file_path = generate_final_master_list(month_date)
            
            # Generate download URL
            relative_path = file_path.relative_to(Path(settings.MEDIA_ROOT))
            download_url = f"{settings.MEDIA_URL}{relative_path}"
            
            return success_response(
                data={
                    'file_path': str(relative_path),
                    'download_url': download_url,
                    'month': month,
                    'filename': file_path.name
                },
                message='Final master list generated successfully'
            )
        
        except ValidationException as e:
            return success_response(
                data={'error': str(e)},
                message='Validation error',
                status_code=400
            )
        except DomainException as e:
            return success_response(
                data={'error': str(e)},
                message='Domain error',
                status_code=400
            )
        except Exception as e:
            return success_response(
                data={'error': str(e)},
                message='Unexpected error occurred',
                status_code=500
            )


class GetFinalMasterListView(APIView):
    """View for getting final master list."""
    
    def get(self, request: Request):
        """Get final master list if exists."""
        try:
            # Get employee from token
            employee = get_employee_from_request(request)
            
            # Check admin or CEO permission
            try:
                check_admin_permission(employee.id)
            except:
                try:
                    check_ceo_permission(employee.id)
                except:
                    return success_response(
                        data={'error': 'Admin or CEO access required'},
                        message='Permission denied',
                        status_code=403
                    )
            
            # Get month parameter
            month = request.query_params.get('month')
            if not month:
                return success_response(
                    data={'error': 'Month parameter is required'},
                    message='Month is required (format: YYYY-MM)',
                    status_code=400
                )
            
            # Check if file exists
            month_str = month
            filename = f"final_master_list_{month_str}.xlsx"
            file_path = Path(settings.MEDIA_ROOT) / 'final_master_lists' / filename
            
            if not file_path.exists():
                return success_response(
                    data={'error': 'Final master list not found. Please generate it first.'},
                    message='File not found',
                    status_code=404
                )
            
            # Generate download URL
            relative_path = file_path.relative_to(Path(settings.MEDIA_ROOT))
            download_url = f"{settings.MEDIA_URL}{relative_path}"
            
            return success_response(
                data={
                    'file_path': str(relative_path),
                    'download_url': download_url,
                    'month': month,
                    'filename': filename,
                    'exists': True
                },
                message='Final master list found'
            )
        
        except Exception as e:
            return success_response(
                data={'error': str(e)},
                message='Unexpected error occurred',
                status_code=500
            )

