import pytest
import responses
from cli.core.accounts.containers import AccountContainer
from cli.core.accounts.models import Account as CLIAccount
from cli.core.mpt.client import MPTClient


@pytest.fixture
def requests_mocker():
    """Allow mocking of http calls made with requests."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def mpt_client():
    return MPTClient("https://example.com", "token")


@pytest.fixture
def mpt_products_response():
    return {
        "data": [
            {
                "id": "PRD-1234-1234",
                "name": "Adobe for Commercial",
                "status": "Published",
                "vendor": {
                    "id": "ACC-4321",
                    "name": "Adobe",
                    "type": "Vendor",
                },
            },
            {
                "id": "PRD-4321-4321",
                "name": "Azure CSP Commercial",
                "status": "Draft",
                "vendor": {
                    "id": "ACC-1234",
                    "name": "Microsoft",
                    "type": "Vendor",
                },
            },
        ],
        "$meta": {
            "pagination": {
                "limit": 10,
                "offset": 0,
                "total": 2,
            },
        },
    }


@pytest.fixture
def active_operations_account():
    return CLIAccount(
        id="ACC-12340",
        name="Account 1",
        type="Operations",
        token="idt:TKN-1111-1111:secret",  # noqa: S106
        token_id="TKN-1111-1111",  # noqa: S106
        environment="https://example.com",
        is_active=True,
    )


@pytest.fixture
def active_vendor_account():
    return CLIAccount(
        id="ACC-12341",
        name="Account 1",
        type="Vendor",
        token="idt:TKN-1111-1111:secret",  # noqa: S106
        token_id="TKN-1111-1111",  # noqa: S106
        environment="https://example.com",
        is_active=True,
    )


@pytest.fixture
def account_container_mock(mocker, active_operations_account):
    container = AccountContainer()
    container.account.override(mocker.MagicMock(return_value=active_operations_account))
    container.mpt_client.override(mocker.MagicMock(MPTClient))
    mock = mocker.patch("cli.core.products.app.AccountContainer", autospec=True)
    mock.return_value = container

    return container
