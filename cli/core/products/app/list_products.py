from typing import Annotated

import typer
from cli.core.accounts.app import get_active_account
from cli.core.console import console
from cli.core.console.renderers.products import ProductsTableRenderer
from cli.core.mpt.flows import get_products
from cli.core.mpt.mpt_client import create_api_mpt_client_from_account

app = typer.Typer()
products_table_renderer = ProductsTableRenderer()


@app.command(name="list")
def list_products(
    page_size: Annotated[
        int,
        typer.Option("--page", "-p", min=1, help="Products page size"),
    ] = 10,
    rql_query: Annotated[
        str | None,
        typer.Option("--query", "-q", help="RQL Query to filter products list"),
    ] = None,
):
    """List available products from SoftwareOne Marketplace.

    Args:
        page_size: Number of products to display per page.
        rql_query: RQL query string to filter products.

    """
    active_account = get_active_account()
    mpt_client = create_api_mpt_client_from_account(active_account)
    page = 1
    while True:
        with console.status(f"Fetching page {page} of products"):
            meta, products = get_products(
                mpt_client, page_size, (page - 1) * page_size, query=rql_query
            )

        console.print(products_table_renderer.render("Products", products))

        if meta.offset + meta.limit >= meta.total:
            return
        typer.confirm("Do you want to fetch next page?", abort=True)
        page += 1
