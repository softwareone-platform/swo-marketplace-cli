from swo.mpt.cli.core.handlers.excel_file_handler import SheetData
from swo.mpt.cli.core.pricelists import constants


def to_operations_pricelist_json(values: SheetData) -> SheetData:
    pricelist_json = to_vendor_pricelist_json(values)
    pricelist_json["defaultMarkup"] = values[constants.GENERAL_DEFAULT_MARKUP]["value"]

    return pricelist_json


def to_vendor_pricelist_json(values: SheetData) -> SheetData:
    pricelist_json = {
        "currency": values[constants.GENERAL_CURRENCY]["value"],
        "precision": values[constants.GENERAL_PRECISION]["value"],
        "notes": values[constants.GENERAL_NOTES]["value"],
        "product": {"id": values[constants.GENERAL_PRODUCT_ID]["value"]},
    }

    external_id = values.get(constants.EXTERNAL_ID, {}).get("value")
    if external_id:
        pricelist_json["externalIds"] = {"vendor": external_id}

    return pricelist_json


def to_operations_priceitem_json(values: SheetData) -> SheetData:
    status = values[constants.PRICELIST_ITEMS_STATUS]["value"]
    priceitem_json = {
        "markup": values[constants.PRICELIST_ITEMS_MARKUP]["value"],
        "unitLP": values[constants.PRICELIST_ITEMS_UNIT_LP]["value"],
        "unitPP": values[constants.PRICELIST_ITEMS_UNIT_PP]["value"],
    }

    unit_sp = values.get(constants.PRICELIST_ITEMS_UNIT_SP, {}).get("value")
    if unit_sp is not None:
        priceitem_json["unitSP"] = unit_sp

    if status != "Draft":
        priceitem_json["status"] = status

    return priceitem_json


def to_vendor_priceitem_json(values: SheetData) -> SheetData:
    return {
        "status": values[constants.PRICELIST_ITEMS_STATUS]["value"],
        "unitLP": values[constants.PRICELIST_ITEMS_UNIT_LP]["value"],
        "unitPP": values[constants.PRICELIST_ITEMS_UNIT_PP]["value"],
    }
