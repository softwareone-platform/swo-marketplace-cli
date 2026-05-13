from typing import Annotated, Any

import typer
from cli.core.console import console
from cli.core.console.renderers.stats import StatsTableRenderer
from cli.core.models import DataCollectionModel
from cli.core.products.containers import ProductContainer
from rich.status import Status

app = typer.Typer()
stats_table_renderer = StatsTableRenderer()


class ProductSyncer:
    """Coordinate the CLI-driven sync of a single product definition file."""

    def __init__(self, product_container: ProductContainer) -> None:
        self._container = product_container
        self._product_service = self._container.product_service()
        account = self._container.account_container().account()
        self._account = account
        self._account_label = f"{account.id} ({account.name})"

    def sync(self, product_path: str, *, is_dry_run: bool, force_create: bool) -> None:
        """Validate the definition and either create or update the product.

        Args:
            product_path: Path to the product definition file (used only for messages).
            is_dry_run: When True, validate the file and exit without syncing.
            force_create: When True, create a new product even if the ID already exists.

        Raises:
            typer.Exit: With code 3 if validation fails or sync produces errors, code 0 on
                successful dry runs.

        """
        validation = self._product_service.validate_definition()
        if not validation.success:
            console.print(validation.stats.errors)
            raise typer.Exit(code=3)

        console.print(f"Product definition [cyan]{product_path}[/cyan] is correct")
        if is_dry_run:
            raise typer.Exit(code=0)

        product = self._product_service.retrieve().model
        self._confirm(product, force_create=force_create)
        if product is None or force_create:
            with console.status("Create product...") as status:
                self._run_create(status)
        else:
            with console.status("Update product...") as status:
                self._container.resource_id.override(product.id)
                self._run_update(status)

        console.print(stats_table_renderer.render(self._container.stats()))
        if self._container.stats().has_errors:
            raise typer.Exit(code=3)

    def _confirm(self, product: Any, *, force_create: bool) -> None:
        if product is None:
            msg = f"Do you want to create new product for account {self._account_label}"
        elif force_create:
            msg = (
                f"Do you want to create new product for account {self._account_label} "
                f"because the product ID exists in the SWO Platform?"
            )
        else:
            msg = (
                f"Do you want to update product {product.id} ({product.name}) "
                f"for account {self._account_label}? "
                f"To create new use --force-create or -f options."
            )
        typer.confirm(msg, abort=True)

    def _create_parameter_collections(
        self, product_id: str, parameter_group_collection: Any, status: Status
    ) -> DataCollectionModel | None:
        scopes = (
            ("agreement", self._container.agreement_parameters_service()),
            ("asset", self._container.asset_parameters_service()),
            ("item", self._container.item_parameters_service()),
            ("request", self._container.request_parameters_service()),
            ("subscription", self._container.subscription_parameters_service()),
        )
        merged: DataCollectionModel | None = None
        for scope_name, service in scopes:
            status.update(f"Create {scope_name} parameters for product {product_id}...")
            service.set_new_parameter_group(parameter_group_collection)
            scope_collection = service.create().collection
            if merged is None:
                merged = scope_collection
            elif scope_collection is not None:
                merged.add(scope_collection.collection)
        return merged

    def _run_create(self, status: Status) -> None:  # noqa: WPS210,WPS213
        status.update("Create product...")
        result = self._product_service.create()
        if not result.success or result.model is None:
            return

        product = result.model
        self._container.resource_id.override(product.id)
        status.update(f"Create items groups for product {product.id}...")
        item_group_collection = self._container.item_group_service().create().collection

        status.update(f"Create parameters groups for product {product.id}...")
        parameter_group_collection = self._container.parameter_group_service().create().collection

        parameters_collection = self._create_parameter_collections(
            product.id, parameter_group_collection, status
        )
        if parameters_collection is not None:
            status.update(f"Create template parameters for product {product.id}...")
            template_service = self._container.template_service()
            template_service.set_new_parameter_group(parameters_collection)
            template_service.create()

        status.update(f"Create items for product {product.id}...")
        item_service = self._container.item_service()
        item_service.set_new_item_groups(item_group_collection)
        item_service.create()

    def _run_update(self, status: Status) -> None:
        resource_id = self._container.resource_id()
        # NOTE: order cannot be changed to ensure related components are handled before
        # their group.
        update_steps = (
            ("Update product...", self._container.product_service),
            (f"Update item for {resource_id}...", self._container.item_service),
            (
                f"Update items groups for product {resource_id}...",
                self._container.item_group_service,
            ),
            (
                f"Update template for product {resource_id}...",
                self._container.template_service,
            ),
            (
                f"Update parameters groups for product {resource_id}...",
                self._container.parameter_group_service,
            ),
            (
                f"Update agreement parameters for product {resource_id}...",
                self._container.agreement_parameters_service,
            ),
            (
                f"Update asset parameters for product {resource_id}...",
                self._container.asset_parameters_service,
            ),
            (
                f"Update item parameters for product {resource_id}...",
                self._container.item_parameters_service,
            ),
            (
                f"Update request parameters for product {resource_id}...",
                self._container.request_parameters_service,
            ),
            (
                f"Update subscription parameters for product {resource_id}...",
                self._container.subscription_parameters_service,
            ),
        )
        for status_msg, service_factory in update_steps:
            status.update(status_msg)
            service_factory().update()


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
    ProductSyncer(container).sync(product_path, is_dry_run=is_dry_run, force_create=force_create)
