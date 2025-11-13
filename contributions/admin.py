from django.contrib import admin
from .models import RawFile, ContributionRecord


@admin.register(RawFile)
class RawFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'uploaded_by', 'uploaded_at', 'file_size']
    list_filter = ['uploaded_at']
    search_fields = ['file_name', 'uploaded_by__name', 'uploaded_by__employee_code']
    readonly_fields = ['uploaded_at', 'checksum']


@admin.register(ContributionRecord)
class ContributionRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'product', 'contribution_month', 'effort_hours', 'department', 'pod']
    list_filter = ['contribution_month', 'product', 'department', 'pod']
    search_fields = ['employee__employee_code', 'employee__name', 'product__name']
    date_hierarchy = 'contribution_month'
