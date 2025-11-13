"""Entity interactors for listing entities."""
from contributions.storages import product_storage, feature_storage, raw_file_storage
from contributions.storages.storage_dto import ProductDTO, FeatureDTO, RawFileDTO
from contributions.exceptions import EntityNotFoundException


class ListProductsInteractor:
    """Interactor for listing all products."""
    
    def execute(self) -> list[ProductDTO]:
        """Execute the product listing."""
        return product_storage.list_products()


class ListFeaturesInteractor:
    """Interactor for listing features by product."""
    
    def __init__(self, product_id: int):
        self.product_id = product_id
    
    def execute(self) -> list[FeatureDTO]:
        """Execute the feature listing."""
        return feature_storage.list_features_by_product(self.product_id)


class GetRawFileInteractor:
    """Interactor for getting raw file details."""
    
    def __init__(self, raw_file_id: int):
        self.raw_file_id = raw_file_id
    
    def execute(self) -> RawFileDTO:
        """Execute the raw file retrieval."""
        try:
            return raw_file_storage.get_raw_file_by_id(self.raw_file_id)
        except EntityNotFoundException:
            raise EntityNotFoundException(f"RawFile with id {self.raw_file_id} not found")

