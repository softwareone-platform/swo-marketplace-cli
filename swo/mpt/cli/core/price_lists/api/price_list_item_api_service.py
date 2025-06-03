from swo.mpt.cli.core.mpt.api import APIService
from swo.mpt.cli.core.mpt.models import PriceListItem


class PriceListItemAPIService(APIService):
    _base_url = "/catalog/price-lists/{price_list_id}/items/"
    _api_model = PriceListItem

    def __init__(self, client, price_list_id: str):
        super().__init__(client)
        self._price_list_id = price_list_id

    @property
    def url(self) -> str:
        return self._base_url.format(price_list_id=self._price_list_id)
