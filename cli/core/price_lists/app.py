from pathlib import Path
from typing import Annotated

import typer
from cli.core.accounts.app import get_active_account
from cli.core.console import console
from cli.core.file_discovery import get_files_path
from cli.core.mpt.mpt_client import create_api_mpt_client_from_account
from cli.core.price_lists.api import PriceListAPIService
from cli.core.price_lists.api.price_list_item_api_service import PriceListItemAPIService
from cli.core.price_lists.handlers import (
    PriceListExcelFileManager,
    PriceListItemExcelFileManager,
)
from cli.core.price_lists.models import ItemData, PriceListData
from cli.core.price_lists.services import ItemService, PriceListService
from cli.core.services.service_context import ServiceContext
from cli.core.stats import PriceListStatsCollector

app = typer.Typer()


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
        console.print(f"No files found for provided paths {', '.join(pricelists_paths)}")
        raise typer.Exit(code=3)

    typer.confirm(
        f"Do you want to sync {len(file_paths)} price_lists files?",
        abort=True,
    )

    if not _PriceListOps.sync_files(file_paths):
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

    if not _PriceListOps.export_lists(active_account, price_list_ids, out_path):
        console.print("Price list export [red bold]FAILED")
        raise typer.Exit(code=4)


class _PriceListOps:
    @classmethod
    def export_lists(cls, active_account, price_list_ids: list[str], out_path: str | None) -> bool:
        output_path = str(Path.cwd()) if out_path is None else out_path
        mpt_client = create_api_mpt_client_from_account(active_account)
        stats = PriceListStatsCollector()
        has_error = False
        for price_list_id in price_list_ids:
            has_error = has_error or not cls.export_price_list(
                active_account=active_account,
                mpt_client=mpt_client,
                out_path=output_path,
                price_list_id=price_list_id,
                stats=stats,
            )
        return not has_error

    @classmethod
    def export_price_list(
        cls,
        active_account,
        mpt_client,
        out_path: str,
        price_list_id: str,
        stats: PriceListStatsCollector,
    ) -> bool:
        file_path = Path(out_path) / f"{price_list_id}.xlsx"
        if not cls.prepare_export_path(file_path, out_path, price_list_id):
            return True
        result = cls.export_price_list_data(
            active_account, mpt_client, price_list_id, file_path, stats
        )
        if not result.success:
            console.print(f"Failed to export price list with id: {price_list_id}")
            console.print(result.errors)
            return False

        result = cls.export_price_list_items(
            active_account, mpt_client, price_list_id, file_path, stats
        )
        if not result.success:
            console.print(f"Failed to export price list items for id: {price_list_id}")
            return False
        console.print(f"Price list with id: {price_list_id} has been exported into {file_path}")
        return True

    @classmethod
    def export_price_list_data(
        cls,
        active_account,
        mpt_client,
        price_list_id: str,
        file_path: Path,
        stats: PriceListStatsCollector,
    ):
        return PriceListService(
            ServiceContext(
                account=active_account,
                api=PriceListAPIService(mpt_client),
                data_model=PriceListData,
                file_manager=PriceListExcelFileManager(str(file_path)),
                stats=stats,
            )
        ).export(resource_id=price_list_id)

    @classmethod
    def export_price_list_items(
        cls,
        active_account,
        mpt_client,
        price_list_id: str,
        file_path: Path,
        stats: PriceListStatsCollector,
    ):
        return ItemService(
            ServiceContext(
                account=active_account,
                api=PriceListItemAPIService(mpt_client, price_list_id),
                data_model=ItemData,
                file_manager=PriceListItemExcelFileManager(str(file_path)),
                stats=stats,
            )
        ).export()

    @classmethod
    def prepare_export_path(cls, file_path: Path, out_path: str, price_list_id: str) -> bool:
        if file_path.exists():
            overwrite = typer.confirm(
                f"File {file_path} already exists. Do you want to overwrite it?",
                abort=False,
            )
            if not overwrite:
                console.print(f"Skipped export for {price_list_id}.")
                return False
            file_path.unlink()
            return True
        typer.confirm(
            f"Do you want to export {price_list_id} in {out_path}?",
            abort=True,
        )
        return True

    @classmethod
    def sync_file(
        cls,
        active_account,
        file_path: str,
        mpt_client,
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
        result, price_list_id = cls.sync_price_list_model(
            price_list_service, active_account, file_path
        )
        if not result.success:
            return False

        with console.status("Sync Price list Items..."):
            item_result = ItemService(
                ServiceContext(
                    account=active_account,
                    api=PriceListItemAPIService(mpt_client, price_list_id=price_list_id),
                    data_model=ItemData,
                    file_manager=PriceListItemExcelFileManager(file_path),
                    stats=stats,
                )
            ).update()
        stats.stat_id = price_list_id
        console.print(stats.to_table())
        return item_result.success

    @classmethod
    def sync_files(cls, file_paths: list[str]) -> bool:
        active_account = get_active_account()
        mpt_client = create_api_mpt_client_from_account(active_account)
        stats = PriceListStatsCollector()
        has_error = False
        for file_path in file_paths:
            has_error = has_error or not cls.sync_file(
                active_account=active_account,
                file_path=file_path,
                mpt_client=mpt_client,
                stats=stats,
            )
        return not has_error

    @classmethod
    def sync_price_list_model(
        cls, price_list_service: PriceListService, active_account, file_path: str
    ):
        price_list = price_list_service.retrieve().model
        if price_list is None:
            typer.confirm(
                f"Do you want to create new price list from file {file_path} for "
                f"account {active_account.id} ({active_account.name})?",
                abort=True,
            )
            with console.status("Create Price list..."):
                create_result = price_list_service.create()
            if create_result.model is None:
                return create_result, ""
            return create_result, create_result.model.id

        typer.confirm(
            f"Do you want to update {price_list.id} for "
            f"account {active_account.id} ({active_account.name})?",
            abort=True,
        )
        with console.status("Sync Price list..."):
            return price_list_service.update(), price_list.id


if __name__ == "__main__":
    app()
