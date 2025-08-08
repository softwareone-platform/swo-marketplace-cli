from operator import attrgetter

from cli.core.accounts.handlers import JsonFileHandler
from cli.core.accounts.models import Account
from cli.core.errors import AccountNotFoundError, NoActiveAccountFoundError
from cli.core.mpt.models import Token


def from_token(token: Token, environment: str) -> Account:
    """Extracts Account from the MPT Token."""
    return Account(
        id=token.account.id,
        name=token.account.name,
        type=token.account.type,
        token=token.token,
        token_id=token.id,
        environment=environment,
        is_active=True,
    )


def get_or_create_accounts() -> list[Account]:
    """Extract the list of accounts from the passed file or create empty."""
    json_parser = JsonFileHandler()
    accounts = json_parser.read()
    return [Account.model_validate(account) for account in accounts]


def does_account_exist(accounts: list[Account], account: Account) -> bool:
    """Checks if the account exists in the passed list."""
    return any(a.id == account.id for a in accounts)


def remove_account(accounts: list[Account], account: Account) -> list[Account]:
    """Remove an account from the passed accounts list."""
    return [a for a in accounts if a.id != account.id]


def write_accounts(accounts: list[Account]) -> None:
    """Write accounts list to the file."""
    accounts_data = [a.model_dump() for a in sorted(accounts, key=attrgetter("id"))]
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
    account = next((a for a in accounts if a.id == account_id), None)
    if not account:
        raise AccountNotFoundError(account_id)

    return account


def find_active_account(accounts: list[Account]) -> Account:
    """Return an active account."""
    account = next((a for a in accounts if a.is_active), None)
    if not account:
        raise NoActiveAccountFoundError()

    return account
