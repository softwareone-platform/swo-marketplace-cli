from cli.core.mpt.api import APIService
from cli.core.mpt.models import Product


class ProductAPIService(APIService):
    _base_url = "/catalog/products"
    _api_model = Product
