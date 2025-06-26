from swo.mpt.cli.core.mpt.api import RelatedAPIService
from swo.mpt.cli.core.mpt.models import Template


class TemplateAPIService(RelatedAPIService):
    _base_url = "/catalog/products/{resource_id}/templates"
    _api_model = Template
