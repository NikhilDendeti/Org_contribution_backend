"""Storage layer for Feature entities."""
from core.models import Feature
from .storage_dto import FeatureDTO
from ..exceptions import EntityNotFoundException


def get_feature_by_id(feature_id: int) -> FeatureDTO:
    """Get feature by ID."""
    try:
        feature = Feature.objects.select_related('product').get(id=feature_id)
        return FeatureDTO(
            id=feature.id,
            name=feature.name,
            product_id=feature.product_id,
            product_name=feature.product.name,
            description=feature.description,
            created_at=feature.created_at,
            updated_at=feature.updated_at,
        )
    except Feature.DoesNotExist:
        raise EntityNotFoundException(f"Feature with id {feature_id} not found")


def get_or_create_feature(name: str, product_id: int, description: str = None) -> FeatureDTO:
    """Get or create a feature."""
    feature, _ = Feature.objects.get_or_create(
        name=name,
        product_id=product_id,
        defaults={'description': description} if description else {}
    )
    feature.refresh_from_db()
    feature.product.refresh_from_db()
    return FeatureDTO(
        id=feature.id,
        name=feature.name,
        product_id=feature.product_id,
        product_name=feature.product.name,
        description=feature.description,
        created_at=feature.created_at,
        updated_at=feature.updated_at,
    )


def list_features_by_product(product_id: int) -> list[FeatureDTO]:
    """List features by product."""
    features = Feature.objects.filter(product_id=product_id).select_related('product').order_by('name')
    return [
        FeatureDTO(
            id=feature.id,
            name=feature.name,
            product_id=feature.product_id,
            product_name=feature.product.name,
            description=feature.description,
            created_at=feature.created_at,
            updated_at=feature.updated_at,
        )
        for feature in features
    ]

