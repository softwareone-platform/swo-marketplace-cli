from pathlib import Path
from typing import Annotated

import typer
from cli.core.accounts.app import get_active_account
from cli.core.console import console
from cli.core.mpt.mpt_client import create_api_mpt_client_from_account
from cli.core.price_lists.api import PriceListAPIService, PriceListItemAPIService
from cli.core.price_lists.handlers import PriceListExcelFileManager, PriceListItemExcelFileManager
from cli.core.price_lists.models import ItemData, PriceListData
from cli.core.price_lists.services import ItemService, PriceListService
from cli.core.services.service_context import ServiceContext
from cli.core.stats import PriceListStatsCollector

app = typer.Typer()


class PriceListExporter:
    """Coordinate the CLI-driven export of one or more price lists."""

    def __init__(self, out_path: str | None) -> None:
        account = get_active_account()
        self._account = account
        self._account_label = f"{account.id} ({account.name})"
        if not account.is_operations():
            console.print(
                f"Current active account {self._account_label} is not allowed "
                f"for the export command. Please, activate an operation account."
            )
            raise typer.Exit(code=4)
        self._out_dir = str(Path.cwd()) if out_path is None else out_path
        self._mpt_client = create_api_mpt_client_from_account(account)
        self._stats = PriceListStatsCollector()

    def export_all(self, price_list_ids: list[str]) -> None:
        """Export every id; raise ``typer.Exit`` if any export failed."""
        outcomes = [self.export_one(price_list_id) for price_list_id in price_list_ids]
        if any(outcome is False for outcome in outcomes):
            console.print("Price list export [red bold]FAILED")
            raise typer.Exit(code=4)

    def export_one(self, price_list_id: str) -> bool | None:
        """Export a single price list.

        Writes the workbook to a temporary file first so a failed export does
        not destroy the previous valid workbook on disk.

        Returns True on success, False on failure, None if the user skipped.
        """
        file_path = Path(self._out_dir) / f"{price_list_id}.xlsx"
        if file_path.exists():
            if not typer.confirm(
                f"File {file_path} already exists. Do you want to overwrite it?",
                abort=False,
            ):
                console.print(f"Skipped export for {price_list_id}.")
                return None
        else:
            typer.confirm(
                f"Do you want to export {price_list_id} in {self._out_dir}?",
                abort=True,
            )

        temp_path = file_path.with_name(f"{file_path.name}.tmp")
        temp_path.unlink(missing_ok=True)
        if not self._export_workbook(price_list_id, temp_path):
            return False

        temp_path.replace(file_path)
        console.print(f"Price list with id: {price_list_id} has been exported into {file_path}")
        return True

    def _export_workbook(self, price_list_id: str, target_path: Path) -> bool:
        """Run the price list and item service exports against ``target_path``.

        Removes ``target_path`` on failure so a stale temp file is not left behind.
        """
        price_list_context = ServiceContext(
            account=self._account,
            api=PriceListAPIService(self._mpt_client),
            data_model=PriceListData,
            file_manager=PriceListExcelFileManager(str(target_path)),
            stats=self._stats,
        )
        result = PriceListService(price_list_context).export(resource_id=price_list_id)
        if not result.success:
            target_path.unlink(missing_ok=True)
            console.print(f"Failed to export price list with id: {price_list_id}", result.errors)
            return False

        item_context = ServiceContext(
            account=self._account,
            api=PriceListItemAPIService(self._mpt_client, price_list_id),
            data_model=ItemData,
            file_manager=PriceListItemExcelFileManager(str(target_path)),
            stats=self._stats,
        )
        result = ItemService(item_context).export()
        if not result.success:
            target_path.unlink(missing_ok=True)
            console.print(f"Failed to export price list items for id: {price_list_id}")
            return False

        return True


@app.command("export")
def export(
    price_list_ids: Annotated[
        list[str],
        typer.Argument(help="List of price lists IDs to export"),
    ],
    out_path: Annotated[
        str | None,
        typer.Option(
            "--out",
            "-o",
            help="Specify folder to export price lists to. Default filename is <pricelist-id>.xlsx",
        ),
    ] = None,
):
    """Export price lists to Excel files.

    Args:
        price_list_ids: List of price list IDs to export.
        out_path: Output directory path. Defaults to current working directory.

    Raises:
        typer.Exit: With code 4 if account is not operations or export fails.

    """
    PriceListExporter(out_path).export_all(price_list_ids)
