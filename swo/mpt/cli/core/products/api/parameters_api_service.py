from swo.mpt.cli.core.mpt.api import RelatedAPIService
from swo.mpt.cli.core.mpt.models import Parameter


class ParametersAPIService(RelatedAPIService):
    _base_url = "/catalog/products/{resource_id}/parameters"
    _api_model = Parameter
