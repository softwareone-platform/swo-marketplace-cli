from typing import Annotated, Optional

import typer
from rich import box
from rich.table import Table
from swo.mpt.cli.core.accounts.flows import (
    find_active_account,
    get_accounts_file_path,
    get_or_create_accounts,
)
from swo.mpt.cli.core.console import console
from swo.mpt.cli.core.errors import NoActiveAccountFoundError
from swo.mpt.cli.core.mpt.client import client_from_account
from swo.mpt.cli.core.mpt.flows import get_products
from swo.mpt.cli.core.mpt.models import Account as MPTAccount
from swo.mpt.cli.core.mpt.models import Product as MPTProduct

app = typer.Typer()


def _offset_by_page(page: int, limit: int) -> int:
    return page * limit


@app.command(name="list")
def list_products(
    page_size: Annotated[
        int,
        typer.Option("--page", "-p", help="Products page size"),
    ] = 10,
    rql_query: Annotated[
        Optional[str],
        typer.Option("--query", "-q", help="RQL Query to filter products list"),
    ] = None,
):
    """
    List available products from SoftwareOne Marketplace
    """
    with console.status("Reading accounts from the configuration file"):
        accounts_file_path = get_accounts_file_path()
        accounts = get_or_create_accounts(accounts_file_path)

    try:
        account = find_active_account(accounts)
        console.print(f"Current active account: {account.id} ({account.name})")
    except NoActiveAccountFoundError as e:
        console.print(str(e))
        raise typer.Exit(code=3)

    has_pages = True
    page = 0
    while has_pages:
        offset = _offset_by_page(page, page_size)

        with console.status(f"Fetching #{page} page  of products"):
            mpt_client = client_from_account(account)
            meta, products = get_products(
                mpt_client, page_size, offset, query=rql_query
            )

        table = _products_table("Products")
        table = _list_products(table, products)
        console.print(table)

        if meta.offset + meta.limit < meta.total:
            _ = typer.confirm("Do you want to fetch next page?", abort=True)
            page += 1
        else:
            has_pages = False


def _products_table(title: str) -> Table:
    table = Table(title=title, box=box.ROUNDED)

    table.add_column("ID")
    table.add_column("Name", no_wrap=True)
    table.add_column("Status")
    table.add_column("Vendor", no_wrap=True)

    return table


def _list_products(table: Table, products: list[MPTProduct]) -> Table:
    def _wrap_product_status(status: str) -> str:  # pragma: no cover
        match status:
            case "Draft":
                return f"[white]{status}"
            case "Pending":
                return f"[blue]{status}"
            case "Published":
                return f"[green bold]{status}"
            case "Unpublished":
                return f"[red]{status}"
            case _:
                return status

    def _wrap_vendor(vendor: MPTAccount) -> str:  # pragma: no cover
        return f"{vendor.id} ({vendor.name})"

    for product in products:
        table.add_row(
            product.id,
            product.name,
            _wrap_product_status(product.status),
            _wrap_vendor(product.vendor),
        )

    return table


if __name__ == "__main__":
    app()
