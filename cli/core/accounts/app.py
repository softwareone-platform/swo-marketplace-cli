from typing import Annotated

import typer
from cli.core.accounts.constants import FETCHING, READING, REMOVING, STATUS_MSG
from cli.core.console import console
from cli.core.errors import (
    AccountNotFoundError,
    MPTAPIError,
    NoActiveAccountFoundError,
)
from cli.core.mpt.client import MPTClient
from cli.core.mpt.flows import get_token
from cli.core.state import state
from rich import box
from rich.table import Table

from .flows import (
    disable_accounts_except,
    does_account_exist,
    find_account,
    find_active_account,
    from_token,
    get_or_create_accounts,
    remove_account,
    write_accounts,
)
from .models import Account

app = typer.Typer()


@app.command(name="add")
def add_account(
    secret: Annotated[str, typer.Argument(help="SoftwareOne Marketplace API Token secret")],
    environment: Annotated[
        str, typer.Option("--environment", "-e", help="URL to the API for environment")
    ] = "https://api.platform.softwareone.com/public/v1",
):
    """Add an account to work with the SoftwareOne Marketplace."""
    with console.status(STATUS_MSG[READING]) as status:
        status.update(f"{STATUS_MSG[FETCHING]} from environment {environment}")
        mpt_client = MPTClient(environment, secret, debug=state.verbose)
        try:
            token = get_token(mpt_client, secret)
        except MPTAPIError as e:
            console.print(
                f"Cannot find account for token {secret} on "
                f"environment {environment}. Exception: {e!s}"
            )
            raise typer.Exit(code=3)
        account = from_token(token, environment)

    accounts = get_or_create_accounts()
    if does_account_exist(accounts, account):
        _ = typer.confirm(
            f"Token for account {account.id} ({account.name}) already exists. Replace it?",
            abort=True,
        )
        accounts = remove_account(accounts, account)

    with console.status(f"Adding account {account.id} ({account.name}) to the configuration file"):
        accounts.append(account)
        accounts = disable_accounts_except(accounts, account)

        write_accounts(accounts)

    table = _account_table("Account has been added")
    table = _list_accounts(table, [account])
    console.print(table)


@app.command(name="activate")
def activate_account(
    account_id: Annotated[
        str,
        typer.Argument(help="SoftwareOne Marketplace Account ID", metavar="ACCOUNT-ID"),
    ],
):
    """Activate SoftwareOne Marketplace account."""
    with console.status(STATUS_MSG[READING]):
        accounts = get_or_create_accounts()

    try:
        account = find_account(accounts, account_id)
    except AccountNotFoundError as e:
        console.print(str(e))
        raise typer.Exit(code=3)

    with console.status(f"Making account {account.id} ({account.name}) active"):
        accounts = disable_accounts_except(accounts, account)
        write_accounts(accounts)

    table = _account_table("Account has been activated")
    table = _list_accounts(table, [account])
    console.print(table)


@app.command(name="remove")
def extract_account(
    account_id: Annotated[
        str,
        typer.Argument(help="SoftwareOne Marketplace Account ID", metavar="ACCOUNT-ID"),
    ],
):
    """Remove SoftwareOne Marketplace account."""
    with console.status(STATUS_MSG[READING]):
        accounts = get_or_create_accounts()

    try:
        account = find_account(accounts, account_id)
    except AccountNotFoundError as e:
        console.print(str(e))
        raise typer.Exit(code=3)

    _ = typer.confirm(
        f"Do you want to remove {account.id} ({account.name})?",
        abort=True,
    )

    with console.status(f"{STATUS_MSG[REMOVING]} {account.id} ({account.name})"):
        accounts = remove_account(accounts, account)
        write_accounts(accounts)

    table = _account_table("Account has been deleted")
    table = _list_accounts(table, [account])
    console.print(table)


@app.command(name="list")
def list_accounts(
    active_only: Annotated[  # noqa: FBT002
        bool, typer.Option("--active", "-a", help="Show only current active account")
    ] = False,
):
    """List available SoftwareOne Marketplace accounts."""
    with console.status(STATUS_MSG[READING]):
        accounts = get_or_create_accounts()

        if active_only:
            accounts = list(filter(lambda a: a.is_active, accounts))

    if not accounts:
        console.print("No account found")
        raise typer.Exit(code=0)

    table = _account_table("Available accounts")
    table = _list_accounts(table, accounts, wrap_secret=False)
    console.print(table)


def get_active_account() -> Account:
    """Check for file and create current active account."""
    with console.status(STATUS_MSG[READING]):
        accounts = get_or_create_accounts()

    try:
        account = find_active_account(accounts)
        console.print(f"Current active account: {account.id} ({account.name})")
        return account
    except NoActiveAccountFoundError as e:
        console.print(str(e))
        raise typer.Exit(code=3)


def _account_table(title: str) -> Table:
    table = Table(title=title, box=box.ROUNDED)

    table.add_column("ID", no_wrap=True)
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Token", no_wrap=True)
    table.add_column("Environment", no_wrap=True)
    table.add_column("Active", justify="center")

    return table


def _list_accounts(table: Table, accounts: list[Account], *, wrap_secret: bool = True) -> Table:  # noqa: C901
    def _wrap_account_type(account_type: str) -> str:  # pragma: no cover
        match account_type:
            case "Vendor":
                return f"[cyan]{account_type}"
            case "Operations":
                return f"[white]{account_type}"
            case "Client":
                return f"[magenta]{account_type}"
            case _:
                return account_type

    def _wrap_active(*, is_active: bool) -> str:  # pragma: no cover
        if is_active:
            return "[red bold]\u2714"
        return ""

    def _wrap_token(account: Account, *, to_wrap_secret: bool) -> str:
        is_new_token = "idt:TKN-" in account.token

        token = account.token if is_new_token else f"{account.token_id}:{account.token}"

        if to_wrap_secret:
            if is_new_token:
                token = f"{token[0:][:22]}*****{token[:4]}"
            else:
                token = f"{token[0:][:4]}*****{token[:4]}"

        return token

    for account in accounts:
        table.add_row(
            account.id,
            account.name,
            _wrap_account_type(account.type),
            _wrap_token(account, to_wrap_secret=wrap_secret),
            account.environment,
            _wrap_active(is_active=account.is_active),
        )

    return table


if __name__ == "__main__":
    app()
