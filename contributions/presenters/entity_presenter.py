"""Presenter for entity list responses."""
from contributions.storages.storage_dto import ProductDTO, FeatureDTO, RawFileDTO


def present_products(products: list[ProductDTO]) -> list[dict]:
    """Present products list."""
    return [
        {
            'id': p.id,
            'name': p.name,
        }
        for p in products
    ]


def present_features(features: list[FeatureDTO]) -> list[dict]:
    """Present features list."""
    return [
        {
            'id': f.id,
            'name': f.name,
            'product_id': f.product_id,
            'product_name': f.product_name,
            'description': f.description,
        }
        for f in features
    ]


def present_raw_file(raw_file: RawFileDTO) -> dict:
    """Present raw file."""
    return {
        'id': raw_file.id,
        'file_name': raw_file.file_name,
        'uploaded_by_id': raw_file.uploaded_by_id,
        'uploaded_at': raw_file.uploaded_at.isoformat() if raw_file.uploaded_at else None,
        'file_size': raw_file.file_size,
        'parse_summary': raw_file.parse_summary,
    }

