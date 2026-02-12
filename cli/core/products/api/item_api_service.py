from cli.core.mpt.api import RelatedAPIService
from cli.core.mpt.models import MptItem


class ItemAPIService(RelatedAPIService):
    """API service for managing item operations."""

    _base_url = "/catalog/items"
    _api_model = MptItem
