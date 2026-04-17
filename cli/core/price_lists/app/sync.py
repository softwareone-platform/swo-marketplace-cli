from typing import Annotated

import typer
from cli.core.accounts.app import get_active_account
from cli.core.console import console
from cli.core.file_discovery import get_files_path
from cli.core.mpt.mpt_client import create_api_mpt_client_from_account
from cli.core.price_lists.api import PriceListAPIService, PriceListItemAPIService
from cli.core.price_lists.handlers import PriceListExcelFileManager, PriceListItemExcelFileManager
from cli.core.price_lists.models import ItemData, PriceListData
from cli.core.price_lists.services import ItemService, PriceListService
from cli.core.services.service_context import ServiceContext
from cli.core.stats import PriceListStatsCollector

app = typer.Typer()


@app.command(name="sync")
def sync_price_lists(  # noqa: C901
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
        console.print(f"No files found for provided paths {', '.join(pricelists_paths)}")
        raise typer.Exit(code=3)

    typer.confirm(
        f"Do you want to sync {len(file_paths)} price_lists files?",
        abort=True,
    )

    active_account = get_active_account()
    mpt_client = create_api_mpt_client_from_account(active_account)
    stats = PriceListStatsCollector()
    has_error = False
    for file_path in file_paths:
        service_context = ServiceContext(
            account=active_account,
            api=PriceListAPIService(mpt_client),
            data_model=PriceListData,
            file_manager=PriceListExcelFileManager(file_path),
            stats=stats,
        )
        price_list_service = PriceListService(service_context)
        result = price_list_service.retrieve()
        if not result.success:
            has_error = True
            continue

        price_list = result.model
        if price_list is None:
            typer.confirm(
                f"Do you want to create new price list from file {file_path} for "
                f"account {active_account.id} ({active_account.name})?",
                abort=True,
            )
            with console.status("Create Price list..."):
                result = price_list_service.create()
                if not result.success or result.model is None:
                    has_error = True
                    continue

                price_list = result.model
        else:
            typer.confirm(
                f"Do you want to update {price_list.id} for "
                f"account {active_account.id} ({active_account.name})?",
                abort=True,
            )
            with console.status("Sync Price list..."):
                result = price_list_service.update()

        if not result.success:
            has_error = True
            continue

        price_list_item_service = ItemService(
            ServiceContext(
                account=active_account,
                api=PriceListItemAPIService(mpt_client, price_list_id=price_list.id),
                data_model=ItemData,
                file_manager=PriceListItemExcelFileManager(file_path),
                stats=stats,
            )
        )
        with console.status("Sync Price list Items..."):
            result = price_list_item_service.update()
            if not result.success:
                has_error = True

        stats.stat_id = price_list.id
        console.print(stats.to_table())

    if has_error:
        console.print("Price list sync [red bold]FAILED")
        raise typer.Exit(code=4)
