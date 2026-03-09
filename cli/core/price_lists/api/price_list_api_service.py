from cli.core.mpt.api import APIService
from cli.core.mpt.models import PriceList


class PriceListAPIService(APIService):
    """API service for managing price list operations."""

    _base_url = "/catalog/price-lists/"
    _api_model = PriceList

    @property
    def api_collection(self):
        return self._client.catalog.price_lists
