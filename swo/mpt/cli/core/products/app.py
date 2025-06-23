from functools import partial
from typing import Annotated

import typer
from rich import box
from rich.table import Table
from swo.mpt.cli.core.accounts.app import get_active_account
from swo.mpt.cli.core.console import console
from swo.mpt.cli.core.mpt.client import client_from_account
from swo.mpt.cli.core.mpt.flows import get_products
from swo.mpt.cli.core.mpt.models import Account as MPTAccount
from swo.mpt.cli.core.mpt.models import Product as MPTProduct
from swo.mpt.cli.core.products.api import (
    ItemAPIService,
    ItemGroupAPIService,
    ParameterGroupAPIService,
    ParametersAPIService,
    TemplateAPIService,
)
from swo.mpt.cli.core.products.api.product_api_service import ProductAPIService
from swo.mpt.cli.core.products.handlers import (
    AgreementParametersExcelFileManager,
    ItemExcelFileManager,
    ItemGroupExcelFileManager,
    ItemParametersExcelFileManager,
    ProductExcelFileManager,
    RequestParametersExcelFileManager,
    SubscriptionParametersExcelFileManager,
    TemplateExcelFileManager,
)
from swo.mpt.cli.core.products.handlers.parameter_group_excel_file_manager import (
    ParameterGroupExcelFileManager,
)
from swo.mpt.cli.core.products.models import (
    AgreementParametersData,
    ItemData,
    ItemGroupData,
    ItemParametersData,
    ParameterGroupData,
    ProductData,
    RequestParametersData,
    SubscriptionParametersData,
    TemplateData,
)
from swo.mpt.cli.core.products.services import (
    ItemGroupService,
    ItemService,
    ParameterGroupService,
    ParametersService,
    ProductService,
    TemplateService,
)
from swo.mpt.cli.core.services.service_context import ServiceContext
from swo.mpt.cli.core.stats import ProductStatsCollector

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
        str | None,
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
            meta, products = get_products(mpt_client, page_size, offset, query=rql_query)

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
    active_account = get_active_account()
    mpt_client = client_from_account(active_account)
    service_context = ServiceContext(
        account=active_account,
        api=ProductAPIService(mpt_client),
        data_model=ProductData,
        file_manager=ProductExcelFileManager(product_path),
        stats=ProductStatsCollector(),
    )
    product_service = ProductService(service_context)

    result = product_service.validate_definition()
    if not result.success:
        console.print(result.stats.errors)
        raise typer.Exit(code=3)

    console.print(f"Product definition [cyan]{product_path}[/cyan] is correct")
    if is_dry_run:
        raise typer.Exit(code=0)

    product = product_service.retrieve().model
    stats = ProductStatsCollector()
    if product is None or force_create:
        if product is None:
            msg = (
                "Do you want to create new product for account {active_account.id} "
                "({active_account.name})"
            )
        else:
            msg = (
                "Do you want to create new product for account {active_account.id} "
                "({active_account.name}) because the product ID exists in the SWO Platform?"
            )

        _ = typer.confirm(msg, abort=True)

        with console.status("Create product...") as status:
            stats, product = create_product(
                active_account, mpt_client, str(product_path), stats, status
            )
    else:
        _ = typer.confirm(
            f"Do you want to update product {product.id} ({product.name}) "
            f"for account {active_account.id} ({active_account.name})? "
            f"To create new use --force-create or -f options.",
            abort=True,
        )
        console.print("Only Items updated is supported now.")
        with console.status("Update product...") as status:
            stats, product = update_product(
                active_account, mpt_client, str(product_path), stats, product, status
            )

    console.print(stats.to_table())
    if stats.is_error:
        raise typer.Exit(code=3)


