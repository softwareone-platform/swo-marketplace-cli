from cli.core.mpt.api import RelatedAPIService
from cli.core.mpt.models import ItemGroup


class ItemGroupAPIService(RelatedAPIService):
    _base_url = "/catalog/products/{resource_id}/item-groups"
    _api_model = ItemGroup
