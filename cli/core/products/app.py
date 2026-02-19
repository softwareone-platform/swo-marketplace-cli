from pathlib import Path
from typing import Annotated

import typer
from cli.core.accounts.app import get_active_account
from cli.core.accounts.containers import AccountContainer
from cli.core.console import console
from cli.core.mpt.client import client_from_account
from cli.core.mpt.flows import get_products
from cli.core.mpt.models import Account as MPTAccount
from cli.core.mpt.models import Product as MPTProduct
from cli.core.products.containers import ProductContainer
from rich import box
from rich.status import Status
from rich.table import Table

app = typer.Typer()


def _offset_by_page(page: int, limit: int) -> int:  # noqa: FURB118
    return page * limit


@app.command("export")
def export(  # noqa: C901
    product_ids: Annotated[
        list[str],
        typer.Argument(help="List of product IDs to export"),
    ],
    out_path: Annotated[
        str | None,
        typer.Option(
            "--out",
            "-o",
            help="Specify folder to export price lists to. Default filename is <product-id>.xlsx",
        ),
    ] = None,
):
    """Export products to Excel files.

    Args:
        product_ids: List of product IDs to export.
        out_path: Output directory path. Defaults to current working directory.

    Raises:
        typer.Exit: With code 4 if account is not operations, code 3 if export fails.

    """
    account_container = AccountContainer()
    active_account = account_container.account()
    if not active_account.is_operations():
        console.print(
            f"Current active account {active_account.id} ({active_account.name}) is not "
            f"allowed for the export command. Please, activate an operation account."
        )
        raise typer.Exit(code=4)

    out_path = out_path if out_path is not None else str(Path.cwd())
    has_error = False
    for product_id in product_ids:
        file_path = Path(out_path) / f"{product_id}.xlsx"
        product_container = ProductContainer(
            account_container=account_container, file_path=str(file_path), resource_id=product_id
        )
        if file_path.exists():
            overwrite = typer.confirm(
                f"File {file_path} already exists. Do you want to overwrite it?",
                abort=False,
            )
            if not overwrite:
                console.print(f"Skipped export for {product_id}.")
                continue

            Path(file_path).unlink()
        else:
            typer.confirm(
                f"Do you want to export {product_id} in {out_path}?",
                abort=True,
            )

        with console.status(f"Exporting product with id: {product_id}..."):
            product_container.product_service().export(resource_id=product_id)
            product_container.item_service().export()
            product_container.item_group_service().export()
            product_container.parameter_group_service().export()
            product_container.agreement_parameters_service().export()
            product_container.asset_parameters_service().export()
            product_container.item_parameters_service().export()
            product_container.request_parameters_service().export()
            product_container.subscription_parameters_service().export()
            product_container.template_service().export()

            if product_container.stats().has_errors:
                console.print(f"Product export with id: {product_id} [red bold]FAILED")
                has_error = True
                continue

            console.print(f"Product with id: {product_id} has been exported into {file_path}")

    if has_error:
        raise typer.Exit(code=3)


