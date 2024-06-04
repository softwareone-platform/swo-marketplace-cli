import enum
import json
import os
import re
from functools import partial
from pathlib import Path
from typing import Optional, TypeAlias, TypeVar

from openpyxl import load_workbook  # type: ignore
from openpyxl.workbook import Workbook  # type: ignore
from openpyxl.worksheet.worksheet import Worksheet  # type: ignore
from rich.status import Status
from swo.mpt.cli.core.accounts.models import Account
from swo.mpt.cli.core.errors import FileNotExistsError
from swo.mpt.cli.core.mpt.client import MPTClient
from swo.mpt.cli.core.mpt.flows import (
    create_item as mpt_create_item,
)
from swo.mpt.cli.core.mpt.flows import (
    create_item_group,
    create_parameter,
    create_parameter_group,
    create_product,
    create_template,
    get_item,
    get_products,
    publish_item,
    review_item,
    search_uom_by_name,
    unpublish_item,
)
from swo.mpt.cli.core.mpt.flows import (
    update_item as mpt_update_item,
)
from swo.mpt.cli.core.mpt.models import (
    Item,
    ItemGroup,
    Parameter,
    ParameterGroup,
    Product,
    Template,
)
from swo.mpt.cli.core.products import constants
from swo.mpt.cli.core.stats import ErrorMessagesCollector, ProductStatsCollector
from swo.mpt.cli.core.utils import (
    SheetValue,
    SheetValueGenerator,
    add_or_create_error,
    find_first,
    find_value_for,
    find_values_by_pattern,
    get_values_for_dynamic_table,
    get_values_for_general,
    get_values_for_table,
    set_dict_value,
    set_value,
    status_step_text,
)

T = TypeVar("T")
SyncResult: TypeAlias = tuple[Worksheet, dict[str, T]]


class ProductAction(enum.Enum):
    CREATE = "create"
    UPDATE = "update"


class ItemAction(enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    REVIEW = "review"
    PUBLISH = "publish"
    UNPUBLISH = "unpublish"
    SKIP = "-"
    SKIPPED = ""


def get_definition_file(path: str) -> Path:
    """
    Returns product definition file path. If only product id is passed assumed
    that product definition file is in the same folder with .xlsx file extension
    """
    if ".xlsx" not in path:
        path = f"{path}.xlsx"

    return Path(path)


def check_file_exists(product_file_path: Path) -> bool:
    """
    Check that product file exists
    """
    is_exists = os.path.exists(product_file_path)
    if not is_exists:
        raise FileNotExistsError(product_file_path)

    return is_exists


def check_product_definition(
    definition_path: Path, stats: ErrorMessagesCollector
) -> ErrorMessagesCollector:
    """
    Parses Product definition file and check consistensy of product definition file
    """
    # check all required columns are defined
    # check parameters and items refer to proper groups
    wb = load_workbook(filename=str(definition_path))

    for sheet_name in constants.REQUIRED_TABS:
        if sheet_name not in wb.sheetnames:
            stats.add_msg(sheet_name, "", "Required tab doesn't exist")

    existing_sheets = set(constants.REQUIRED_TABS).intersection(set(wb.sheetnames))

    for sheet_name in existing_sheets:
        if sheet_name not in constants.REQUIRED_FIELDS_BY_TAB:
            continue

        if sheet_name == constants.TAB_GENERAL:
            check_required_general_fields(
                stats,
                wb[sheet_name],
                constants.REQUIRED_FIELDS_BY_TAB[sheet_name],
                constants.REQUIRED_FIELDS_WITH_VALUES_BY_TAB[sheet_name],
            )
        else:
            check_required_columns(
                stats,
                wb[sheet_name],
                constants.REQUIRED_FIELDS_BY_TAB[sheet_name],
            )

    return stats


def check_required_general_fields(
    stats: ErrorMessagesCollector,
    sheet: Worksheet,
    required_field_names: list[str],
    required_values_field_names: list[str],
) -> ErrorMessagesCollector:
    """
    Check that required fields and values are presented in General worksheet
    """
    column_values = {v[0].value: v[1].value for v in zip(sheet["A"], sheet["B"])}

    for required_column_name in required_field_names:
        if required_column_name not in column_values:
            stats.add_msg(
                sheet.title,
                "",
                f"Required field {required_column_name} is not provided",
            )

    for required_value_column_name in required_values_field_names:
        if (
            required_value_column_name in column_values
            and not column_values[required_value_column_name]
        ):
            stats.add_msg(
                sheet.title,
                required_value_column_name,
                f"Value is not provided for the required field. "
                f"Current value: {column_values[required_value_column_name]}",
            )

    return stats


def check_required_columns(
    stats: ErrorMessagesCollector,
    sheet: Worksheet,
    required_field_names: list[str],
) -> ErrorMessagesCollector:
    """
    Check that required fields and values are presented in tables worksheet
    """
    columns = {v.value for v in sheet["1"]}
    for required_column_name in required_field_names:
        if required_column_name not in columns:
            stats.add_msg(
                sheet.title,
                "",
                f"Required field {required_column_name} is not provided",
            )

    return stats


def to_product_json(values: list[SheetValue]) -> dict:
    return {
        "name": find_value_for(constants.GENERAL_PRODUCT_NAME, values)[2],
        "shortDescription": find_value_for(
            constants.GENERAL_CATALOG_DESCRIPTION, values
        )[2],
        "longDescription": find_value_for(
            constants.GENERAL_PRODUCT_DESCRIPTION, values
        )[2],
        "website": find_value_for(constants.GENERAL_PRODUCT_WEBSITE, values)[2],
        "externalIds": None,
        "settings": None,
    }


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
        "isDefault": find_value_for(constants.PARAMETERS_GROUPS_DEFAULT, values)[2]
        == "True",
    }


