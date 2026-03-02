from cli.core.mpt.api import RelatedAPIService
from cli.core.mpt.models import ItemGroup


class ItemGroupAPIService(RelatedAPIService):
    """API service for managing item group operations."""

    _base_url = "/catalog/products/{resource_id}/item-groups"
    _api_model = ItemGroup

    @property
    def api_collection(self):
        return self._client.catalog.products.item_groups(self.resource_id)
