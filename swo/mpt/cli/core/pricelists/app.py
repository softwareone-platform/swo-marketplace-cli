from typing import Annotated

import typer
from swo.mpt.cli.core.accounts.app import get_active_account
from swo.mpt.cli.core.console import console
from swo.mpt.cli.core.mpt.client import client_from_account
from swo.mpt.cli.core.pricelists.api import PriceListAPIService
from swo.mpt.cli.core.pricelists.api.price_list_item_api_service import PriceListItemAPIService
from swo.mpt.cli.core.pricelists.handlers import PriceListItemExcelFileHandler
from swo.mpt.cli.core.pricelists.handlers.price_list_excel_file_handler import (
    PriceListExcelFileHandler,
)
from swo.mpt.cli.core.pricelists.models import PriceListData
from swo.mpt.cli.core.pricelists.services import ItemService, PriceListService
from swo.mpt.cli.core.products.models import ItemData
from swo.mpt.cli.core.services.service_context import ServiceContext
from swo.mpt.cli.core.stats import PricelistStatsCollector
from swo.mpt.cli.core.utils import get_files_path

app = typer.Typer()


@app.command(name="sync")
def sync_pricelists(
    pricelists_paths: Annotated[
        list[str],
        typer.Argument(help="Path to Price lists definition files", metavar="PRICELISTS-PATHS"),
    ],
):
    with console.status("Fetching pricelist files..."):
        file_paths = get_files_path(pricelists_paths)

    if not len(file_paths):
        console.print(f"No files found for provided paths {', '.join(pricelists_paths)}")
        raise typer.Exit(code=3)

    _ = typer.confirm(
        f"Do you want to sync {len(file_paths)} pricelists files?",
        abort=True,
    )

    active_account = get_active_account()
    mpt_client = client_from_account(active_account)
    stats = PricelistStatsCollector()
    has_error = False
    for file_path in file_paths:
        service_context = ServiceContext(
            account=active_account,
            api=PriceListAPIService(mpt_client),
            data_model=PriceListData,
            file_handler=PriceListExcelFileHandler(file_path),
            stats=stats,
        )
        price_list_service = PriceListService(service_context)
        price_list = price_list_service.retrieve().model
        if price_list is None:
            _ = typer.confirm(
                f"Do you want to create new pricelist from file {file_path} for "
                f"account {active_account.id} ({active_account.name})?",
                abort=True,
            )
            with console.status("Create Pricelist..."):
                result = price_list_service.create()
                if not result.success or result.model is None:
                    has_error = True
                    continue

                price_list = result.model
        else:
            _ = typer.confirm(
                f"Do you want to update {price_list.id} for "
                f"account {active_account.id} ({active_account.name})?",
                abort=True,
            )
            with console.status("Sync Pricelist..."):
                result = price_list_service.update(price_list.id)

        if not result.success:
            has_error = True
            continue

        price_list_item_service = ItemService(
            ServiceContext(
                account=active_account,
                api=PriceListItemAPIService(mpt_client, price_list_id=price_list.id),
                data_model=ItemData,
                file_handler=PriceListItemExcelFileHandler(file_path),
                stats=stats,
            )
        )
        with console.status("Sync Pricelist Items..."):
            result = price_list_item_service.update(price_list.id)

        stats.pricelist_id = price_list.id
        console.print(stats.to_table())

    if has_error:
        console.print("Pricelist sync [red bold]FAILED")
        raise typer.Exit(code=4)


if __name__ == "__main__":
    app()
