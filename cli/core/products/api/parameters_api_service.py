from cli.core.mpt.api import RelatedAPIService
from cli.core.mpt.models import Parameter


class ParametersAPIService(RelatedAPIService):
    """API service for managing parameter operations."""

    _base_url = "/catalog/products/{resource_id}/parameters"
    _api_model = Parameter
