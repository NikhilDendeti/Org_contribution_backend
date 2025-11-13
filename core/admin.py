from django.contrib import admin
from .models import Department, Pod, Product, Feature, Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Pod)
class PodAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'created_at']
    list_filter = ['department']
    search_fields = ['name', 'department__name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'created_at']
    list_filter = ['product']
    search_fields = ['name', 'product__name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_code', 'name', 'email', 'department', 'pod', 'role']
    list_filter = ['role', 'department', 'pod']
    search_fields = ['employee_code', 'name', 'email']
