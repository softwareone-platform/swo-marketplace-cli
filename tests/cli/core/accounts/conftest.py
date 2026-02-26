import shutil
from pathlib import Path

import pytest
from cli.core.accounts.models import Account as CLIAccount
from mpt_api_client import MPTClient as MPTAPIClient


@pytest.fixture
def mock_mpt_api_client(mocker):
    return mocker.MagicMock(spec=MPTAPIClient)


@pytest.fixture
def mock_mpt_api_tokens(mock_mpt_api_client):
    return mock_mpt_api_client.accounts.api_tokens.get.return_value


@pytest.fixture
def accounts_path():
    return Path("tests/accounts_config/home/.swocli/accounts.json")


@pytest.fixture
def new_accounts_path(tmp_path, accounts_path):
    shutil.copyfile(accounts_path, tmp_path / "accounts.json")
    return tmp_path / "accounts.json"


@pytest.fixture
def inactive_vendor_account():
    return CLIAccount(
        id="ACC-12342",
        name="Account 2",
        type="Vendor",
        token="idt:TKN-1111-1112:secret2",  # noqa: S106
        token_id="TKN-1111-1112",  # noqa: S106
        environment="https://example.com",
        is_active=False,
    )
