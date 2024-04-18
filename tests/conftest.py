import shutil
from pathlib import Path

import pytest
import responses
from swo.mpt.cli.core.accounts.models import Account
from swo.mpt.cli.core.mpt.client import MPTClient


@pytest.fixture()
def requests_mocker():
    """
    Allow mocking of http calls made with requests.
    """
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture()
def base_url():
    return "https://example.com"


@pytest.fixture()
def mpt_client(base_url):
    return MPTClient(base_url, "token")


@pytest.fixture()
def mpt_token():
    return {
        "id": "TKN-1234",
        "name": "Adobe Token",
        "account": {
            "id": "ACC-4321",
            "name": "Adobe",
            "type": "Vendor",
        },
    }


@pytest.fixture()
def accounts_path():
    return Path("tests/accounts_config/home/.swocli/accounts.json")


@pytest.fixture()
def new_accounts_path(tmp_path, accounts_path):
    shutil.copyfile(accounts_path, tmp_path / "accounts.json")
    return tmp_path / "accounts.json"


@pytest.fixture()
def expected_account():
    return Account(
        id="ACC-12341",
        name="Account 1",
        type="Vendor",
        secret="secret 1",
        environment="https://example.com",
        is_active=True,
    )


@pytest.fixture()
def another_expected_account():
    return Account(
        id="ACC-12342",
        name="Account 2",
        type="Vendor",
        secret="secret 2",
        environment="https://example.com",
        is_active=False,
    )
