from swo.mpt.cli.core.mpt.api import APIService
from swo.mpt.cli.core.mpt.models import PriceList


class PriceListAPIService(APIService):
    _base_url = "/catalog/price-lists/"
    _api_model = PriceList
