import json
from operator import itemgetter
from pathlib import Path

import pytest
from cli.core.accounts.flows import (
    disable_accounts_except,
    does_account_exist,
    find_account,
    find_active_account,
    get_or_create_accounts,
    remove_account,
    write_accounts,
)
from cli.core.accounts.handlers import JsonFileHandler
from cli.core.accounts.models import Account
from cli.core.errors import AccountNotFoundError, NoActiveAccountFoundError
from cli.core.mpt.models import Account as MPTAccount
from cli.core.mpt.models import Token


def test_from_token(active_vendor_account):
    token = Token(
        id="TKN-1111-1111",
        account=MPTAccount(
            id="ACC-12341",
            name="Account 1",
            type="Vendor",
        ),
        token="idt:TKN-1111-1111:secret",  # noqa: S106
    )

    result = Account.from_token(token, "https://example.com")

    assert result == active_vendor_account


def test_get_or_create_accounts_create(mocker, tmp_path):
    mocker.patch.object(JsonFileHandler, "_default_file_path", tmp_path / "no_exists_file.json")

    result = get_or_create_accounts()

    assert result == []


def test_get_or_create_accounts_get(
    mocker, accounts_path, active_vendor_account, inactive_vendor_account
):
    mocker.patch.object(JsonFileHandler, "_default_file_path", accounts_path)

    result = get_or_create_accounts()

    expected_accounts = [active_vendor_account, inactive_vendor_account]
    assert result == expected_accounts


def test_does_account_exist(active_vendor_account, inactive_vendor_account):
    result = does_account_exist(
        [active_vendor_account, inactive_vendor_account], active_vendor_account
    )

    assert result is True


def test_doesnot_account_exist(active_vendor_account, inactive_vendor_account):
    result = does_account_exist(
        [active_vendor_account, inactive_vendor_account],
        Account(
            id="ACC-4321",
            name="Not exists account",
            type="Vendor",
            token="secret",  # noqa: S106
            token_id="TKN-0000-0000-0001",  # noqa: S106
            environment="https://example.com",
            is_active=False,
        ),
    )

    assert result is False


def test_remove_account(active_vendor_account, inactive_vendor_account):
    accounts = [active_vendor_account, inactive_vendor_account]

    result = remove_account(accounts, inactive_vendor_account)

    assert result == [active_vendor_account]


def test_write_accounts(mocker, tmp_path, active_vendor_account, inactive_vendor_account):
    file_path = tmp_path / ".swocli" / "accounts.json"
    mocker.patch.object(JsonFileHandler, "_default_file_path", file_path)
    accounts = [active_vendor_account, inactive_vendor_account]
    write_accounts(accounts)
    with Path(file_path).open(encoding="utf-8") as file_obj:
        written_accounts = json.load(file_obj)

    result = sorted(written_accounts, key=itemgetter("id"))

    assert result == [account.model_dump() for account in accounts]


def test_disable_accounts_except(active_vendor_account, inactive_vendor_account):
    accounts = [active_vendor_account, inactive_vendor_account]

    disable_accounts_except(accounts, inactive_vendor_account)  # act

    assert not active_vendor_account.is_active
    assert inactive_vendor_account.is_active


def test_find_account(active_vendor_account, inactive_vendor_account):
    result = find_account(
        [active_vendor_account, inactive_vendor_account], active_vendor_account.id
    )

    assert result == active_vendor_account


def test_find_account_exception(active_vendor_account, inactive_vendor_account):
    accounts = [active_vendor_account, inactive_vendor_account]

    with pytest.raises(AccountNotFoundError) as error:
        find_account(accounts, "another-account-id")

    assert "nother-account-id" in str(error.value)


def test_find_active_account(active_vendor_account, inactive_vendor_account):
    accounts = [active_vendor_account, inactive_vendor_account]

    result = find_active_account(accounts)

    assert result == active_vendor_account


def test_find_active_account_exception(active_vendor_account, inactive_vendor_account):
    active_vendor_account.is_active = False
    accounts = [active_vendor_account, inactive_vendor_account]

    with pytest.raises(NoActiveAccountFoundError) as error:
        find_active_account(accounts)

    assert "No active account found. Activate any account first" in str(error.value)