def to_item_group_json(values: list[SheetValue]) -> dict:
    return {
        "name": find_value_for(constants.ITEMS_GROUPS_NAME, values)[2],
        "label": find_value_for(constants.ITEMS_GROUPS_LABEL, values)[2],
        "description": find_value_for(constants.ITEMS_GROUPS_DESCRIPTION, values)[2],
        "displayOrder": find_value_for(constants.ITEMS_GROUPS_DISPLAY_ORDER, values)[2],
        "isDefault": find_value_for(constants.ITEMS_GROUPS_DEFAULT, values)[2]
        == "True",
        "isMultipleChoice": find_value_for(
            constants.ITEMS_GROUPS_MULTIPLE_CHOICES, values
        )[2]
        == "True",
        "isRequired": find_value_for(constants.ITEMS_GROUPS_REQUIRED, values)[2]
        == "True",
    }


def to_parameter_json(
    scope: str,
    parameter_group_mapping: dict[str, ParameterGroup],
    values: list[SheetValue],
) -> dict:
    phase = find_value_for(constants.PARAMETERS_PHASE, values)[2]
    parameter_json = {
        "name": find_value_for(constants.PARAMETERS_NAME, values)[2],
        "description": find_value_for(constants.PARAMETERS_DESCRIPTION, values)[2],
        "scope": scope,
        "phase": phase,
        "type": find_value_for(constants.PARAMETERS_TYPE, values)[2],
        "options": json.loads(find_value_for(constants.PARAMETERS_OPTIONS, values)[2]),
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
        "terms": {
            "commitment": find_value_for(constants.ITEMS_COMMITMENT_TERM, values)[2],
            "period": find_value_for(constants.ITEMS_BILLING_FREQUENCY, values)[2],
        },
        "unit": {
            "id": find_value_for(constants.ITEMS_UNIT_ID, values)[2],
        },
        "parameters": parameters,
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
    product: Product,
    values: list[SheetValue],
) -> dict:
    return {
        "name": find_value_for(constants.TEMPLATES_NAME, values)[2],
        "type": find_value_for(constants.TEMPLATES_TYPE, values)[2],
        "content": find_value_for(constants.TEMPLATES_CONTENT, values)[2],
        "default": find_value_for(constants.TEMPLATES_DEFAULT, values)[2] == "True",
    }


