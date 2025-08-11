import json
from operator import itemgetter
from pathlib import Path

import pytest
from cli.core.accounts.flows import (
    disable_accounts_except,
    does_account_exist,
    find_account,
    find_active_account,
    from_token,
    get_or_create_accounts,
    remove_account,
    write_accounts,
)
from cli.core.accounts.handlers import JsonFileHandler
from cli.core.accounts.models import Account
from cli.core.errors import AccountNotFoundError, NoActiveAccountFoundError
from cli.core.mpt.models import Account as MPTAccount
from cli.core.mpt.models import Token


def test_from_token(expected_account):
    token = Token(
        id="TKN-0000-0000-0001",
        account=MPTAccount(
            id="ACC-12341",
            name="Account 1",
            type="Vendor",
        ),
        token="secret 1",
    )
    account = from_token(token, "https://example.com")

    assert account == expected_account


def test_get_or_create_accounts_create(mocker, tmp_path):
    mocker.patch.object(JsonFileHandler, "_default_file_path", tmp_path / "no_exists_file.json")
    accounts = get_or_create_accounts()

    assert accounts == []


def test_get_or_create_accounts_get(
    mocker, accounts_path, expected_account, another_expected_account
):
    mocker.patch.object(JsonFileHandler, "_default_file_path", accounts_path)
    accounts = get_or_create_accounts()

    expected_accounts = [expected_account, another_expected_account]
    assert accounts == expected_accounts


def test_does_account_exist(expected_account, another_expected_account):
    assert does_account_exist([expected_account, another_expected_account], expected_account)


def test_doesnot_account_exist(expected_account, another_expected_account):
    assert not does_account_exist(
        [expected_account, another_expected_account],
        Account(
            id="ACC-4321",
            name="Not exists account",
            type="Vendor",
            token="secret",
            token_id="TKN-0000-0000-0001",
            environment="https://example.com",
            is_active=False,
        ),
    )


def test_remove_account(expected_account, another_expected_account):
    accounts = [expected_account, another_expected_account]

    accounts_after_remove = remove_account(accounts, another_expected_account)

    assert accounts_after_remove == [expected_account]


def test_write_accounts(mocker, tmp_path, expected_account, another_expected_account):
    file_path = tmp_path / ".swocli" / "accounts.json"
    mocker.patch.object(JsonFileHandler, "_default_file_path", file_path)

    accounts = [expected_account, another_expected_account]
    write_accounts(accounts)

    with Path(file_path).open() as f:
        written_accounts = json.load(f)

    assert sorted(written_accounts, key=itemgetter("id")) == [a.model_dump() for a in accounts]


def test_disable_accounts_except(expected_account, another_expected_account):
    accounts = [expected_account, another_expected_account]

    disable_accounts_except(accounts, another_expected_account)

    assert not expected_account.is_active
    assert another_expected_account.is_active


def test_find_account(expected_account, another_expected_account):
    account = find_account([expected_account, another_expected_account], expected_account.id)

    assert account == expected_account


def test_find_account_exception(expected_account, another_expected_account):
    accounts = [expected_account, another_expected_account]

    with pytest.raises(AccountNotFoundError) as e:
        find_account(accounts, "another-account-id")

    assert "nother-account-id" in str(e.value)


def test_find_active_account(expected_account, another_expected_account):
    accounts = [expected_account, another_expected_account]

    account = find_active_account(accounts)

    assert account == expected_account


def test_find_active_account_exception(expected_account, another_expected_account):
    expected_account.is_active = False
    accounts = [expected_account, another_expected_account]

    with pytest.raises(NoActiveAccountFoundError) as e:
        find_active_account(accounts)

    assert "No active account found. Activate any account first" in str(e.value)
