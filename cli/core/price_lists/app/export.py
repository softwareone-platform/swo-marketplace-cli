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


@app.command("export")
def export(  # noqa: C901
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
    active_account = get_active_account()
    if not active_account.is_operations():
        console.print(
            f"Current active account {active_account.id} ({active_account.name}) is not "
            f"allowed for the export command. Please, activate an operation account."
        )
        raise typer.Exit(code=4)

    out_path = str(Path.cwd()) if out_path is None else out_path
    mpt_client = create_api_mpt_client_from_account(active_account)
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
            Path(file_path).unlink()
        else:
            typer.confirm(
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
