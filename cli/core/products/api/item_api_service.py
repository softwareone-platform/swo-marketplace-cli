from cli.core.mpt.api import RelatedAPIService
from cli.core.mpt.models import Item


class ItemAPIService(RelatedAPIService):
    _base_url = "/catalog/items"
    _api_model = Item