def create_product(active_account, mpt_client, product_path, product_stats, status):
    PartialServiceContext = partial(ServiceContext, account=active_account, stats=product_stats)
    product_service = ProductService(
        PartialServiceContext(
            api=ProductAPIService(mpt_client),
            data_model=ProductData,
            file_manager=ProductExcelFileManager(product_path),
        )
    )
    status.update("Create product...")
    result = product_service.create()
    if not result.success or result.model is None:
        return product_stats, None

    product = result.model
    item_group_service = ItemGroupService(
        PartialServiceContext(
            api=ItemGroupAPIService(mpt_client, product.id),
            data_model=ItemGroupData,
            file_manager=ItemGroupExcelFileManager(product_path),
        )
    )
    status.update(f"Create items groups for product {product.id}...")
    item_group_data_collection = item_group_service.create().collection

    parameter_group_service = ParameterGroupService(
        PartialServiceContext(
            api=ParameterGroupAPIService(mpt_client, product.id),
            data_model=ParameterGroupData,
            file_manager=ParameterGroupExcelFileManager(product_path),
        )
    )
    status.update(f"Create parameters groups for product {product.id}...")
    parameter_group_collection_data = parameter_group_service.create().collection

    PartialParameterServiceContext = partial(
        PartialServiceContext, api=ParametersAPIService(mpt_client, product.id)
    )

    agreement_parameter_service = ParametersService(
        PartialParameterServiceContext(
            data_model=AgreementParametersData,
            file_manager=AgreementParametersExcelFileManager(product_path),
        )
    )
    if parameter_group_collection_data is not None:
        agreement_parameter_service.set_new_parameter_group(parameter_group_collection_data)

    status.update(f"Create agreement parameters for product {product.id}...")
    parameters_data_collection = agreement_parameter_service.create().collection
    item_parameter_service = ParametersService(
        PartialParameterServiceContext(
            data_model=ItemParametersData, file_manager=ItemParametersExcelFileManager(product_path)
        )
    )
    if parameter_group_collection_data is not None:
        item_parameter_service.set_new_parameter_group(parameter_group_collection_data)

    status.update(f"Create item parameters for product {product.id}...")
    item_parameter_data_collection = item_parameter_service.create().collection
    if item_parameter_data_collection is not None:
        parameters_data_collection.add(item_parameter_data_collection.collection)

    request_parameters_service = ParametersService(
        PartialParameterServiceContext(
            data_model=RequestParametersData,
            file_manager=RequestParametersExcelFileManager(product_path),
        )
    )
    if parameter_group_collection_data is not None:
        request_parameters_service.set_new_parameter_group(parameter_group_collection_data)

    status.update(f"Create request parameters for product {product.id}...")
    request_parameter_data_collection = request_parameters_service.create().collection
    if request_parameter_data_collection is not None:
        parameters_data_collection.add(request_parameter_data_collection.collection)

    subscription_parameter_service = ParametersService(
        PartialParameterServiceContext(
            data_model=SubscriptionParametersData,
            file_manager=SubscriptionParametersExcelFileManager(product_path),
        )
    )
    if parameter_group_collection_data is not None:
        subscription_parameter_service.set_new_parameter_group(parameter_group_collection_data)

    status.update(f"Create subscription parameters for product {product.id}...")
    subscription_parameter_data_collection = subscription_parameter_service.create().collection
    if subscription_parameter_data_collection is not None:
        parameters_data_collection.add(subscription_parameter_data_collection.collection)

    template_service = TemplateService(
        PartialServiceContext(
            api=TemplateAPIService(mpt_client, product.id),
            data_model=TemplateData,
            file_manager=TemplateExcelFileManager(product_path),
        )
    )
    if parameters_data_collection is not None:
        template_service.set_new_parameter_group(parameters_data_collection)

    status.update(f"Create template parameters for product {product.id}...")
    template_service.create()

    item_service = ItemService(
        PartialServiceContext(
            api=ItemAPIService(mpt_client),
            data_model=ItemData,
            file_manager=ItemExcelFileManager(product_path),
        )
    )
    if item_group_data_collection is not None:
        item_service.set_new_item_groups(item_group_data_collection)

    status.update(f"Create items for product {product.id}...")
    item_service.create(product_id=product.id)

    return product_stats, product


def update_product(active_account, mpt_client, product_path, product_stats, product, status):
    PartialServiceContext = partial(ServiceContext, account=active_account, stats=product_stats)
    item_service = ItemService(
        PartialServiceContext(
            api=ItemAPIService(mpt_client),
            data_model=ItemData,
            file_manager=ItemExcelFileManager(product_path),
        )
    )
    status.update(f"Update item for {product.id}...")
    item_service.update(product.id)

    return product_stats, product


# TODO: move to to_table()
def _products_table(title: str) -> Table:
    table = Table(title=title, box=box.ROUNDED)

    table.add_column("ID")
    table.add_column("Name", no_wrap=True)
    table.add_column("Status")
    table.add_column("Vendor", no_wrap=True)

    return table


# TODO: move to to_table()
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
