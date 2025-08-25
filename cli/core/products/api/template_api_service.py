from cli.core.mpt.api import RelatedAPIService
from cli.core.mpt.models import Template


class TemplateAPIService(RelatedAPIService):
    """API service for managing template operations."""

    _base_url = "/catalog/products/{resource_id}/templates"
    _api_model = Template
