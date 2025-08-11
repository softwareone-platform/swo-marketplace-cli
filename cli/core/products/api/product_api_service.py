from cli.core.mpt.api import APIService
from cli.core.mpt.models import Product


class ProductAPIService(APIService):
    """Service for interacting with product-related API endpoints."""

    _base_url: str = "/catalog/products"
    _api_model = Product