@app.command(name="list")
def list_products(
    page_size: Annotated[
        int,
        typer.Option("--page", "-p", help="Products page size"),
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

    has_pages = True
    page = 0
    while has_pages:
        offset = _offset_by_page(page, page_size)

        with console.status(f"Fetching #{page} page  of products"):
            mpt_client = client_from_account(active_account)
            meta, products = get_products(mpt_client, page_size, offset, query=rql_query)

        table = _products_table("Products")
        table = _list_products(table, products)
        console.print(table)

        if meta.offset + meta.limit < meta.total:
            typer.confirm("Do you want to fetch next page?", abort=True)
            page += 1
        else:
            has_pages = False


@app.command(name="sync")
def sync_product(
    product_path: Annotated[
        str,
        typer.Argument(help="Path to Product Definition file", metavar="PRODUCT-PATH"),
    ],
    is_dry_run: Annotated[  # noqa: FBT002
        bool,
        typer.Option(
            "--dry-run",
            "-r",
            help="Do not sync Product Definition. Check the file consistency only.",
        ),
    ] = False,
    force_create: Annotated[  # noqa: FBT002
        bool,
        typer.Option(
            "--force-create",
            "-f",
            help="Force create product even if the Product ID exists in the SWO Platform.",
        ),
    ] = False,
):
    """Sync product to the environment.

    Args:
        product_path: Path to the product definition file.
        is_dry_run: Whether to only validate the file without syncing.
        force_create: Whether to force create product even if it exists.

    Raises:
        typer.Exit: With code 3 if validation fails or sync errors occur.

    """
    container = ProductContainer(file_path=str(product_path))
    product_service = container.product_service()
    result = product_service.validate_definition()
    if not result.success:
        console.print(result.stats.errors)
        raise typer.Exit(code=3)

    console.print(f"Product definition [cyan]{product_path}[/cyan] is correct")
    if is_dry_run:
        raise typer.Exit(code=0)

    product = product_service.retrieve().model
    active_account = container.account_container().account()
    if product is None or force_create:
        if product is None:
            msg = (
                f"Do you want to create new product for account {active_account.id} "
                f"({active_account.name})"
            )
        else:
            msg = (
                f"Do you want to create new product for account {active_account.id} "
                f"({active_account.name}) because the product ID exists in the SWO Platform?"
            )

        typer.confirm(msg, abort=True)

        with console.status("Create product...") as status:
            create_product(container, status)
    else:
        typer.confirm(
            f"Do you want to update product {product.id} ({product.name}) "
            f"for account {active_account.id} ({active_account.name})? "
            f"To create new use --force-create or -f options.",
            abort=True,
        )
        console.print("Only Items updated is supported now.")
        with console.status("Update product...") as status:
            container.resource_id.override(product.id)
            update_product(container, status)

    console.print(container.stats().to_table())
    if container.stats().has_errors:
        raise typer.Exit(code=3)


def create_product(container, status):
    """Create a new product with all its components.

    Args:
        container: The product container instance.
        status: The status object used to display progress updates.

    """
    status.update("Create product...")
    result = container.product_service().create()
    if not result.success or result.model is None:
        return

    product = result.model
    container.resource_id.override(product.id)
    status.update(f"Create items groups for product {product.id}...")
    item_group_data_collection = container.item_group_service().create().collection

    status.update(f"Create parameters groups for product {product.id}...")
    parameter_group_collection_data = container.parameter_group_service().create().collection

    agreement_parameter_service = container.agreement_parameters_service()
    agreement_parameter_service.set_new_parameter_group(parameter_group_collection_data)

    status.update(f"Create agreement parameters for product {product.id}...")
    parameters_data_collection = agreement_parameter_service.create().collection

    status.update(f"Create asset parameters for product {product.id}...")
    asset_parameter_service = container.asset_parameters_service()
    asset_parameter_service.set_new_parameter_group(parameter_group_collection_data)
    asset_parameter_data_collection = asset_parameter_service.create().collection
    parameters_data_collection.add(asset_parameter_data_collection.collection)

    status.update(f"Create item parameters for product {product.id}...")
    item_parameter_service = container.item_parameters_service()
    item_parameter_service.set_new_parameter_group(parameter_group_collection_data)
    item_parameter_data_collection = item_parameter_service.create().collection
    parameters_data_collection.add(item_parameter_data_collection.collection)

    status.update(f"Create request parameters for product {product.id}...")
    request_parameters_service = container.request_parameters_service()
    request_parameters_service.set_new_parameter_group(parameter_group_collection_data)
    request_parameter_data_collection = request_parameters_service.create().collection
    parameters_data_collection.add(request_parameter_data_collection.collection)

    status.update(f"Create subscription parameters for product {product.id}...")
    subscription_parameter_service = container.subscription_parameters_service()
    subscription_parameter_service.set_new_parameter_group(parameter_group_collection_data)

    subscription_parameter_data_collection = subscription_parameter_service.create().collection
    parameters_data_collection.add(subscription_parameter_data_collection.collection)

    status.update(f"Create template parameters for product {product.id}...")
    template_service = container.template_service()
    template_service.set_new_parameter_group(parameters_data_collection)
    template_service.create()

    status.update(f"Create items for product {product.id}...")
    item_service = container.item_service()
    item_service.set_new_item_groups(item_group_data_collection)
    item_service.create()


def update_product(container: ProductContainer, status: Status):
    """
    Update product definition.

    Args:
        container: The product container instance.
        status: The status object used to display progress.

    """
    # NOTE: the order cannot be changed to ensure the related components are handled before
    # its group.
    status.update("Update product...")
    container.product_service().update()

    resource_id = container.resource_id()
    status.update(f"Update item for {resource_id}...")
    container.item_service().update()

    status.update(f"Update items groups for product {resource_id}...")
    container.item_group_service().update()

    status.update(f"Update subscription parameters for product {resource_id}...")
    container.template_service().update()

    status.update(f"Update parameters groups for product {resource_id}...")
    container.parameter_group_service().update()

    status.update(f"Update agreement parameters for product {resource_id}...")
    container.agreement_parameters_service().update()

    status.update(f"Update asset parameters for product {resource_id}...")
    container.asset_parameters_service().update()

    status.update(f"Update item parameters for product {resource_id}...")
    container.item_parameters_service().update()

    status.update(f"Update request parameters for product {resource_id}...")
    container.request_parameters_service().update()

    status.update(f"Update subscription parameters for product {resource_id}...")
    container.subscription_parameters_service().update()


# TODO: move to to_table()
def _products_table(title: str) -> Table:
    table = Table(title=title, box=box.ROUNDED)

    table.add_column("ID")
    table.add_column("Name", no_wrap=True)
    table.add_column("Status")
    table.add_column("Vendor", no_wrap=True)

    return table


# TODO: move to to_table()
def _list_products(table: Table, products: list[MPTProduct]) -> Table:  # noqa: C901
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
