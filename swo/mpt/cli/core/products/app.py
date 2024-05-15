from typing import Annotated, Optional

import typer
from rich import box
from rich.table import Table
from swo.mpt.cli.core.accounts.app import get_active_account
from swo.mpt.cli.core.console import console
from swo.mpt.cli.core.errors import FileNotExistsError
from swo.mpt.cli.core.mpt.client import client_from_account
from swo.mpt.cli.core.mpt.flows import get_products
from swo.mpt.cli.core.mpt.models import Account as MPTAccount
from swo.mpt.cli.core.mpt.models import Product as MPTProduct
from swo.mpt.cli.core.products.flows import (
    ProductAction,
    check_file_exists,
    check_product_definition,
    check_product_exists,
    get_definition_file,
    sync_product_definition,
)
from swo.mpt.cli.core.stats import ErrorMessagesCollector, ProductStatsCollector

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
    active_account = get_active_account()

    has_pages = True
    page = 0
    while has_pages:
        offset = _offset_by_page(page, page_size)

        with console.status(f"Fetching #{page} page  of products"):
            mpt_client = client_from_account(active_account)
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


@app.command(name="sync")
def sync_product(
    product_path: Annotated[
        str,
        typer.Argument(help="Path to Product Definition file", metavar="PRODUCT-PATH"),
    ],
    is_dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-r",
            help="Do not sync Product Definition. Check the file consistency only.",
        ),
    ] = False,
    force_create: Annotated[
        bool,
        typer.Option(
            "--force-create",
            "-f",
            help="Force create product even if the Product ID exists in the SWO Platform.",
        ),
    ] = False,
):
    """
    Sync product to the environment
    """
    with console.status("Check product definition"):
        product_definition_path = get_definition_file(product_path)

        try:
            check_file_exists(product_definition_path)
        except FileNotExistsError as e:
            console.print(str(e))
            raise typer.Exit(code=3)

        stats = ErrorMessagesCollector()
        stats = check_product_definition(product_definition_path, stats)

    if not stats.is_empty():
        console.print(str(stats))
        raise typer.Exit(code=3)

    console.print(f"Product definition [cyan]{product_path}[/cyan] is correct")

    if not is_dry_run:
        active_account = get_active_account()
        mpt_client = client_from_account(active_account)
        product_stats = ProductStatsCollector()

        product = check_product_exists(mpt_client, product_definition_path)
        if product and not force_create:
            _ = typer.confirm(
                f"Do you want to update product {product.id} ({product.name}) "
                f"for account {active_account.id} ({active_account.name})? "
                f"To create new use --force-create or -f options.",
                abort=True,
            )
            console.print("Only Items updated is supported now.")
            action = ProductAction.UPDATE
        elif product and force_create:
            _ = typer.confirm(
                f"Product {product.id} ({product.name}) for account "
                f"{active_account.id} ({active_account.name}) exists. Do you want to create new?",
                abort=True,
            )
            action = ProductAction.CREATE
        elif not product:
            _ = typer.confirm(
                f"Do you want to create new product for account "
                f"{active_account.id} ({active_account.name})?",
                abort=True,
            )
            action = ProductAction.CREATE

        with console.status("Syncing product definition...") as status:
            product_stats, product = sync_product_definition(
                mpt_client,
                product_definition_path,
                action,
                active_account,
                product_stats,
                status,
            )

        table = _product_stats_table(product_stats)
        table = _list_products_stats(table, product_stats)

        console.print(table)

        if product_stats.is_error:
            raise typer.Exit(code=3)


def _product_stats_table(stats: ProductStatsCollector) -> Table:
    if stats.is_error:
        title = "Product Sync [red bold]FAILED"
    else:
        title = "Product Sync [green bold]SUCCEED"

    table = Table(title, box=box.ROUNDED)

    table.add_column("Total")
    table.add_column("Synced")
    table.add_column("Errors")
    table.add_column("Skipped")

    return table


def _list_products_stats(table: Table, stats: ProductStatsCollector) -> Table:
    for tab_name, tab_stats in stats.tabs.items():
        table.add_row(
            tab_name,
            f"[blue]{tab_stats["total"]}",
            f"[green]{tab_stats["synced"]}",
            f"[red bold]{tab_stats["error"]}",
            f"[white]{tab_stats["skipped"]}",
        )

    return table


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
