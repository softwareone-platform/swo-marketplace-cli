from cli.core.mpt.api import RelatedAPIService
from cli.core.mpt.models import ParameterGroup


class ParameterGroupAPIService(RelatedAPIService):
    _base_url = "/catalog/products/{resource_id}/parameter-groups"
    _api_model = ParameterGroup
