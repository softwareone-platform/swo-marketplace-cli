from typing import Annotated

import typer
from cli.core.accounts.api.account_api_service import MPTAccountService
from cli.core.accounts.constants import FETCHING, READING, REMOVING, STATUS_MSG
from cli.core.accounts.flows import (
    disable_accounts_except,
    does_account_exist,
    find_account,
    find_active_account,
    get_or_create_accounts,
    remove_account,
    write_accounts,
)
from cli.core.accounts.models import Account
from cli.core.accounts.url_parser import protocol_and_host
from cli.core.console import console
from cli.core.console.renderers.accounts import AccountsTableRenderer
from cli.core.errors import (
    AccountNotFoundError,
    MPTAPIError,
    NoActiveAccountFoundError,
)
from mpt_api_client import MPTClient

app = typer.Typer()
accounts_table_renderer = AccountsTableRenderer()


@app.command(name="add")
def add_account(
    secret: Annotated[str, typer.Argument(help="SoftwareOne Marketplace API Token secret")],
    environment: Annotated[
        str,
        typer.Option(
            "--environment",
            "-e",
            help="Protocol and host part of API URL for environment",
            parser=protocol_and_host,
        ),
    ] = "https://api.platform.softwareone.com",
):
    """Add an account to work with the SoftwareOne Marketplace."""
    with console.status(STATUS_MSG[READING]) as status:
        status.update(f"{STATUS_MSG[FETCHING]} from environment {environment}")
        account_service = MPTAccountService(
            MPTClient.from_config(api_token=secret, base_url=environment)
        )
        try:
            token = account_service.get_authentication(secret)
        except (MPTAPIError, ValueError) as error:
            console.print(
                f"Cannot find account for token {secret} on "
                f"environment {environment}. Exception: {error!s}"
            )
            raise typer.Exit(code=3)
        account = Account.from_token(token, environment)

    accounts = get_or_create_accounts()
    if does_account_exist(accounts, account):
        typer.confirm(
            f"Token for account {account.id} ({account.name}) already exists. Replace it?",
            abort=True,
        )
        accounts = remove_account(accounts, account)

    with console.status(f"Adding account {account.id} ({account.name}) to the configuration file"):
        accounts.append(account)
        accounts = disable_accounts_except(accounts, account)

        write_accounts(accounts)

    console.print(accounts_table_renderer.render("Account has been added", [account]))


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
    except AccountNotFoundError as error:
        console.print(str(error))
        raise typer.Exit(code=3)

    with console.status(f"Making account {account.id} ({account.name}) active"):
        accounts = disable_accounts_except(accounts, account)
        write_accounts(accounts)

    console.print(accounts_table_renderer.render("Account has been activated", [account]))


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
    except AccountNotFoundError as error:
        console.print(str(error))
        raise typer.Exit(code=3)

    typer.confirm(
        f"Do you want to remove {account.id} ({account.name})?",
        abort=True,
    )

    with console.status(f"{STATUS_MSG[REMOVING]} {account.id} ({account.name})"):
        accounts = remove_account(accounts, account)
        write_accounts(accounts)

    console.print(accounts_table_renderer.render("Account has been deleted", [account]))


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
            accounts = list(filter(lambda account: account.is_active, accounts))

    if not accounts:
        console.print("No account found")
        raise typer.Exit(code=0)

    console.print(accounts_table_renderer.render("Available accounts", accounts, wrap_secret=False))


def get_active_account() -> Account:
    """Check for file and create current active account."""
    with console.status(STATUS_MSG[READING]):
        accounts = get_or_create_accounts()

    try:
        account = find_active_account(accounts)
    except NoActiveAccountFoundError as error:
        console.print(str(error))
        raise typer.Exit(code=3)

    console.print(f"Current active account: {account.id} ({account.name})")
    return account


if __name__ == "__main__":
    app()
