"""URL configuration for contributions app."""
from django.urls import path
from contributions.views import (
    upload_views, dashboard_views, entity_views, raw_file_views, auth_views, user_views
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
]