def sync_product_definition(
    mpt_client: MPTClient,
    definition_path: Path,
    action: ProductAction,
    active_account: Account,
    stats: ProductStatsCollector,
    status: Status,
) -> tuple[ProductStatsCollector, Optional[Product]]:
    """
    Sync product definition to the marketplace platform
    """
    wb = load_workbook(filename=str(definition_path))

    if action == ProductAction.UPDATE:
        stats, product = update_product_definition(
            mpt_client, wb, active_account, stats, status
        )
    else:
        stats, product = create_product_definition(mpt_client, wb, stats, status)

    wb.save(str(definition_path))

    return stats, product


def create_product_definition(
    mpt_client: MPTClient,
    wb: Workbook,
    stats: ProductStatsCollector,
    status: Status,
) -> tuple[ProductStatsCollector, Optional[Product]]:
    try:
        general_values = get_values_for_general(
            wb[constants.TAB_GENERAL], constants.GENERAL_FIELDS
        )
        settings_values = get_values_for_table(
            wb[constants.TAB_SETTINGS], constants.SETTINGS_FIELDS
        )
        product = create_product(
            mpt_client,
            to_product_json(general_values),
            to_settings_json(settings_values, constants.SETTINGS_API_MAPPING),
            Path(os.path.dirname(__file__)) / "../icons/fake-icon.png",
        )
        index, _, _ = find_value_for(constants.GENERAL_PRODUCT_ID, general_values)
        wb[constants.TAB_GENERAL][index] = product.id
        stats.add_synced(constants.TAB_GENERAL)

    except Exception as e:
        add_or_create_error(wb[constants.TAB_GENERAL], general_values, e)
        stats.add_error(constants.TAB_GENERAL)
        return stats, None

    parameters_groups_ws = wb[constants.TAB_PARAMETERS_GROUPS]
    parameter_groups = get_values_for_table(
        parameters_groups_ws, constants.PARAMETERS_GROUPS_FIELDS
    )
    _, parameters_groups_id_mapping = sync_parameters_groups(
        mpt_client,
        parameters_groups_ws,
        product,
        parameter_groups,
        stats,
        status,
    )

    items_groups_ws = wb[constants.TAB_ITEMS_GROUPS]
    item_groups = get_values_for_table(items_groups_ws, constants.ITEMS_GROUPS_FIELDS)
    _, items_groups_id_mapping = sync_items_groups(
        mpt_client, items_groups_ws, product, item_groups, stats, status
    )

    agreements_parameters_ws = wb[constants.TAB_AGREEMENTS_PARAMETERS]
    agreements_parameters = get_values_for_table(
        agreements_parameters_ws, constants.PARAMETERS_FIELDS
    )
    _, agreements_parameters_id_mapping = sync_agreement_parameters(
        mpt_client,
        agreements_parameters_ws,
        product,
        agreements_parameters,
        parameters_groups_id_mapping,
        stats,
        status,
    )

    item_parameters_ws = wb[constants.TAB_ITEM_PARAMETERS]
    item_parameters = get_values_for_table(
        item_parameters_ws, constants.PARAMETERS_FIELDS
    )
    _, item_parameters_id_mapping = sync_item_parameters(
        mpt_client,
        item_parameters_ws,
        product,
        item_parameters,
        parameters_groups_id_mapping,
        stats,
        status,
    )

    request_parameters_ws = wb[constants.TAB_REQUEST_PARAMETERS]
    request_parameters = get_values_for_table(
        request_parameters_ws, constants.PARAMETERS_FIELDS
    )
    _, request_parameters_id_mapping = sync_request_parameters(
        mpt_client,
        request_parameters_ws,
        product,
        request_parameters,
        parameters_groups_id_mapping,
        stats,
        status,
    )

    subscription_parameters_ws = wb[constants.TAB_SUBSCRIPTION_PARAMETERS]
    subscription_parameters = get_values_for_table(
        subscription_parameters_ws, constants.PARAMETERS_FIELDS
    )
    _, subscription_parameters_id_mapping = sync_subscription_parameters(
        mpt_client,
        subscription_parameters_ws,
        product,
        subscription_parameters,
        parameters_groups_id_mapping,
        stats,
        status,
    )

    items_ws = wb[constants.TAB_ITEMS]
    items = get_values_for_dynamic_table(
        items_ws, constants.ITEMS_FIELDS, [re.compile(r"Parameter\.*")]
    )
    _, items_id_mapping = sync_items(
        mpt_client,
        items_ws,
        product,
        items,
        items_groups_id_mapping,
        item_parameters_id_mapping,
        stats,
        status,
    )

    all_parameters_id_mapping = {
        **agreements_parameters_id_mapping,
        **item_parameters_id_mapping,
        **request_parameters_id_mapping,
        **subscription_parameters_id_mapping,
    }

    templates_ws = wb[constants.TAB_TEMPLATES]
    templates = get_values_for_table(templates_ws, constants.TEMPLATES_FIELDS)
    _, templates_id_mapping = sync_templates(
        mpt_client,
        templates_ws,
        product,
        templates,
        all_parameters_id_mapping,
        stats,
        status,
    )

    return stats, product


