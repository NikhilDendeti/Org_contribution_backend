"""Management command to seed initial products."""
from django.core.management.base import BaseCommand
from contributions.storages import product_storage


class Command(BaseCommand):
    help = 'Seed initial products (Academy, Intensive, NIAT)'

    def handle(self, *args, **options):
        products = ['Academy', 'Intensive', 'NIAT']
        
        for product_name in products:
            product = product_storage.get_or_create_product(product_name)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created/retrieved product: {product.name}')
            )
        
        self.stdout.write(self.style.SUCCESS('Products seeded successfully!'))

