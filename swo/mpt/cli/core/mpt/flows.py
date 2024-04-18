from swo.mpt.cli.core.errors import wrap_http_error

from .client import MPTClient
from .models import Token


@wrap_http_error
def get_token(mpt_client: MPTClient, token_id: str) -> Token:
    """
    Retrieves API Token from the MPT Platform
    """
    response = mpt_client.get(f"/accounts/api-tokens/{token_id}")
    response.raise_for_status()

    return Token.model_validate(response.json())
