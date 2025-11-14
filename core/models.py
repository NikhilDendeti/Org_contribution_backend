from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Department(models.Model):
    """Department model representing organizational departments."""
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'
        ordering = ['name']

    def __str__(self):
        return self.name


class Pod(models.Model):
    """Pod model representing teams within departments."""
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='pods')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pods'
        ordering = ['department', 'name']
        unique_together = [['name', 'department']]

    def __str__(self):
        return f"{self.department.name} - {self.name}"


class Product(models.Model):
    """Product model representing organizational products."""
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['name']

    def __str__(self):
        return self.name


class Feature(models.Model):
    """Feature model representing features within products."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='features')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'features'
        ordering = ['product', 'name']
        unique_together = [['product', 'name']]

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class Employee(models.Model):
    """Employee model representing employees in the organization."""
    ROLE_CHOICES = [
        ('CEO', 'CEO'),
        ('HOD', 'Head of Department'),
        ('POD_LEAD', 'Pod Lead'),
        ('EMPLOYEE', 'Employee'),
        ('ADMIN', 'Admin'),
        ('AUTOMATION', 'Automation'),
    ]

    employee_code = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    pod = models.ForeignKey(Pod, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    pod_head = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='direct_reports')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    monthly_baseline_hours = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('160.00'), validators=[MinValueValidator(Decimal('0'))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees'
        ordering = ['name']
        indexes = [
            models.Index(fields=['employee_code'], name='idx_employees_code'),
        ]

    def __str__(self):
        return f"{self.employee_code} - {self.name}"
