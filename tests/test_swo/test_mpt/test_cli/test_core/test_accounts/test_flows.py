import json
import os
from operator import itemgetter

import pytest
from swo.mpt.cli.core.accounts.flows import (
    disable_accounts_except,
    does_account_exist,
    find_account,
    find_active_account,
    from_file,
    from_token,
    get_accounts_file_path,
    get_or_create_accounts,
    remove_account,
    write_accounts,
)
from swo.mpt.cli.core.accounts.models import Account
from swo.mpt.cli.core.errors import AccountNotFoundError, NoActiveAccountFoundError
from swo.mpt.cli.core.mpt.models import Account as MPTAccount
from swo.mpt.cli.core.mpt.models import Token


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


def test_from_file(accounts_path, expected_account, another_expected_account):
    accounts = from_file(accounts_path)

    expected_accounts = [expected_account, another_expected_account]
    assert accounts == expected_accounts


def test_get_or_create_accounts_create(tmp_path):
    file_path = tmp_path / ".swocli" / "accounts.json"

    accounts = get_or_create_accounts(file_path)

    assert accounts == []


def test_get_or_create_accounts_get(
    accounts_path, expected_account, another_expected_account
):
    accounts = get_or_create_accounts(accounts_path)

    expected_accounts = [expected_account, another_expected_account]
    assert accounts == expected_accounts


def test_get_accounts_file_path():
    assert str(get_accounts_file_path()) == "/root/.swocli/accounts.json"


def test_does_account_exist(expected_account, another_expected_account):
    assert does_account_exist(
        [expected_account, another_expected_account], expected_account
    )


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


def test_write_accounts(tmp_path, expected_account, another_expected_account):
    file_path = tmp_path / ".swocli" / "accounts.json"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w+"):
        pass

    accounts = [expected_account, another_expected_account]
    write_accounts(file_path, accounts)

    with open(file_path) as f:
        written_accounts = json.load(f)

    assert sorted(written_accounts, key=itemgetter("id")) == [
        a.model_dump() for a in accounts
    ]


def test_disable_accounts_except(expected_account, another_expected_account):
    accounts = [expected_account, another_expected_account]

    accounts = disable_accounts_except(accounts, another_expected_account)

    assert not expected_account.is_active
    assert another_expected_account.is_active


def test_find_account(expected_account, another_expected_account):
    account = find_account(
        [expected_account, another_expected_account], expected_account.id
    )

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
