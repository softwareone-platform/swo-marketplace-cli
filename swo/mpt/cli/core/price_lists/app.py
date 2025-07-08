import os
from pathlib import Path
from typing import Annotated

import typer
from swo.mpt.cli.core.accounts.app import get_active_account
from swo.mpt.cli.core.console import console
from swo.mpt.cli.core.mpt.client import client_from_account
from swo.mpt.cli.core.price_lists.api import PriceListAPIService
from swo.mpt.cli.core.price_lists.api.price_list_item_api_service import PriceListItemAPIService
from swo.mpt.cli.core.price_lists.handlers import (
    PriceListExcelFileManager,
    PriceListItemExcelFileManager,
)
from swo.mpt.cli.core.price_lists.models import ItemData, PriceListData
from swo.mpt.cli.core.price_lists.services import ItemService, PriceListService
from swo.mpt.cli.core.services.service_context import ServiceContext
from swo.mpt.cli.core.stats import PriceListStatsCollector
from swo.mpt.cli.core.utils import get_files_path

app = typer.Typer()


@app.command(name="sync")
def sync_price_lists(
    pricelists_paths: Annotated[
        list[str],
        typer.Argument(help="Path to Price lists definition files", metavar="PRICELISTS-PATHS"),
    ],
):
    with console.status("Fetching price list files..."):
        file_paths = get_files_path(pricelists_paths)

    if not len(file_paths):
        console.print(f"No files found for provided paths {', '.join(pricelists_paths)}")
        raise typer.Exit(code=3)

    _ = typer.confirm(
        f"Do you want to sync {len(file_paths)} price_lists files?",
        abort=True,
    )

    active_account = get_active_account()
    mpt_client = client_from_account(active_account)
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
        price_list = price_list_service.retrieve().model
        if price_list is None:
            _ = typer.confirm(
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
            _ = typer.confirm(
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

        stats.id = price_list.id
        console.print(stats.to_table())

    if has_error:
        console.print("Price list sync [red bold]FAILED")
        raise typer.Exit(code=4)


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
    active_account = get_active_account()
    if not active_account.is_operations():
        console.print(
            f"Current active account {active_account.id} ({active_account.name}) is not "
            f"allowed for the export command. Please, activate an operation account."
        )
        raise typer.Exit(code=4)

    out_path = out_path if out_path is not None else os.getcwd()
    mpt_client = client_from_account(active_account)
    stats = PriceListStatsCollector()
    has_error = False
    for price_list_id in price_list_ids:
        file_path = Path(out_path) / f"{price_list_id}.xlsx"
        if file_path.exists():
            overwrite = typer.confirm(
                f"File {file_path} already exists. Do you want to overwrite it?",
                abort=False,
            )
            if not overwrite:
                console.print(f"Skipped export for {price_list_id}.")
                continue
            os.remove(file_path)
        else:
            _ = typer.confirm(
                f"Do you want to export {price_list_id} in {out_path}?",
                abort=True,
            )

        price_list_service_context = ServiceContext(
            account=active_account,
            api=PriceListAPIService(mpt_client),
            data_model=PriceListData,
            file_manager=PriceListExcelFileManager(str(file_path)),
            stats=stats,
        )
        result = PriceListService(price_list_service_context).export(resource_id=price_list_id)
        if not result.success:
            console.print(f"Failed to export price list with id: {price_list_id}")
            console.print(result.errors)
            has_error = True
            continue

        item_service_context = ServiceContext(
            account=active_account,
            api=PriceListItemAPIService(mpt_client, price_list_id),
            data_model=ItemData,
            file_manager=PriceListItemExcelFileManager(str(file_path)),
            stats=stats,
        )
        result = ItemService(item_service_context).export()
        if not result.success:
            console.print(f"Failed to export price list items for id: {price_list_id}")
            has_error = True
            continue

        console.print(f"Price list with id: {price_list_id} has been exported into {file_path}")

    if has_error:
        console.print("Price list export [red bold]FAILED")
        raise typer.Exit(code=4)


if __name__ == "__main__":
    app()
