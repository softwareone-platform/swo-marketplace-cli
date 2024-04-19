from urllib.parse import urljoin

import pytest
from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.mpt.flows import get_token
from swo.mpt.cli.core.mpt.models import Token


def test_get_token(requests_mocker, mpt_client, mpt_token):
    token_id = "TKN-1234"
    requests_mocker.get(
        urljoin(mpt_client.base_url, f"/accounts/api-tokens/{token_id}"),
        json=mpt_token,
    )

    token = get_token(mpt_client, token_id)

    assert token == Token.model_validate(mpt_token)


def test_get_token_exception(requests_mocker, mpt_client):
    token_id = "TKN-1234"
    requests_mocker.get(
        urljoin(mpt_client.base_url, f"/accounts/api-tokens/{token_id}"),
        status=404,
        json={},
    )

    with pytest.raises(MPTAPIError) as e:
        get_token(mpt_client, token_id)

    assert "404 Client Error: Not Found for url" in str(e.value)
