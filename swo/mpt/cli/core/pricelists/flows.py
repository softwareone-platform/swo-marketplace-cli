import enum
from typing import Optional

from openpyxl.workbook import Workbook  # type: ignore
from openpyxl.worksheet.worksheet import Worksheet  # type: ignore
from rich.console import Console
from swo.mpt.cli.core.accounts.models import Account
from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.mpt.client import MPTClient
from swo.mpt.cli.core.mpt.flows import (
    create_pricelist,
    get_pricelist,
    get_pricelist_item,
    update_pricelist,
    update_pricelist_item,
)
from swo.mpt.cli.core.mpt.models import Pricelist
from swo.mpt.cli.core.pricelists import constants
from swo.mpt.cli.core.stats import PricelistStatsCollector
from swo.mpt.cli.core.utils import (
    SheetValue,
    add_or_create_error,
    find_value_for,
    get_values_for_general,
    get_values_for_table,
    status_step_text,
)


class PricelistAction(enum.Enum):
    CREATE = "create"
    UPDATE = "update"


class PricelistItemAction(enum.Enum):
    SKIP = "-"
    SKIPPED = ""
    UPDATE = "update"


def check_pricelist(mpt_client: MPTClient, wb: Workbook) -> Pricelist | None:
    ws = wb[constants.TAB_GENERAL]

    values = get_values_for_general(ws, constants.GENERAL_FIELDS)
    pricelist_id = find_value_for(constants.GENERAL_PRICELIST_ID, values)[2]

    try:
        pricelist = get_pricelist(mpt_client, pricelist_id)
    except MPTAPIError:
        pricelist = None

    return pricelist


def to_operations_pricelist_json(values: list[SheetValue]) -> dict:
    pricelist_json = to_vendor_pricelist_json(values)
    pricelist_json["defaultMarkup"] = find_value_for(
        constants.GENERAL_DEFAULT_MARKUP, values
    )[2]

    return pricelist_json


def to_vendor_pricelist_json(values: list[SheetValue]) -> dict:
    return {
        "currency": find_value_for(constants.GENERAL_CURRENCY, values)[2],
        "precision": find_value_for(constants.GENERAL_PRECISION, values)[2],
        "notes": find_value_for(constants.GENERAL_NOTES, values)[2],
        "product": {
            "id": find_value_for(constants.GENERAL_PRODUCT_ID, values)[2],
        },
    }


def sync_pricelist(
    mpt_client: MPTClient,
    wb: Workbook,
    action: PricelistAction,
    active_account: Account,
    stats: PricelistStatsCollector,
    console: Console,
) -> tuple[PricelistStatsCollector, Optional[Pricelist]]:
    with console.status("Sync Pricelist..."):
        general_ws = wb[constants.TAB_GENERAL]
        general_values = get_values_for_general(general_ws, constants.GENERAL_FIELDS)

        if active_account.type == "Operations":
            pricelist_json = to_operations_pricelist_json(general_values)
        else:
            pricelist_json = to_vendor_pricelist_json(general_values)

        try:
            if action == PricelistAction.CREATE:
                pricelist = create_pricelist(
                    mpt_client,
                    pricelist_json,
                )
            else:
                pricelist_id = find_value_for(
                    constants.GENERAL_PRICELIST_ID, general_values
                )[2]
                pricelist = update_pricelist(
                    mpt_client,
                    pricelist_id,
                    pricelist_json,
                )
        except Exception as e:
            add_or_create_error(general_ws, general_values, e)
            stats.add_error(constants.TAB_GENERAL)
            return stats, None

    index, _, _ = find_value_for(constants.GENERAL_PRICELIST_ID, general_values)
    general_ws[index] = pricelist.id
    stats.add_synced(constants.TAB_GENERAL)

    stats = sync_pricelist_items(
        mpt_client,
        wb[constants.TAB_PRICE_ITEMS],
        pricelist.id,
        active_account,
        stats,
        console,
    )

    return stats, pricelist


def to_operations_priceitem_json(values: list[SheetValue]) -> dict:
    status = find_value_for(constants.PRICELIST_ITEMS_STATUS, values)[2]
    priceitem_json = {
        "markup": find_value_for(constants.PRICELIST_ITEMS_MARKUP, values)[2],
        "unitLP": find_value_for(constants.PRICELIST_ITEMS_UNIT_LP, values)[2],
        "unitPP": find_value_for(constants.PRICELIST_ITEMS_UNIT_PP, values)[2],
    }

    unit_sp = find_value_for(constants.PRICELIST_ITEMS_UNIT_SP, values)
    if unit_sp and unit_sp[2] is not None:
        priceitem_json["unitSP"] = unit_sp[2]

    if status != "Draft":
        priceitem_json["status"] = status

    return priceitem_json


def to_vendor_priceitem_json(values: list[SheetValue]) -> dict:
    return {
        "status": find_value_for(constants.PRICELIST_ITEMS_STATUS, values)[2],
        "unitLP": find_value_for(constants.PRICELIST_ITEMS_UNIT_LP, values)[2],
        "unitPP": find_value_for(constants.PRICELIST_ITEMS_UNIT_PP, values)[2],
    }


def sync_pricelist_items(
    mpt_client: MPTClient,
    ws: Worksheet,
    pricelist_id: str,
    active_account: Account,
    stats: PricelistStatsCollector,
    console: Console,
) -> PricelistStatsCollector:
    with console.status("Sync Pricelist Items...") as status:
        values = get_values_for_table(ws, constants.PRICELIST_ITEMS_FIELDS)

        for sheet_value in values:
            try:
                action = PricelistItemAction(
                    find_value_for(constants.PRICELIST_ITEMS_ACTION, sheet_value)[2]
                )

                if action != PricelistItemAction.UPDATE:
                    stats.add_skipped(constants.TAB_PRICE_ITEMS)
                    continue

                vendor_id = find_value_for(
                    constants.PRICELIST_ITEMS_ITEM_VENDOR_ID, sheet_value
                )[2]
                pricelist_item = get_pricelist_item(mpt_client, pricelist_id, vendor_id)

                if active_account.type == "Operations":
                    pricelist_item_json = to_operations_priceitem_json(sheet_value)
                else:
                    pricelist_item_json = to_vendor_priceitem_json(sheet_value)

                pricelist_item = update_pricelist_item(
                    mpt_client, pricelist_id, pricelist_item.id, pricelist_item_json
                )

                index_id, _, _ = find_value_for(
                    constants.PRICELIST_ITEMS_ID, sheet_value
                )
                ws[index_id] = pricelist_item.id
                stats.add_synced(constants.TAB_PRICE_ITEMS)
            except Exception as e:
                add_or_create_error(ws, sheet_value, e)
                stats.add_error(constants.TAB_PRICE_ITEMS)
            finally:
                step_text = status_step_text(stats, ws.title)
                status.update(f"Syncing {ws.title}: {step_text}")

    return stats
