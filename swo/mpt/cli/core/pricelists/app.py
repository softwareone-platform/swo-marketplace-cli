from glob import glob
from pathlib import Path
from typing import Annotated

import typer
from openpyxl import load_workbook  # type: ignore
from rich import box
from rich.table import Table
from swo.mpt.cli.core.accounts.app import get_active_account
from swo.mpt.cli.core.console import console
from swo.mpt.cli.core.mpt.client import client_from_account
from swo.mpt.cli.core.mpt.models import Pricelist
from swo.mpt.cli.core.pricelists.flows import (
    PricelistAction,
    check_pricelist,
    sync_pricelist,
)
from swo.mpt.cli.core.stats import PricelistStatsCollector

app = typer.Typer()


@app.command(name="sync")
def sync_pricelists(
    pricelists_paths: Annotated[
        list[str],
        typer.Argument(
            help="Path to Price lists definition files", metavar="PRICELISTS-PATHS"
        ),
    ],
):
    with console.status("Fetching pricelist files..."):
        file_paths = []
        for pricelist_path in pricelists_paths:
            path = Path(pricelist_path)

            if path.is_file():
                file_paths.append(pricelist_path)
            elif path.is_dir():
                file_paths.extend(glob(str(path / "*")))
            else:
                file_paths.extend(glob(pricelist_path))

        file_paths = list(filter(lambda p: p.endswith(".xlsx"), file_paths))

    if not len(file_paths):
        console.print(
            f"No files found for provided paths {', '.join(pricelists_paths)}"
        )
        raise typer.Exit(code=3)

    _ = typer.confirm(
        f"Do you want to sync {len(file_paths)} pricelists files?",
        abort=True,
    )

    active_account = get_active_account()
    mpt_client = client_from_account(active_account)

    has_error = False
    for file_path in file_paths:
        wb = load_workbook(filename=file_path)

        pricelist = check_pricelist(mpt_client, wb)
        if pricelist:
            _ = typer.confirm(
                f"Do you want to update {pricelist.id} for "
                f"account {active_account.id} ({active_account.name})?",
                abort=True,
            )
            action = PricelistAction.UPDATE
        else:
            _ = typer.confirm(
                f"Do you want to create new pricelist from file {file_path} for "
                f"account {active_account.id} ({active_account.name})?",
                abort=True,
            )
            action = PricelistAction.CREATE

        stats = PricelistStatsCollector()
        stats, pricelist = sync_pricelist(
            mpt_client,
            wb,
            action,
            active_account,
            stats,
            console,
        )

        has_error = has_error or stats.is_error

        if pricelist:
            pricelist_table = _pricelist_stats_table(pricelist, stats)
            pricelist_table = _list_pricelist_stats(pricelist_table, stats)

            console.print(pricelist_table)
        else:
            console.print("Pricelist sync [red bold]FAILED")

        wb.save(file_path)

    if has_error:
        raise typer.Exit(code=4)


def _pricelist_stats_table(
    pricelist: Pricelist, stats: PricelistStatsCollector
) -> Table:
    if stats.is_error:
        title = "Pricelist sync [red bold]FAILED"
    else:
        title = f"Pricelist {pricelist.id} sync [green bold]SUCCEED"

    table = Table(title, box=box.ROUNDED)

    table.add_column("Total")
    table.add_column("Synced")
    table.add_column("Errors")
    table.add_column("Skipped")

    return table


def _list_pricelist_stats(table: Table, stats: PricelistStatsCollector) -> Table:
    for tab_name, tab_stats in stats.tabs.items():
        table.add_row(
            tab_name,
            f"[blue]{tab_stats["total"]}",
            f"[green]{tab_stats["synced"]}",
            f"[red bold]{tab_stats["error"]}",
            f"[white]{tab_stats["skipped"]}",
        )

    return table


if __name__ == "__main__":
    app()
