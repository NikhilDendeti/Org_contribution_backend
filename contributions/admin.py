from django.contrib import admin
from .models import RawFile, ContributionRecord, PodLeadAllocation


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


@admin.register(PodLeadAllocation)
class PodLeadAllocationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'pod_lead', 'contribution_month', 'product', 'academy_percent', 'intensive_percent', 'niat_percent', 'status', 'is_verified_description']
    list_filter = ['contribution_month', 'status', 'is_verified_description', 'product']
    search_fields = ['employee__employee_code', 'employee__name', 'pod_lead__employee_code', 'pod_lead__name', 'product']
    date_hierarchy = 'contribution_month'
    readonly_fields = ['created_at', 'updated_at']
