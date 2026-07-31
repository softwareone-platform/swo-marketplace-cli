import json
import shutil
from functools import partial
from pathlib import Path

import httpx
import pytest
from cli.core.accounts.handlers import JsonFileHandler
from cli.core.accounts.models import Account as CLIAccount


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
def account_file_path(tmp_path):
    return tmp_path / ".swocli" / "accounts.json"


@pytest.fixture
def default_accounts_path(mocker, account_file_path):
    mocker.patch.object(JsonFileHandler, "_default_file_path", account_file_path)
    return account_file_path


def _write_accounts_file(account_file_path, raw_accounts):
    account_file_path.parent.mkdir(parents=True, exist_ok=True)
    account_file_path.write_text(json.dumps(raw_accounts))
    return account_file_path


def _write_accounts(account_file_path, accounts):
    return _write_accounts_file(account_file_path, [account.model_dump() for account in accounts])


def _authorization_header(authenticator):
    request = httpx.Request("GET", "https://example.com/public/v1/")
    return next(authenticator.auth_flow(request)).headers["Authorization"]


@pytest.fixture
def write_accounts_file(account_file_path):
    return partial(_write_accounts_file, account_file_path)


@pytest.fixture
def write_accounts(account_file_path):
    return partial(_write_accounts, account_file_path)


@pytest.fixture
def authorization_header():
    return _authorization_header


@pytest.fixture
def stored_accounts(active_vendor_account, inactive_vendor_account):
    return [active_vendor_account, inactive_vendor_account]


@pytest.fixture
def inactive_vendor_account():
    return CLIAccount(
        id="ACC-12342",
        name="Account 2",
        type="Vendor",
        token="idt:TKN-1111-1112:secret2",  # ruff:ignore[hardcoded-password-func-arg]
        token_id="TKN-1111-1112",  # ruff:ignore[hardcoded-password-func-arg]
        environment="https://example.com",
        is_active=False,
    )
