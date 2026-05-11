from pathlib import Path
from typing import Annotated

import typer
from cli.core.accounts.containers import AccountContainer
from cli.core.console import console
from cli.core.products.containers import ProductContainer

app = typer.Typer()


class ProductExporter:
    """Coordinate the CLI-driven export of one or more products."""

    def __init__(self, account_container: AccountContainer, out_path: str | None) -> None:
        self._account_container = account_container
        account = self._account_container.account()
        self._account_label = f"{account.id} ({account.name})"
        if not account.is_operations():
            console.print(
                f"Current active account {self._account_label} is not allowed "
                f"for the export command. Please, activate an operation account."
            )
            raise typer.Exit(code=4)
        self._out_dir = str(Path.cwd()) if out_path is None else out_path

    def export_all(self, product_ids: list[str]) -> None:
        """Export every product id.

        Args:
            product_ids: List of product IDs to export.

        Raises:
            typer.Exit: With code 3 if any single product failed to export.

        """
        outcomes = [self.export_one(product_id) for product_id in product_ids]
        if any(outcome is False for outcome in outcomes):
            raise typer.Exit(code=3)

    def export_one(self, product_id: str) -> bool | None:
        """Export a single product.

        Writes the workbook to a temporary file first so a failed export does not
        destroy the previous valid workbook on disk.

        Args:
            product_id: The product ID to export.

        Returns:
            ``True`` on success, ``False`` on failure, ``None`` if the user
            skipped the overwrite confirmation.

        """
        file_path = Path(self._out_dir) / f"{product_id}.xlsx"
        if file_path.exists():
            if not typer.confirm(
                f"File {file_path} already exists. Do you want to overwrite it?",
                abort=False,
            ):
                console.print(f"Skipped export for {product_id}.")
                return None
        else:
            typer.confirm(
                f"Do you want to export {product_id} in {self._out_dir}?",
                abort=True,
            )

        temp_path = file_path.with_stem(f"{file_path.stem}.tmp")
        temp_path.unlink(missing_ok=True)
        if not self._export_workbook(product_id, temp_path):
            return False

        temp_path.replace(file_path)
        console.print(f"Product with id: {product_id} has been exported into {file_path}")
        return True

    def _export_workbook(self, product_id: str, target_path: Path) -> bool:
        container = ProductContainer(
            account_container=self._account_container,
            file_path=str(target_path),
            resource_id=product_id,
        )
        related_service_factories = (
            container.item_service,
            container.item_group_service,
            container.parameter_group_service,
            container.agreement_parameters_service,
            container.asset_parameters_service,
            container.item_parameters_service,
            container.request_parameters_service,
            container.subscription_parameters_service,
            container.template_service,
        )
        with console.status(f"Exporting product with id: {product_id}..."):
            container.product_service().export(resource_id=product_id)
            for service_factory in related_service_factories:
                service_factory().export()

        if container.stats().has_errors:
            target_path.unlink(missing_ok=True)
            console.print(f"Product export with id: {product_id} [red bold]FAILED")
            return False
        return True


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
            help="Specify folder to export products to. Default filename is <product-id>.xlsx",
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
    ProductExporter(AccountContainer(), out_path).export_all(product_ids)
