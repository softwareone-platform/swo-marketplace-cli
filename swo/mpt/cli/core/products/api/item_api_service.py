from swo.mpt.cli.core.mpt.api import APIService
from swo.mpt.cli.core.mpt.models import Item


class ItemAPIService(APIService):
    _base_url = "/catalog/items/"
    _api_model = Item
