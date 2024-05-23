import json
import os
from operator import attrgetter
from pathlib import Path

from swo.mpt.cli.core.accounts.models import Account
from swo.mpt.cli.core.errors import AccountNotFoundError, NoActiveAccountFoundError
from swo.mpt.cli.core.mpt.models import Token


def from_token(token: Token, environment: str) -> Account:
    """
    Extracts Account from the MPT Token
    """
    return Account(
        id=token.account.id,
        name=token.account.name,
        type=token.account.type,
        token=token.token,
        token_id=token.id,
        environment=environment,
        is_active=True,
    )


def from_file(accounts_file_path: Path) -> list[Account]:
    """
    Extracts list of accounts from the passed file
    """
    with open(accounts_file_path) as f:
        accounts = json.load(f)

    return [Account.model_validate(account) for account in accounts]


def get_or_create_accounts(accounts_file_path: Path) -> list[Account]:
    """
    Extract list of accounts from the passed file or create empty
    """
    if not os.path.exists(accounts_file_path):
        os.makedirs(os.path.dirname(accounts_file_path), exist_ok=True)
        with open(accounts_file_path, "w+") as f:
            f.write("[]")

    return from_file(accounts_file_path)


def get_accounts_file_path() -> Path:
    """
    Returns accounts file path
    """
    return Path.home() / ".swocli" / "accounts.json"


def does_account_exist(accounts: list[Account], account: Account) -> bool:
    """
    Checks if account exists in the passed list
    """
    return any(a.id == account.id for a in accounts)


def remove_account(accounts: list[Account], account: Account) -> list[Account]:
    """
    Remove account from the passed accounts list
    """
    return [a for a in accounts if a.id != account.id]


def write_accounts(accounts_file_path: Path, accounts: list[Account]) -> None:
    """
    Write accounts list to the file
    """
    accounts_dict: list[dict] = [
        a.model_dump() for a in sorted(accounts, key=attrgetter("id"))
    ]

    with open(accounts_file_path, "w") as f:
        accounts_json = json.dumps(accounts_dict, indent=2)
        f.write(accounts_json)


def disable_accounts_except(
    accounts: list[Account], except_account: Account
) -> list[Account]:
    """
    Disable all account in the passed accounts list and enables passed account
    """
    for account in accounts:
        if account.id == except_account.id:
            account.is_active = True
        else:
            account.is_active = False

    return accounts


def find_account(accounts: list[Account], account_id: str) -> Account:
    """
    Return account by id
    """
    account = next((a for a in accounts if a.id == account_id), None)
    if not account:
        raise AccountNotFoundError(account_id)

    return account


def find_active_account(accounts: list[Account]) -> Account:
    """
    Return active account
    """
    account = next((a for a in accounts if a.is_active), None)
    if not account:
        raise NoActiveAccountFoundError()

    return account