def update_product_definition(
    mpt_client: MPTClient,
    wb: Workbook,
    active_account: Account,
    stats: ProductStatsCollector,
    status: Status,
) -> tuple[ProductStatsCollector, Optional[Product]]:
    general_values = get_values_for_general(
        wb[constants.TAB_GENERAL], constants.GENERAL_FIELDS
    )
    product_id = find_value_for(constants.GENERAL_PRODUCT_ID, general_values)[2]

    items_ws = wb[constants.TAB_ITEMS]
    items = get_values_for_dynamic_table(
        items_ws, constants.ITEMS_FIELDS, [re.compile(r"Parameter\.*")]
    )

    update_items(
        mpt_client,
        items_ws,
        product_id,
        items,
        active_account,
        stats,
        status,
    )

    return stats, None


def update_items(
    mpt_client: MPTClient,
    ws: Worksheet,
    product_id: str,
    values: SheetValueGenerator,
    active_account: Account,
    stats: ProductStatsCollector,
    status: Status,
) -> None:
    for sheet_value in values:
        try:
            action = ItemAction(find_value_for(constants.ITEMS_ACTION, sheet_value)[2])
            if action not in (ItemAction.SKIP, ItemAction.SKIPPED, ItemAction.CREATE):
                item_vendor_id = find_value_for(constants.ITEMS_VENDOR_ITEM_ID, sheet_value)[2]
                item = get_item(mpt_client, product_id, item_vendor_id)

            match ItemAction(action):
                case ItemAction.REVIEW:
                    review_item(mpt_client, item.id)
                    stats.add_synced(ws.title)
                case ItemAction.PUBLISH:
                    publish_item(mpt_client, item.id)
                    stats.add_synced(ws.title)
                case ItemAction.UNPUBLISH:
                    unpublish_item(mpt_client, item.id)
                    stats.add_synced(ws.title)
                case ItemAction.UPDATE:
                    update_item(
                        mpt_client, active_account, item.id, product_id, sheet_value
                    )
                    stats.add_synced(ws.title)
                case ItemAction.CREATE:
                    create_item(mpt_client, active_account, product_id, ws, sheet_value)
                    stats.add_synced(ws.title)
                case _:
                    stats.add_skipped(ws.title)
        except Exception as e:
            add_or_create_error(ws, sheet_value, e)
            stats.add_error(ws.title)
        finally:
            step_text = status_step_text(stats, ws.title)
            status.update(f"Syncing {ws.title}: {step_text}")


def update_item(
    mpt_client: MPTClient,
    active_account: Account,
    item_id: str,
    product_id: str,
    sheet_value: list[SheetValue],
) -> None:
    item_json = to_item_update_or_create_json(
        product_id, sheet_value, active_account.type == "Operations"
    )
    mpt_update_item(mpt_client, item_id, item_json)


def sync_parameters_groups(
    mpt_client: MPTClient,
    ws: Worksheet,
    product: Product,
    values: SheetValueGenerator,
    stats: ProductStatsCollector,
    status: Status,
) -> SyncResult[ParameterGroup]:
    """
    Sync product parameters groups
    Returns mapping if ids {"<excel-id>": ParameterGroup}
    """
    id_mapping = {}

    for sheet_value in values:
        try:
            parameter_group = create_parameter_group(
                mpt_client,
                product,
                to_parameter_group_json(sheet_value),
            )

            index, _, sheet_id_value = find_value_for(
                constants.PARAMETERS_GROUPS_ID, sheet_value
            )

            # TODO: refactor, should be done out of this function
            ws[index] = parameter_group.id
            id_mapping[sheet_id_value] = parameter_group
            stats.add_synced(ws.title)
        except Exception as e:
            add_or_create_error(ws, sheet_value, e)
            stats.add_error(ws.title)
        finally:
            step_text = status_step_text(stats, ws.title)
            status.update(f"Syncing {ws.title}: {step_text}")

    return ws, id_mapping


