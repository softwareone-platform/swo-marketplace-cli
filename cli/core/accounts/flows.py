from operator import attrgetter

from cli.core.accounts.handlers import JsonFileHandler
from cli.core.accounts.models import Account
from cli.core.errors import AccountNotFoundError, NoActiveAccountFoundError


def get_or_create_accounts() -> list[Account]:
    """Extract the list of accounts from the passed file or create empty."""
    json_parser = JsonFileHandler()
    accounts = json_parser.read()
    return [Account.model_validate(account) for account in accounts]


def does_account_exist(accounts: list[Account], account: Account) -> bool:
    """Checks if the account exists in the passed list."""
    return any(account_item.id == account.id for account_item in accounts)


def remove_account(accounts: list[Account], account: Account) -> list[Account]:
    """Remove an account from the passed accounts list."""
    return [account_item for account_item in accounts if account_item.id != account.id]


def write_accounts(accounts: list[Account]) -> None:
    """Write accounts list to the file."""
    accounts_data = [
        account_item.model_dump() for account_item in sorted(accounts, key=attrgetter("id"))
    ]
    JsonFileHandler().write(accounts_data)


def disable_accounts_except(accounts: list[Account], except_account: Account) -> list[Account]:
    """Disable all accounts in the passed accounts list and enables the passed account."""
    for account in accounts:
        if account.id == except_account.id:
            account.is_active = True
        else:
            account.is_active = False

    return accounts


def find_account(accounts: list[Account], account_id: str) -> Account:
    """Return account by id."""
    account = next(
        (account_item for account_item in accounts if account_item.id == account_id), None
    )
    if not account:
        raise AccountNotFoundError(account_id)

    return account


def find_active_account(accounts: list[Account]) -> Account:
    """Return an active account."""
    account = next((account_item for account_item in accounts if account_item.is_active), None)
    if not account:
        raise NoActiveAccountFoundError

    return account
