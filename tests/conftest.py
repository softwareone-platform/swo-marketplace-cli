import shutil
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import responses
from cli.core.accounts.containers import AccountContainer
from cli.core.accounts.models import Account as CLIAccount
from cli.core.mpt.client import MPTClient
from cli.core.mpt.models import Account, Product


@pytest.fixture
def account_container_mock(mocker, operations_account):
    container = AccountContainer()
    container.account.override(MagicMock(return_value=operations_account))
    container.mpt_client.override(MagicMock(MPTClient))
    mock = mocker.patch("cli.core.products.app.AccountContainer", autospec=True)
    mock.return_value = container

    return container


@pytest.fixture
def requests_mocker():
    """
    Allow mocking of http calls made with requests.
    """
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def base_url():
    return "https://example.com"


@pytest.fixture
def mpt_client(base_url):
    return MPTClient(base_url, "token")


@pytest.fixture
def wrap_to_mpt_list_response():
    def _wrap_to_list(list_response):
        return {
            "data": list_response,
            "$meta": {
                "pagination": {
                    "limit": 10,
                    "offset": 0,
                    "total": 2,
                },
            },
        }

    return _wrap_to_list


@pytest.fixture
def mpt_token():
    return {
        "id": "TKN-0000-0000-0001",
        "name": "Adobe Token",
        "token": "TKN-1234",
        "account": {
            "id": "ACC-4321",
            "name": "Adobe",
            "type": "Vendor",
        },
    }


@pytest.fixture
def mpt_products():
    return [
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
    ]


@pytest.fixture
def mpt_uom():
    return {
        "id": "UM-1234-1234",
        "name": "User",
    }


@pytest.fixture
def product():
    return Product(
        id="PRD-1234-1234",
        name="Adobe for Commercial",
        status="Draft",
        vendor=Account(id="ACC-4321", name="Adobe", type="Vendor"),
    )


@pytest.fixture
def mpt_products_response(wrap_to_mpt_list_response, mpt_products):
    return wrap_to_mpt_list_response(mpt_products)


@pytest.fixture
def mpt_uoms_response(wrap_to_mpt_list_response, mpt_uom):
    return wrap_to_mpt_list_response([mpt_uom])


@pytest.fixture
def accounts_path():
    return Path("tests/accounts_config/home/.swocli/accounts.json")


@pytest.fixture
def new_accounts_path(tmp_path, accounts_path):
    shutil.copyfile(accounts_path, tmp_path / "accounts.json")
    return tmp_path / "accounts.json"


@pytest.fixture
def expected_account():
    return CLIAccount(
        id="ACC-12341",
        name="Account 1",
        type="Vendor",
        token="secret 1",  # noqa: S106
        token_id="TKN-0000-0000-0001",  # noqa: S106
        environment="https://example.com",
        is_active=True,
    )


@pytest.fixture
def operations_account():
    return CLIAccount(
        id="ACC-12341",
        name="Account 1",
        type="Operations",
        token="secret 1",  # noqa: S106
        token_id="TKN-0000-0000-0001",  # noqa: S106
        environment="https://example.com",
        is_active=True,
    )


@pytest.fixture
def another_expected_account():
    return CLIAccount(
        id="ACC-12342",
        name="Account 2",
        type="Vendor",
        token="idt:TKN-0000-0000-0002:secret 2",  # noqa: S106
        token_id="TKN-0000-0000-0002",  # noqa: S106
        environment="https://example.com",
        is_active=False,
    )


@pytest.fixture
def active_vendor_account():
    return CLIAccount(
        id="ACC-12341",
        name="Account 1",
        type="Vendor",
        token="secret 1",  # noqa: S106
        token_id="TKN-0000-0000-0001",  # noqa: S106
        environment="https://example.com",
        is_active=True,
    )


@pytest.fixture
def active_operations_account():
    return CLIAccount(
        id="ACC-12341",
        name="Account 1",
        type="Operations",
        token="secret 1",  # noqa: S106
        token_id="TKN-0000-0000-0001",  # noqa: S106
        environment="https://example.com",
        is_active=True,
    )


@pytest.fixture
def new_token_account():
    return CLIAccount(
        id="ACC-12341",
        name="Account 1",
        type="Vendor",
        token="idt:TKN-0000-0000-0001:secret 1",  # noqa: S106
        token_id="TKN-0000-0000-0001",  # noqa: S106
        environment="https://example.com",
        is_active=True,
    )
