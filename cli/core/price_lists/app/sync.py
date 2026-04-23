from typing import Annotated

import typer
from cli.core.accounts.app import get_active_account
from cli.core.accounts.models import Account
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
from mpt_api_client import MPTClient

app = typer.Typer()
stats_table_renderer = StatsTableRenderer()


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
    file_paths = _get_file_paths(pricelists_paths)
    typer.confirm(
        f"Do you want to sync {len(file_paths)} price_lists files?",
        abort=True,
    )

    active_account = get_active_account()
    mpt_client = create_api_mpt_client_from_account(active_account)
    stats = PriceListStatsCollector()
    has_error = False
    for file_path in file_paths:
        if not _sync_price_list_file(active_account, file_path, mpt_client, stats):
            has_error = True

    if has_error:
        console.print("Price list sync [red bold]FAILED")
        raise typer.Exit(code=4)


def _create_price_list(
    active_account: Account, file_path: str, price_list_service: PriceListService
):
    typer.confirm(
        f"Do you want to create new price list from file {file_path} for "
        f"account {active_account.id} ({active_account.name})?",
        abort=True,
    )
    with console.status("Create Price list..."):
        return price_list_service.create()


def _get_file_paths(pricelists_paths: list[str]) -> list[str]:
    with console.status("Fetching price list files..."):
        file_paths = get_files_path(pricelists_paths)

    if file_paths:
        return file_paths

    provided_paths = ", ".join(pricelists_paths)
    console.print(f"No files found for provided paths {provided_paths}")
    raise typer.Exit(code=3)


def _sync_price_list_items(
    active_account: Account,
    file_path: str,
    mpt_client: MPTClient,
    price_list_id: str,
    stats: PriceListStatsCollector,
) -> bool:
    with console.status("Sync Price list Items..."):
        result = ItemService(
            ServiceContext(
                account=active_account,
                api=PriceListItemAPIService(mpt_client, price_list_id=price_list_id),
                data_model=ItemData,
                file_manager=PriceListItemExcelFileManager(file_path),
                stats=stats,
            )
        ).update()
    return result.success


def _sync_price_list_file(
    active_account: Account,
    file_path: str,
    mpt_client: MPTClient,
    stats: PriceListStatsCollector,
) -> bool:
    price_list_service = PriceListService(
        ServiceContext(
            account=active_account,
            api=PriceListAPIService(mpt_client),
            data_model=PriceListData,
            file_manager=PriceListExcelFileManager(file_path),
            stats=stats,
        )
    )
    result = price_list_service.retrieve()
    if not result.success:
        return False

    price_list = result.model
    if price_list is None:
        result = _create_price_list(active_account, file_path, price_list_service)
    else:
        result = _update_price_list(active_account, price_list, price_list_service)

    if not result.success or result.model is None:
        return False

    if not _sync_price_list_items(active_account, file_path, mpt_client, result.model.id, stats):
        return False

    stats.stat_id = result.model.id
    console.print(stats_table_renderer.render(stats))
    return True


def _update_price_list(
    active_account: Account, price_list: PriceListData, price_list_service: PriceListService
):
    typer.confirm(
        f"Do you want to update {price_list.id} for "
        f"account {active_account.id} ({active_account.name})?",
        abort=True,
    )
    with console.status("Sync Price list..."):
        return price_list_service.update()
