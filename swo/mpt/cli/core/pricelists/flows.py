import enum
from pathlib import Path
from typing import Optional

from rich.console import Console
from swo.mpt.cli.core.accounts.models import Account
from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.handlers.excel_file_handler import ExcelFileHandler
from swo.mpt.cli.core.mpt.client import MPTClient
from swo.mpt.cli.core.mpt.flows import (
    create_pricelist,
    get_pricelist,
    get_pricelist_item,
    update_pricelist,
    update_pricelist_item,
)
from swo.mpt.cli.core.mpt.models import Pricelist
from swo.mpt.cli.core.pricelists.constants import (
    GENERAL_FIELDS,
    GENERAL_PRICELIST_ID,
    PRICELIST_ITEMS_ACTION,
    PRICELIST_ITEMS_FIELDS,
    PRICELIST_ITEMS_ID,
    PRICELIST_ITEMS_ITEM_VENDOR_ID,
    TAB_GENERAL,
    TAB_PRICE_ITEMS,
)
from swo.mpt.cli.core.pricelists.to_json import (
    to_operations_priceitem_json,
    to_operations_pricelist_json,
    to_vendor_priceitem_json,
    to_vendor_pricelist_json,
)
from swo.mpt.cli.core.stats import PricelistStatsCollector
from swo.mpt.cli.core.utils import (
    add_or_create_error,
    status_step_text,
)


class PricelistAction(enum.Enum):
    CREATE = "create"
    UPDATE = "update"


class PricelistItemAction(enum.Enum):
    SKIP = "-"
    SKIPPED = ""
    UPDATE = "update"


def check_pricelist(mpt_client: MPTClient, file_path) -> Pricelist | None:
    file_handler = ExcelFileHandler(file_path)
    general_values = file_handler.get_data_from_vertical_sheet(TAB_GENERAL, GENERAL_FIELDS)
    pricelist_id = general_values[GENERAL_PRICELIST_ID]["value"]
    try:
        pricelist = get_pricelist(mpt_client, pricelist_id)
    except MPTAPIError:
        pricelist = None

    return pricelist


def sync_pricelist(
    mpt_client: MPTClient,
    file_path: Path,
    action: PricelistAction,
    active_account: Account,
    stats: PricelistStatsCollector,
    console: Console,
) -> tuple[PricelistStatsCollector, Optional[Pricelist]]:
    file_handler = ExcelFileHandler(file_path)
    with console.status("Sync Pricelist..."):
        general_data = file_handler.get_data_from_vertical_sheet(TAB_GENERAL, GENERAL_FIELDS)
        if active_account.is_operations():
            pricelist_json = to_operations_pricelist_json(general_data)
        else:
            pricelist_json = to_vendor_pricelist_json(general_data)

        try:
            if action == PricelistAction.CREATE:
                pricelist = create_pricelist(mpt_client, pricelist_json)
            else:
                pricelist_id = general_data[GENERAL_PRICELIST_ID]["value"]
                pricelist = update_pricelist(mpt_client, pricelist_id, pricelist_json)
        except Exception as e:
            add_or_create_error(file_handler, TAB_GENERAL, general_data, e)
            stats.add_error(TAB_GENERAL)
            return stats, None

    pricelist_data = general_data[GENERAL_PRICELIST_ID]
    file_handler.write([{TAB_GENERAL: {pricelist_data["coordinate"]: pricelist.id}}])
    stats.add_synced(TAB_GENERAL)

    stats = sync_pricelist_items(
        mpt_client,
        file_path,
        pricelist.id,
        active_account,
        stats,
        console,
    )

    return stats, pricelist


def sync_pricelist_items(
    mpt_client: MPTClient,
    file_path: Path,
    pricelist_id: str,
    active_account: Account,
    stats: PricelistStatsCollector,
    console: Console,
) -> PricelistStatsCollector:
    with console.status("Sync Pricelist Items...") as status:
        file_handler = ExcelFileHandler(file_path)
        sheet_name = TAB_PRICE_ITEMS
        for row in file_handler.get_data_from_horizontal_sheet(sheet_name, PRICELIST_ITEMS_FIELDS):
            try:
                action = PricelistItemAction(row[PRICELIST_ITEMS_ACTION]["value"])

                if action != PricelistItemAction.UPDATE:
                    stats.add_skipped(sheet_name)
                    continue

                vendor_id = row[PRICELIST_ITEMS_ITEM_VENDOR_ID]["value"]
                pricelist_item = get_pricelist_item(mpt_client, pricelist_id, vendor_id)
                if active_account.is_operations():
                    pricelist_item_json = to_operations_priceitem_json(row)
                else:
                    pricelist_item_json = to_vendor_priceitem_json(row)

                pricelist_item = update_pricelist_item(
                    mpt_client, pricelist_id, pricelist_item.id, pricelist_item_json
                )

                index_id = row[PRICELIST_ITEMS_ID]["coordinate"]
                file_handler.write([{sheet_name: {index_id: pricelist_item.id}}])
                stats.add_synced(sheet_name)
            except Exception as e:
                add_or_create_error(file_handler, sheet_name, row, e)
                stats.add_error(sheet_name)
            finally:
                step_text = status_step_text(stats, sheet_name)
                status.update(f"Syncing {sheet_name}: {step_text}")

    return stats
