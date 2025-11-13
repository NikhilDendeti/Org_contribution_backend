from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import Employee, Department, Pod, Product, Feature


class RawFile(models.Model):
    """RawFile model for storing uploaded contribution files."""
    file_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='uploaded_files')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    storage_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0)
    checksum = models.CharField(max_length=64, blank=True, null=True)
    parse_summary = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'raw_files'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.file_name} - {self.uploaded_at}"


class ContributionRecord(models.Model):
    """ContributionRecord model for storing monthly contribution data."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='contributions')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='contributions')
    pod = models.ForeignKey(Pod, on_delete=models.CASCADE, related_name='contributions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='contributions')
    feature = models.ForeignKey(Feature, on_delete=models.SET_NULL, null=True, blank=True, related_name='contributions')
    contribution_month = models.DateField()
    effort_hours = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    description = models.TextField(blank=True, null=True)
    source_file = models.ForeignKey(RawFile, on_delete=models.CASCADE, related_name='contribution_records')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contribution_records'
        ordering = ['-contribution_month', 'employee']
        indexes = [
            models.Index(fields=['contribution_month'], name='idx_contrib_month'),
            models.Index(fields=['product', 'contribution_month'], name='idx_contrib_prod_month'),
            models.Index(fields=['pod', 'contribution_month'], name='idx_contrib_pod_month'),
            models.Index(fields=['department', 'contribution_month'], name='idx_contrib_dept_month'),
            models.Index(fields=['employee', 'contribution_month'], name='idx_contrib_emp_month'),
        ]

    def __str__(self):
        return f"{self.employee.employee_code} - {self.product.name} - {self.contribution_month}"
