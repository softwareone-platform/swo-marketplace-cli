from typing import Annotated

import typer
from cli.core.accounts.app import get_active_account
from cli.core.console import console
from cli.core.console.renderers.stats import StatsTableRenderer
from cli.core.file_discovery import get_files_path
from cli.core.mpt.mpt_client import create_api_mpt_client_from_account
from cli.core.price_lists.api import PriceListAPIService, PriceListItemAPIService
from cli.core.price_lists.handlers import PriceListExcelFileManager, PriceListItemExcelFileManager
from cli.core.price_lists.models import ItemData, PriceListData
from cli.core.price_lists.services import ItemService, PriceListService
from cli.core.services.service_context import ServiceContext
from cli.core.stats import PriceListStatsCollector

app = typer.Typer()
stats_table_renderer = StatsTableRenderer()


class PriceListSyncer:
    """Coordinate the CLI-driven sync of one or more price list definition files."""

    def __init__(self) -> None:
        account = get_active_account()
        self._account = account
        self._account_label = f"{account.id} ({account.name})"
        self._mpt_client = create_api_mpt_client_from_account(account)
        self._stats = PriceListStatsCollector()

    def sync_all(self, file_paths: list[str]) -> None:
        """Sync every file; raise ``typer.Exit`` if any file failed."""
        outcomes = [self.sync_one(file_path) for file_path in file_paths]
        if not all(outcomes):
            console.print("Price list sync [red bold]FAILED")
            raise typer.Exit(code=4)

    def sync_one(self, file_path: str) -> bool:
        """Sync a single price list definition file.

        Returns True on success, False if any step failed.
        """
        service_context = ServiceContext(
            account=self._account,
            api=PriceListAPIService(self._mpt_client),
            data_model=PriceListData,
            file_manager=PriceListExcelFileManager(file_path),
            stats=self._stats,
        )
        price_list_service = PriceListService(service_context)
        result = price_list_service.retrieve()
        if not result.success:
            return False

        price_list = result.model
        if price_list is None:
            typer.confirm(
                f"Do you want to create new price list from file {file_path} "
                f"for account {self._account_label}?",
                abort=True,
            )
            with console.status("Create Price list..."):
                result = price_list_service.create()
            if not result.success or result.model is None:
                return False
            price_list = result.model
        else:
            typer.confirm(
                f"Do you want to update {price_list.id} for account {self._account_label}?",
                abort=True,
            )
            with console.status("Sync Price list..."):
                result = price_list_service.update()
            if not result.success:
                return False

        items_service = ItemService(
            ServiceContext(
                account=self._account,
                api=PriceListItemAPIService(self._mpt_client, price_list_id=price_list.id),
                data_model=ItemData,
                file_manager=PriceListItemExcelFileManager(file_path),
                stats=self._stats,
            )
        )
        with console.status("Sync Price list Items..."):
            result = items_service.update()

        self._stats.stat_id = price_list.id
        console.print(stats_table_renderer.render(self._stats))
        return result.success


@app.command(name="sync")
def sync_price_lists(
    pricelists_paths: Annotated[
        list[str],
        typer.Argument(help="Path to Price lists definition files", metavar="PRICELISTS-PATHS"),
    ],
):
    """Sync price lists to the environment from Excel definition files.

    Args:
        pricelists_paths: List of paths to price list definition files to sync.

    Raises:
        typer.Exit: With code 3 if no files found, code 4 if sync fails.

    """
    with console.status("Fetching price list files..."):
        file_paths = get_files_path(pricelists_paths)

    if not len(file_paths):
        console.print("No files found for provided paths", ", ".join(pricelists_paths))
        raise typer.Exit(code=3)

    typer.confirm(
        f"Do you want to sync {len(file_paths)} price_lists files?",
        abort=True,
    )

    PriceListSyncer().sync_all(file_paths)
