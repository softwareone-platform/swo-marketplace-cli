from swo.mpt.cli.core.mpt.api import RelatedAPIService
from swo.mpt.cli.core.mpt.models import Item


class ItemAPIService(RelatedAPIService):
    _base_url = "/catalog/items"
    _api_model = Item
