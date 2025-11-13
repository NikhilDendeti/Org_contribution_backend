"""Storage layer for Product entities."""
from core.models import Product
from .storage_dto import ProductDTO
from ..exceptions import EntityNotFoundException


def get_product_by_id(product_id: int) -> ProductDTO:
    """Get product by ID."""
    try:
        product = Product.objects.get(id=product_id)
        return ProductDTO(
            id=product.id,
            name=product.name,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )
    except Product.DoesNotExist:
        raise EntityNotFoundException(f"Product with id {product_id} not found")


def get_or_create_product(name: str) -> ProductDTO:
    """Get or create a product."""
    product, _ = Product.objects.get_or_create(name=name)
    return ProductDTO(
        id=product.id,
        name=product.name,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


def list_products() -> list[ProductDTO]:
    """List all products."""
    products = Product.objects.all().order_by('name')
    return [
        ProductDTO(
            id=product.id,
            name=product.name,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )
        for product in products
    ]

