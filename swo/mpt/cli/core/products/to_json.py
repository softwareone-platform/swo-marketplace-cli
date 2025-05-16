import json
import re
from typing import Any

from swo.mpt.cli.core.mpt.models import ItemGroup, Parameter, ParameterGroup
from swo.mpt.cli.core.products import constants
from swo.mpt.cli.core.utils import (
    SheetValue,
    SheetValueGenerator,
    find_first,
    find_value_for,
    find_values_by_pattern,
    set_dict_value,
)


def to_settings_json(values: SheetValueGenerator, mapping: dict[str, str]) -> dict:
    settings: dict = {}
    for value in values:
        settings_name = find_value_for(constants.SETTINGS_SETTING, value)[2]
        settings_value = find_value_for(constants.SETTINGS_VALUE, value)[2]
        json_path = mapping[settings_name]

        if ".label" not in json_path and ".title" not in json_path:
            settings_value = settings_value == "Enabled"

        settings = set_dict_value(settings, json_path, settings_value)

    return settings


def to_parameter_group_json(values: list[SheetValue]) -> dict:
    return {
        "name": find_value_for(constants.PARAMETERS_GROUPS_NAME, values)[2],
        "label": find_value_for(constants.PARAMETERS_GROUPS_LABEL, values)[2],
        "description": find_value_for(constants.PARAMETERS_GROUPS_DESCRIPTION, values)[
            2
        ],
        "displayOrder": find_value_for(
            constants.PARAMETERS_GROUPS_DISPLAY_ORDER, values
        )[2],
        "default": find_value_for(constants.PARAMETERS_GROUPS_DEFAULT, values)[2]
                   == "True",
    }


def to_item_group_json(values: list[SheetValue]) -> dict:
    return {
        "name": find_value_for(constants.ITEMS_GROUPS_NAME, values)[2],
        "label": find_value_for(constants.ITEMS_GROUPS_LABEL, values)[2],
        "description": find_value_for(constants.ITEMS_GROUPS_DESCRIPTION, values)[2],
        "displayOrder": find_value_for(constants.ITEMS_GROUPS_DISPLAY_ORDER, values)[2],
        "default": find_value_for(constants.ITEMS_GROUPS_DEFAULT, values)[2] == "True",
        "multiple": find_value_for(constants.ITEMS_GROUPS_MULTIPLE_CHOICES, values)[2]
                    == "True",
        "required": find_value_for(constants.ITEMS_GROUPS_REQUIRED, values)[2]
                    == "True",
    }


def to_parameter_json(
    scope: str,
    parameter_group_mapping: dict[str, ParameterGroup],
    values: list[SheetValue],
) -> dict:
    phase = find_value_for(constants.PARAMETERS_PHASE, values)[2]
    options = json.loads(find_value_for(constants.PARAMETERS_OPTIONS, values)[2])

    # backward compatible change for V3 Marketplace API
    if "label" in options:
        del options["label"]

    parameter_json = {
        "name": find_value_for(constants.PARAMETERS_NAME, values)[2],
        "description": find_value_for(constants.PARAMETERS_DESCRIPTION, values)[2],
        "scope": scope,
        "phase": phase,
        "type": find_value_for(constants.PARAMETERS_TYPE, values)[2],
        "options": options,
        "constraints": json.loads(
            find_value_for(constants.PARAMETERS_CONSTRAINTS, values)[2]
        ),
        "externalId": find_value_for(constants.PARAMETERS_EXTERNALID, values)[2],
        "displayOrder": find_value_for(constants.PARAMETERS_DISPLAY_ORDER, values)[2],
    }

    if phase == "Order" and scope not in ("Item", "Request"):
        excel_group_id = find_value_for(constants.PARAMETERS_GROUP_ID, values)[2]
        group = parameter_group_mapping[excel_group_id]

        parameter_json["group"] = {"id": group.id}

    return parameter_json


def to_product_json(data: dict[str, Any]) -> dict[str, Any]:
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
    values: list[SheetValue],
) -> dict:
    # TODO: remove all precalculation out of this function
    parameters = []
    for value in find_values_by_pattern(re.compile(r"Parameter\.*"), values):
        _, external_id = value[1].split(".")
        parameter = find_first(
            lambda p, ext_id=external_id: p.external_id == ext_id,
            item_parameters_id_mapping.values(),
        )
        parameters.append({"id": parameter.id, "value": value[2]})

    excel_group_id = find_value_for(constants.ITEMS_GROUP_ID, values)[2]
    group = item_group_mapping[excel_group_id]

    return _to_item_json(product_id, group.id, values, parameters)


def to_item_update_or_create_json(
    product_id: str, values: list[SheetValue], is_operations: bool
) -> dict:
    group_id = find_value_for(constants.ITEMS_GROUP_ID, values)[2]
    # TODO: Add item parameter update
    return _to_item_json(product_id, group_id, values, [], is_operations)


def _to_item_json(
    product_id: str,
    group_id: str,
    values: list[SheetValue],
    parameters: list[dict],
    is_operations: bool = False,
) -> dict:
    item_json = {
        "name": find_value_for(constants.ITEMS_NAME, values)[2],
        "description": find_value_for(constants.ITEMS_DESCRIPTION, values)[2],
        "group": {
            "id": group_id,
        },
        "product": {
            "id": product_id,
        },
        "quantityNotApplicable": find_value_for(
            constants.ITEMS_QUANTITY_APPLICABLE, values
        )[2]
                                 == "True",
        "unit": {
            "id": find_value_for(constants.ITEMS_UNIT_ID, values)[2],
        },
        "parameters": parameters,
    }

    period = find_value_for(constants.ITEMS_BILLING_FREQUENCY, values)[2]

    if period == "one-time":
        item_json["terms"] = {
            "period": period,
        }
    else:
        item_json["terms"] = {
            "commitment": find_value_for(constants.ITEMS_COMMITMENT_TERM, values)[2],
            "period": period,
        }

    if is_operations:
        item_json["externalIds"] = {
            "operations": find_value_for(constants.ITEMS_ERP_ITEM_ID, values)[2]
        }
    else:
        item_json["externalIds"] = {
            "vendor": find_value_for(constants.ITEMS_VENDOR_ITEM_ID, values)[2],
        }

    return item_json


def to_template_json(
    values: list[SheetValue],
) -> dict:
    return {
        "name": find_value_for(constants.TEMPLATES_NAME, values)[2],
        "type": find_value_for(constants.TEMPLATES_TYPE, values)[2],
        "content": find_value_for(constants.TEMPLATES_CONTENT, values)[2],
        "default": find_value_for(constants.TEMPLATES_DEFAULT, values)[2] == "True",
    }
