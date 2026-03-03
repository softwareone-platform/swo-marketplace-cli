from typing import Any

from cli.core.mpt.api import RelatedAPIService
from cli.core.mpt.models import MPTItem
from mpt_api_client import MPTClient


class ItemAPIService(RelatedAPIService):
    """API service for managing item operations."""

    _base_url = "/catalog/items"
    _api_model = MPTItem

    def __init__(self, collection_service: Any, mpt_client: MPTClient, resource_id: str):
        super().__init__(collection_service, resource_id)
        self.mpt_client = mpt_client
