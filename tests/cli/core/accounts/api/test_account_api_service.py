import pytest
from cli.core.accounts.api.account_api_service import MPTAccountService
from cli.core.errors import MPTAPIError
from cli.core.mpt.models import Account, Token
from mpt_api_client.exceptions import MPTHttpError


def test_get_authentication_success(api_mpt_client, mock_mpt_api_tokens):
    secret = "idt:TKN-1111-1111:secret"
    response_payload = {
        "id": "TKN-123",
        "token": secret,
        "account": {"id": "ACC-1", "name": "Account 1", "type": "Vendor"},
    }
    mock_mpt_api_tokens.to_dict.return_value = response_payload
    service = MPTAccountService(client=api_mpt_client)

    result = service.get_authentication(secret)

    expected_result = Token(
        id="TKN-123",
        account=Account(
            id="ACC-1",
            name="Account 1",
            type="Vendor",
        ),
        token=secret,
    )
    assert result == expected_result


def test_add_account_token_invalid_format(api_mpt_client):
    secret = "invalid_secret_format"
    service = MPTAccountService(client=api_mpt_client)

    with pytest.raises(ValueError, match=f"Invalid token format: {secret}"):
        service.get_authentication(secret)


def test_get_authentication_value_error(api_mpt_client, mock_mpt_api_tokens):
    secret = "idt:TKN-1111-1111:secret"
    mock_mpt_api_tokens.to_dict.side_effect = MPTHttpError(
        400, "Not Found", "Entity for given id TKN-1111-1111 not found"
    )
    service = MPTAccountService(client=api_mpt_client)

    with pytest.raises(MPTAPIError, match="Entity for given id TKN-1111-1111 not found"):
        service.get_authentication(secret)
