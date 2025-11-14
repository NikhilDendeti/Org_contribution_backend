"""URL configuration for contributions app."""
from django.urls import path
from contributions.views import (
    upload_views, dashboard_views, entity_views, raw_file_views, auth_views, user_views,
    employee_master_views, feature_upload_views, pod_lead_allocation_views,
    allocation_processing_views, sheet_distribution_views, automation_views,
    final_master_list_views
)

app_name = 'contributions'

urlpatterns = [
    # Authentication
    path('token/', auth_views.EmployeeTokenObtainView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', auth_views.EmployeeTokenRefreshView.as_view(), name='token_refresh'),
    
    # User Profile
    path('me/', user_views.CurrentUserView.as_view(), name='current_user'),
    
    # Upload endpoints
    path('uploads/csv/', upload_views.UploadContributionFileView.as_view(), name='upload_csv'),
    path('uploads/<int:raw_file_id>/', raw_file_views.GetRawFileView.as_view(), name='get_raw_file'),
    path('uploads/<int:raw_file_id>/download/', raw_file_views.DownloadRawFileView.as_view(), name='download_raw_file'),
    path('uploads/<int:raw_file_id>/errors/', raw_file_views.DownloadErrorsCSVView.as_view(), name='download_errors_csv'),
    
    # Dashboard endpoints
    path('dashboards/org/', dashboard_views.OrgDashboardView.as_view(), name='org_dashboard'),
    path('dashboards/department/<int:dept_id>/', dashboard_views.DepartmentDashboardView.as_view(), name='department_dashboard'),
    path('pods/<int:pod_id>/contributions/', dashboard_views.PodContributionsView.as_view(), name='pod_contributions'),
    path('employees/<int:employee_id>/contributions/', dashboard_views.EmployeeContributionsView.as_view(), name='employee_contributions'),
    
    # Entity endpoints
    path('products/', entity_views.ProductListView.as_view(), name='list_products'),
    path('features/', entity_views.FeatureListView.as_view(), name='list_features'),
    
    # Admin endpoints
    path('admin/employees/import/', employee_master_views.ImportEmployeeMasterView.as_view(), name='import_employee_master'),
    path('admin/features/upload/', feature_upload_views.UploadFeatureCSVView.as_view(), name='upload_feature_csv'),
    path('admin/sheets/generate-all/', sheet_distribution_views.GenerateAllPodSheetsView.as_view(), name='generate_all_sheets'),
    path('admin/allocations/<int:pod_id>/process/', allocation_processing_views.ProcessPodAllocationsView.as_view(), name='process_allocations'),
    
    # Pod Lead allocation endpoints
    path('pod-leads/<int:pod_id>/allocation-sheet/', pod_lead_allocation_views.GetPodAllocationSheetView.as_view(), name='get_allocation_sheet'),
    path('pod-leads/<int:pod_id>/allocation-sheet/download/', pod_lead_allocation_views.DownloadPodAllocationSheetView.as_view(), name='download_allocation_sheet'),
    path('pod-leads/<int:pod_id>/allocations/', pod_lead_allocation_views.GetPodAllocationsView.as_view(), name='get_pod_allocations'),
    path('pod-leads/<int:pod_id>/allocations/submit/', pod_lead_allocation_views.SubmitPodAllocationView.as_view(), name='submit_allocations'),
    
    # Automation endpoints
    path('automation/upload-initial-xlsx/', automation_views.UploadInitialXLSXView.as_view(), name='upload_initial_xlsx'),
    
    # Final master list endpoints
    path('admin/final-master-list/generate/', final_master_list_views.GenerateFinalMasterListView.as_view(), name='generate_final_master_list'),
    path('admin/final-master-list/', final_master_list_views.GetFinalMasterListView.as_view(), name='get_final_master_list'),
]

