"""Entity views."""
from rest_framework.views import APIView
from rest_framework.request import Request
from contributions.interactors.entity_interactors import (
    ListProductsInteractor, ListFeaturesInteractor
)
from contributions.presenters.entity_presenter import present_products, present_features
from contributions.presenters.error_presenter import present_error
from contributions.common.response import success_response
from contributions.utils.auth_middleware import get_employee_from_request
from contributions.exceptions import DomainException


class ProductListView(APIView):
    """Product list view."""
    
    def get(self, request: Request):
        """Get all products."""
        try:
            get_employee_from_request(request)  # Just check auth
            
            interactor = ListProductsInteractor()
            products = interactor.execute()
            
            response_data = present_products(products)
            return success_response(data=response_data)
        
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to get products: {str(e)}"))


class FeatureListView(APIView):
    """Feature list view."""
    
    def get(self, request: Request):
        """Get features by product."""
        try:
            get_employee_from_request(request)  # Just check auth
            product_id = request.query_params.get('product_id')
            
            if not product_id:
                return success_response(
                    data={'error': 'product_id parameter is required'},
                    message='Missing required parameter',
                    status_code=400
                )
            
            interactor = ListFeaturesInteractor(int(product_id))
            features = interactor.execute()
            
            response_data = present_features(features)
            return success_response(data=response_data)
        
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to get features: {str(e)}"))

