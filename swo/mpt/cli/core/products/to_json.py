import json
import re
from typing import Any

from swo.mpt.cli.core.handlers.excel_file_handler import SheetData, SheetDataGenerator
from swo.mpt.cli.core.mpt.models import ItemGroup, Parameter, ParameterGroup
from swo.mpt.cli.core.products import constants
from swo.mpt.cli.core.utils import (
    find_first,
    find_values_by_pattern,
    set_dict_value,
)


def to_settings_json(values: SheetDataGenerator, mapping: dict[str, str]) -> dict:
    settings: dict = {}
    for value in values:
        settings_name = value[constants.SETTINGS_SETTING]["value"]
        settings_value = value[constants.SETTINGS_VALUE]["value"]
        json_path = mapping[settings_name]

        if ".label" not in json_path and ".title" not in json_path:
            settings_value = settings_value == "Enabled"

        settings = set_dict_value(settings, json_path, settings_value)

    return settings


def to_parameter_group_json(values: SheetData) -> dict[str, Any]:
    return {
        "name": values[constants.PARAMETERS_GROUPS_NAME]["value"],
        "label": values[constants.PARAMETERS_GROUPS_LABEL]["value"],
        "description": values[constants.PARAMETERS_GROUPS_DESCRIPTION]["value"],
        "displayOrder": values[constants.PARAMETERS_GROUPS_DISPLAY_ORDER]["value"],
        "default": values[constants.PARAMETERS_GROUPS_DEFAULT]["value"] == "True",
    }


def to_item_group_json(values: SheetData) -> dict[str, Any]:
    return {
        "name": values[constants.ITEMS_GROUPS_NAME]["value"],
        "label": values[constants.ITEMS_GROUPS_LABEL]["value"],
        "description": values[constants.ITEMS_GROUPS_DESCRIPTION]["value"],
        "displayOrder": values[constants.ITEMS_GROUPS_DISPLAY_ORDER]["value"],
        "default": values[constants.ITEMS_GROUPS_DEFAULT]["value"] == "True",
        "multiple": values[constants.ITEMS_GROUPS_MULTIPLE_CHOICES]["value"] == "True",
        "required": values[constants.ITEMS_GROUPS_REQUIRED]["value"] == "True",
    }


def to_parameter_json(
    scope: str,
    parameter_group_mapping: dict[str, ParameterGroup],
    values: SheetData,
) -> dict[str, Any]:
    # backward compatible change for V3 Marketplace API
    options = json.loads(values[constants.PARAMETERS_OPTIONS]["value"])
    if "label" in options:
        del options["label"]

    phase = values[constants.PARAMETERS_PHASE]["value"]
    parameter_json = {
        "name": values[constants.PARAMETERS_NAME]["value"],
        "description": values[constants.PARAMETERS_DESCRIPTION]["value"],
        "scope": scope,
        "phase": phase,
        "type": values[constants.PARAMETERS_TYPE]["value"],
        "options": options,
        "constraints": json.loads(values[constants.PARAMETERS_CONSTRAINTS]["value"]),
        "externalId": values[constants.PARAMETERS_EXTERNALID]["value"],
        "displayOrder": values[constants.PARAMETERS_DISPLAY_ORDER]["value"],
    }

    if phase == "Order" and scope not in ("Item", "Request"):
        excel_group_id = values[constants.PARAMETERS_GROUP_ID]["value"]
        group = parameter_group_mapping[excel_group_id]

        parameter_json["group"] = {"id": group.id}

    return parameter_json


def to_product_json(data: SheetData) -> dict[str, Any]:
    return {
        "name": data[constants.GENERAL_PRODUCT_NAME]["value"],
        "shortDescription": data[constants.GENERAL_CATALOG_DESCRIPTION]["value"],
        "longDescription": data[constants.GENERAL_PRODUCT_DESCRIPTION]["value"],
        "website": data[constants.GENERAL_PRODUCT_WEBSITE]["value"],
        "externalIds": None,
        "settings": None,
    }


def to_item_sync_json(
    product_id: str,
    item_group_mapping: dict[str, ItemGroup],
    item_parameters_id_mapping: dict[str, Parameter],
    values: SheetData,
) -> dict[str, Any]:
    # TODO: remove all precalculation out of this function
    parameters = []
    for key, value in find_values_by_pattern(re.compile(r"Parameter\.*"), values):
        _, external_id = key.split(".")
        parameter = find_first(
            lambda p, ext_id=external_id: p.external_id == ext_id,
            item_parameters_id_mapping.values(),
        )
        parameters.append({"id": parameter.id, "value": value["value"]})

    excel_group_id = values[constants.ITEMS_GROUP_ID]["value"]
    group = item_group_mapping[excel_group_id]
    return _to_item_json(product_id, group.id, values, parameters)


def to_item_update_or_create_json(product_id: str, values: SheetData, is_operations: bool) -> dict:
    group_id = values[constants.ITEMS_GROUP_ID]["value"]
    # TODO: Add item parameter update
    return _to_item_json(product_id, group_id, values, [], is_operations)


def _to_item_json(
    product_id: str,
    group_id: str,
    values: SheetData,
    parameters: list[dict],
    is_operations: bool = False,
) -> dict:
    item_json = {
        "name": values[constants.ITEMS_NAME]["value"],
        "description": values[constants.ITEMS_DESCRIPTION]["value"],
        "group": {
            "id": group_id,
        },
        "product": {
            "id": product_id,
        },
        "quantityNotApplicable": values[constants.ITEMS_QUANTITY_APPLICABLE]["value"] == "True",
        "unit": {
            "id": values[constants.ITEMS_UNIT_ID]["value"],
        },
        "parameters": parameters,
    }

    period = values[constants.ITEMS_BILLING_FREQUENCY]["value"]
    if period == "one-time":
        item_json["terms"] = {
            "period": period,
        }
    else:
        item_json["terms"] = {
            "commitment": values[constants.ITEMS_COMMITMENT_TERM]["value"],
            "period": period,
        }

    if is_operations:
        item_json["externalIds"] = {
            "operations": values[constants.ITEMS_ERP_ITEM_ID]["value"],
        }
    else:
        item_json["externalIds"] = {
            "vendor": values[constants.ITEMS_VENDOR_ITEM_ID]["value"],
        }

    return item_json


def to_template_json(values: SheetData) -> dict[str, Any]:
    return {
        "name": values[constants.TEMPLATES_NAME]["value"],
        "type": values[constants.TEMPLATES_TYPE]["value"],
        "content": values[constants.TEMPLATES_CONTENT]["value"],
        "default": values[constants.TEMPLATES_DEFAULT]["value"] == "True",
    }
