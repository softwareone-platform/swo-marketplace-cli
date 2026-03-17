from pathlib import Path
from typing import Annotated

import typer
from cli.core.accounts.app import get_active_account
from cli.core.accounts.containers import AccountContainer
from cli.core.console import console
from cli.core.mpt.flows import get_products
from cli.core.mpt.models import Product as MPTProduct
from cli.core.mpt.mpt_client import create_api_mpt_client_from_account
from cli.core.products.containers import ProductContainer
from cli.core.products.table_formatters import wrap_product_status, wrap_vendor
from rich import box
from rich.status import Status
from rich.table import Table

app = typer.Typer()


@app.command("export")
def export(
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

    out_path = str(Path.cwd()) if out_path is None else out_path
    has_error = False
    for product_id in product_ids:
        has_error = has_error or not _ProductOps.export_product(
            account_container=account_container,
            out_path=out_path,
            product_id=product_id,
        )

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
    page = 0
    while True:
        meta, products = _ProductOps.fetch_products_page(active_account, page, page_size, rql_query)
        console.print(_ProductOps.list_products(_ProductOps.products_table("Products"), products))
        if meta.offset + meta.limit >= meta.total:
            break
        typer.confirm("Do you want to fetch next page?", abort=True)
        page += 1


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

    _ProductOps.sync_product(container, force_create=force_create)

    console.print(container.stats().to_table())
    if container.stats().has_errors:
        raise typer.Exit(code=3)


def create_product(container, status) -> None:
    """Create a product and all related entities."""
    _ProductOps.create_product(container, status)


def update_product(container: ProductContainer, status: Status) -> None:
    """Update a product and all related entities."""
    _ProductOps.update_product(container, status)


class _ProductOps:
    @classmethod
    def add_parameter_group_data(cls, service, parameter_groups, parameters_data) -> None:
        service.set_new_parameter_group(parameter_groups)
        parameters_data.add(service.create().collection.collection)

    @classmethod
    def create_product(cls, container, status) -> None:
        status.update("Create product...")
        result = container.product_service().create()
        if not result.success or result.model is None:
            return
        cls.create_related_components(container, result.model.id, status)

    @classmethod
    def create_item_groups(cls, container, product_id: str, status):
        status.update(f"Create items groups for product {product_id}...")
        return container.item_group_service().create().collection

    @classmethod
    def create_items(cls, container, item_groups, product_id: str, status) -> None:
        status.update(f"Create items for product {product_id}...")
        item_service = container.item_service()
        item_service.set_new_item_groups(item_groups)
        item_service.create()

    @classmethod
    def create_parameter_groups(cls, container, product_id: str, status):
        status.update(f"Create parameters groups for product {product_id}...")
        return container.parameter_group_service().create().collection

    @classmethod
    def create_parameters(cls, container, parameter_groups, product_id: str, status):
        agreement_service = container.agreement_parameters_service()
        agreement_service.set_new_parameter_group(parameter_groups)
        status.update(f"Create agreement parameters for product {product_id}...")
        parameters_data = agreement_service.create().collection
        status.update(f"Create asset parameters for product {product_id}...")
        cls.add_parameter_group_data(
            container.asset_parameters_service(), parameter_groups, parameters_data
        )
        status.update(f"Create item parameters for product {product_id}...")
        cls.add_parameter_group_data(
            container.item_parameters_service(), parameter_groups, parameters_data
        )
        status.update(f"Create request parameters for product {product_id}...")
        cls.add_parameter_group_data(
            container.request_parameters_service(), parameter_groups, parameters_data
        )
        status.update(f"Create subscription parameters for product {product_id}...")
        cls.add_parameter_group_data(
            container.subscription_parameters_service(), parameter_groups, parameters_data
        )
        return parameters_data

    @classmethod
    def create_related_components(cls, container, product_id: str, status) -> None:
        container.resource_id.override(product_id)
        item_groups = cls.create_item_groups(container, product_id, status)
        parameter_groups = cls.create_parameter_groups(container, product_id, status)
        parameters_data = cls.create_parameters(container, parameter_groups, product_id, status)
        cls.create_template(container, parameters_data, product_id, status)
        cls.create_items(container, item_groups, product_id, status)

    @classmethod
    def create_template(cls, container, parameters_data, product_id: str, status) -> None:
        status.update(f"Create template parameters for product {product_id}...")
        template_service = container.template_service()
        template_service.set_new_parameter_group(parameters_data)
        template_service.create()

    @classmethod
    def export_product(
        cls, account_container: AccountContainer, out_path: str, product_id: str
    ) -> bool:
        file_path = Path(out_path) / f"{product_id}.xlsx"
        if not cls.prepare_product_export_path(file_path, out_path, product_id):
            return True
        product_container = ProductContainer(
            account_container=account_container,
            file_path=str(file_path),
            resource_id=product_id,
        )
        with console.status(f"Exporting product with id: {product_id}..."):
            cls.export_product_components(product_container, product_id)
            if product_container.stats().has_errors:
                console.print(f"Product export with id: {product_id} [red bold]FAILED")
                return False
        console.print(f"Product with id: {product_id} has been exported into {file_path}")
        return True

    @classmethod
    def export_product_components(
        cls, product_container: ProductContainer, product_id: str
    ) -> None:
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

    @classmethod
    def fetch_products_page(cls, active_account, page: int, page_size: int, rql_query: str | None):
        offset = page * page_size
        with console.status(f"Fetching #{page} page  of products"):
            mpt_client = create_api_mpt_client_from_account(active_account)
            return get_products(mpt_client, page_size, offset, query=rql_query)

    @classmethod
    def list_products(cls, table: Table, products: list[MPTProduct]) -> Table:
        for product in products:
            table.add_row(
                product.id,
                product.name,
                wrap_product_status(product.status),
                wrap_vendor(product.vendor),
            )
        return table

    @classmethod
    def prepare_product_export_path(cls, file_path: Path, out_path: str, product_id: str) -> bool:
        if file_path.exists():
            overwrite = typer.confirm(
                f"File {file_path} already exists. Do you want to overwrite it?",
                abort=False,
            )
            if not overwrite:
                console.print(f"Skipped export for {product_id}.")
                return False
            file_path.unlink()
            return True
        typer.confirm(f"Do you want to export {product_id} in {out_path}?", abort=True)
        return True

    @classmethod
    def products_table(cls, title: str) -> Table:
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("ID")
        table.add_column("Name", no_wrap=True)
        table.add_column("Status")
        table.add_column("Vendor", no_wrap=True)
        return table

    @classmethod
    def sync_product(cls, container: ProductContainer, *, force_create: bool) -> None:
        product = container.product_service().retrieve().model
        active_account = container.account_container().account()
        if product is None or force_create:
            typer.confirm(
                cls.sync_product_message(active_account, is_missing_product=product is None),
                abort=True,
            )
            with console.status("Create product...") as status:
                create_product(container, status)
            return
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

    @classmethod
    def sync_product_message(cls, active_account, *, is_missing_product: bool) -> str:
        if is_missing_product:
            return (
                f"Do you want to create new product for account {active_account.id} "
                f"({active_account.name})"
            )
        return (
            f"Do you want to create new product for account {active_account.id} "
            f"({active_account.name}) because the product ID exists in the SWO Platform?"
        )

    @classmethod
    def update_product(cls, container: ProductContainer, status: Status) -> None:
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


if __name__ == "__main__":
    app()