def sync_items_groups(
    mpt_client: MPTClient,
    ws: Worksheet,
    product: Product,
    values: SheetValueGenerator,
    stats: ProductStatsCollector,
    status: Status,
) -> SyncResult[ItemGroup]:
    """
    Sync item parameters groups
    Returns mapping if ids {"<excel-id>": ItemGroup}
    """
    id_mapping = {}

    for sheet_value in values:
        try:
            item_group = create_item_group(
                mpt_client,
                product,
                to_item_group_json(sheet_value),
            )

            index, _, sheet_id_value = find_value_for(
                constants.ITEMS_GROUPS_ID, sheet_value
            )

            # TODO: refactor, should be done out of this function
            ws[index] = item_group.id
            id_mapping[sheet_id_value] = item_group
            stats.add_synced(ws.title)
        except Exception as e:
            add_or_create_error(ws, sheet_value, e)
            stats.add_error(ws.title)
        finally:
            step_text = status_step_text(stats, ws.title)
            status.update(f"Syncing {ws.title}: {step_text}")

    return ws, id_mapping


def sync_parameters(
    scope: str,
    mpt_client: MPTClient,
    ws: Worksheet,
    product: Product,
    values: SheetValueGenerator,
    parameter_groups_mapping: dict[str, ParameterGroup],
    stats: ProductStatsCollector,
    status: Status,
) -> SyncResult[Parameter]:
    """
    Sync parameters by scope
    Returns mapping if ids {"<excel-id>": Parameter}
    """
    id_mapping = {}

    for sheet_value in values:
        try:
            parameter = create_parameter(
                mpt_client,
                product,
                to_parameter_json(scope, parameter_groups_mapping, sheet_value),
            )

            id_index, _, sheet_id_value = find_value_for(
                constants.ID_COLUMN_NAME, sheet_value
            )

            # TODO: refactor, should be done out of this function
            ws[id_index] = parameter.id
            id_mapping[sheet_id_value] = parameter

            phase = find_value_for(constants.PARAMETERS_PHASE, sheet_value)[2]
            if phase == "Order" and scope not in ("Item", "Request"):
                group_id_index, _, sheet_id_value = find_value_for(
                    constants.PARAMETERS_GROUP_ID, sheet_value
                )
                created_group = parameter_groups_mapping[sheet_id_value]
                ws[group_id_index] = created_group.id
            stats.add_synced(ws.title)
        except Exception as e:
            add_or_create_error(ws, sheet_value, e)
            stats.add_error(ws.title)
        finally:
            step_text = status_step_text(stats, ws.title)
            status.update(f"Syncing {ws.title}: {step_text}")

    return ws, id_mapping


sync_agreement_parameters = partial(sync_parameters, "Agreement")
sync_item_parameters = partial(sync_parameters, "Item")
sync_request_parameters = partial(sync_parameters, "Request")
sync_subscription_parameters = partial(sync_parameters, "Subscription")


def sync_items(
    mpt_client: MPTClient,
    ws: Worksheet,
    product: Product,
    values: SheetValueGenerator,
    items_groups_mapping: dict[str, ItemGroup],
    item_parameters_id_mapping: dict[str, Parameter],
    stats: ProductStatsCollector,
    status: Status,
) -> SyncResult[Item]:
    """
    Sync parameters by scope
    Returns mapping if ids {"<excel-id>": Item}
    """
    id_mapping = {}

    for sheet_value in values:
        try:
            sheet_value = setup_unit_of_measure(mpt_client, sheet_value)
            item = mpt_create_item(
                mpt_client,
                to_item_sync_json(
                    product.id,
                    items_groups_mapping,
                    item_parameters_id_mapping,
                    sheet_value,
                ),
            )

            id_index, _, sheet_id_value = find_value_for(
                constants.ID_COLUMN_NAME, sheet_value
            )

            # TODO: refactor, should be done out of this function
            ws[id_index] = item.id
            id_mapping[sheet_id_value] = item

            uom_id_index, _, sheet_id_value = find_value_for(
                constants.ITEMS_UNIT_ID, sheet_value
            )
            ws[uom_id_index] = sheet_id_value

            group_id_index, _, sheet_id_value = find_value_for(
                constants.ITEMS_GROUP_ID, sheet_value
            )
            created_group = items_groups_mapping[sheet_id_value]
            ws[group_id_index] = created_group.id
            stats.add_synced(ws.title)
        except Exception as e:
            add_or_create_error(ws, sheet_value, e)
            stats.add_error(ws.title)
        finally:
            step_text = status_step_text(stats, ws.title)
            status.update(f"Syncing {ws.title}: {step_text}")

    return ws, id_mapping


def create_item(
    mpt_client: MPTClient,
    active_account: Account,
    product_id: str,
    ws: Worksheet,
    sheet_value: list[SheetValue],
) -> None:
    sheet_value = setup_unit_of_measure(mpt_client, sheet_value)
    item = mpt_create_item(
        mpt_client,
        to_item_update_or_create_json(
            product_id,
            sheet_value,
            active_account.type == "Operations",
        ),
    )

    id_index, _, sheet_id_value = find_value_for(constants.ID_COLUMN_NAME, sheet_value)

    # TODO: refactor, should be done out of this function
    ws[id_index] = item.id

    uom_id_index, _, sheet_id_value = find_value_for(
        constants.ITEMS_UNIT_ID, sheet_value
    )
    ws[uom_id_index] = sheet_id_value


def setup_unit_of_measure(
    mpt_client: MPTClient, values: list[SheetValue]
) -> list[SheetValue]:
    unit_name = find_value_for(constants.ITEMS_UNIT_NAME, values)[2]

    uom = search_uom_by_name(mpt_client, unit_name)
    return set_value(constants.ITEMS_UNIT_ID, values, uom.id)


def sync_templates(
    mpt_client: MPTClient,
    ws: Worksheet,
    product: Product,
    values: SheetValueGenerator,
    all_parameters_id_mapping: dict[str, Parameter],
    stats: ProductStatsCollector,
    status: Status,
) -> SyncResult[Template]:
    """
    Sync templates
    Returns mapping if ids {"<excel-id>": Template}
    """
    id_mapping = {}

    for sheet_value in values:
        try:
            sheet_value = replace_parameter_variables(
                sheet_value, all_parameters_id_mapping
            )
            template = create_template(
                mpt_client,
                product,
                to_template_json(product, sheet_value),
            )

            content_index, _, sheet_content_value = find_value_for(
                constants.TEMPLATES_CONTENT, sheet_value
            )
            ws[content_index] = sheet_content_value

            id_index, _, sheet_id_value = find_value_for(
                constants.ID_COLUMN_NAME, sheet_value
            )

            # TODO: refactor, should be done out of this function
            ws[id_index] = template.id
            id_mapping[sheet_id_value] = template
            stats.add_synced(ws.title)
        except Exception as e:
            add_or_create_error(ws, sheet_value, e)
            stats.add_error(ws.title)
        finally:
            step_text = status_step_text(stats, ws.title)
            status.update(f"Syncing {ws.title}: {step_text}")

    return ws, id_mapping


def replace_parameter_variables(
    values: list[SheetValue], parameter_mapping: dict[str, Parameter]
) -> list[SheetValue]:
    _, _, content = find_value_for(constants.TEMPLATES_CONTENT, values)

    for sheet_param_id, param in parameter_mapping.items():
        content = content.replace(sheet_param_id, param.id)

    return set_value(constants.TEMPLATES_CONTENT, values, content)


def check_product_exists(
    mpt_client: MPTClient, product_definition_path: Path
) -> Product | None:
    wb = load_workbook(filename=str(product_definition_path))
    general_values = get_values_for_general(
        wb[constants.TAB_GENERAL], constants.GENERAL_FIELDS
    )

    product_id = find_value_for(constants.GENERAL_PRODUCT_ID, general_values)[2]

    _, products = get_products(mpt_client, 1, 0, query=f"id={product_id}")
    return products[0] if products else None
