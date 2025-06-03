import enum
import os
import re
from copy import deepcopy
from functools import partial
from pathlib import Path
from typing import Optional, TypeAlias, TypeVar

from rich.status import Status
from swo.mpt.cli.core.accounts.models import Account
from swo.mpt.cli.core.errors import FileNotExistsError
from swo.mpt.cli.core.handlers.errors import (
    RequiredFieldsError,
    RequiredFieldValuesError,
    RequiredSheetsError,
)
from swo.mpt.cli.core.handlers.excel_file_handler import (
    ExcelFileHandler,
    SheetData,
    SheetDataGenerator,
)
from swo.mpt.cli.core.mpt.client import MPTClient
from swo.mpt.cli.core.mpt.flows import create_item as mpt_create_item
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
from swo.mpt.cli.core.mpt.flows import update_item as mpt_update_item
from swo.mpt.cli.core.mpt.models import (
    ItemGroup,
    Parameter,
    ParameterGroup,
    Product,
    Template,
)
from swo.mpt.cli.core.products import constants
from swo.mpt.cli.core.products.models import (
    ItemData,
    ItemGroupData,
    ParameterGroupData,
    ParametersData,
    ProductData,
    TemplateData,
)
from swo.mpt.cli.core.stats import ErrorMessagesCollector, ProductStatsCollector
from swo.mpt.cli.core.utils import (
    add_or_create_error,
    find_first,
    find_values_by_pattern,
    set_value,
    status_step_text,
)

T = TypeVar("T")
SyncResult: TypeAlias = dict[str, T]


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
    return ExcelFileHandler.normalize_file_path(path)


def check_file_exists(product_file_path: Path) -> bool:
    """
    Check that product file exists
    """
    if not ExcelFileHandler(product_file_path).exists():
        raise FileNotExistsError(product_file_path)

    return True


def check_product_definition(
    definition_path: Path, stats: ErrorMessagesCollector
) -> ErrorMessagesCollector:
    """
    Parses Product definition file and check consistency of product definition file
    """
    file_handler = ExcelFileHandler(definition_path)
    try:
        file_handler.check_required_sheet(constants.REQUIRED_TABS)
    except RequiredSheetsError as error:
        for section_name in error.details:
            stats.add_msg(section_name, "", "Required tab doesn't exist")

    for section_name in set(constants.ALL_TABS).intersection(set(file_handler.sheet_names)):
        if section_name not in constants.REQUIRED_FIELDS_BY_TAB:
            continue

        if section_name == constants.TAB_GENERAL:
            check_required_general_fields(
                file_handler,
                stats,
                section_name,
                constants.REQUIRED_FIELDS_BY_TAB[section_name],
                constants.REQUIRED_FIELDS_WITH_VALUES_BY_TAB[section_name],
            )
        else:
            check_required_columns(
                file_handler,
                stats,
                section_name,
                constants.REQUIRED_FIELDS_BY_TAB[section_name],
            )

    return stats


def check_required_general_fields(
    file_handler: ExcelFileHandler,
    stats: ErrorMessagesCollector,
    section_name: str,
    required_field_names: list[str],
    required_values_field_names: list[str],
):
    """
    Check that required fields and values are presented in General worksheet
    """
    try:
        file_handler.check_required_fields_in_vertical_sheet(section_name, required_field_names)
    except RequiredFieldsError as error:
        for field in error.details:
            stats.add_msg(section_name, "", f"Required field {field} is not provided")

    try:
        file_handler.check_required_field_values_in_vertical_sheet(
            section_name, required_values_field_names
        )
    except RequiredFieldValuesError as error:
        for field in error.details:
            stats.add_msg(
                section_name,
                field,
                "Value is not provided for the required field. Current value: None",
            )


def check_required_columns(
    file_handler: ExcelFileHandler,
    stats: ErrorMessagesCollector,
    section_name: str,
    required_field_names: list[str],
):
    """
    Check that required fields and values are presented in tables worksheet
    """
    try:
        file_handler.check_required_fields_in_horizontal_sheet(section_name, required_field_names)
    except RequiredFieldsError as error:
        for field in error.details:
            stats.add_msg(section_name, "", f"Required field {field} is not provided")


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
    file_handler = ExcelFileHandler(file_path=definition_path)
    if action == ProductAction.UPDATE:
        stats, product = update_product_definition(
            mpt_client, file_handler, active_account, stats, status
        )
    else:
        stats, product = create_product_definition(mpt_client, file_handler, stats, status)

    return stats, product


def create_product_definition(
    mpt_client: MPTClient,
    file_handler: ExcelFileHandler,
    stats: ProductStatsCollector,
    status: Status,
) -> tuple[ProductStatsCollector, Optional[Product]]:
    general_data = file_handler.get_data_from_vertical_sheet(
        constants.TAB_GENERAL, constants.GENERAL_FIELDS
    )

    general_data["settings"] = {
        str(idx): setting
        for idx, setting in enumerate(
            file_handler.get_data_from_horizontal_sheet(
                constants.TAB_SETTINGS, constants.SETTINGS_FIELDS
            )
        )
    }
    product_data = ProductData.from_dict(general_data)
    try:
        product = create_product(
            mpt_client,
            product_data.to_json(),
            product_data.settings.to_json(),
            Path(os.path.dirname(__file__)) / "../icons/fake-icon.png",
        )
        file_handler.write([{constants.TAB_GENERAL: {product_data.coordinate: product.id}}])
        stats.add_synced(constants.TAB_GENERAL)

    except Exception as e:
        add_or_create_error(file_handler, constants.TAB_GENERAL, general_data, e)
        stats.add_error(constants.TAB_GENERAL)
        return stats, None

    parameter_groups_data = file_handler.get_data_from_horizontal_sheet(
        constants.TAB_PARAMETERS_GROUPS, constants.PARAMETERS_GROUPS_FIELDS
    )
    parameters_groups_id_mapping = sync_parameters_groups(
        mpt_client,
        file_handler,
        product,
        parameter_groups_data,
        stats,
        status,
    )

    item_groups = file_handler.get_data_from_horizontal_sheet(
        constants.TAB_ITEMS_GROUPS, constants.ITEMS_GROUPS_FIELDS
    )
    items_groups_id_mapping = sync_items_groups(
        mpt_client, file_handler, product, item_groups, stats, status
    )

    agreements_parameters = file_handler.get_data_from_horizontal_sheet(
        constants.TAB_AGREEMENT_PARAMETERS, constants.PARAMETERS_FIELDS
    )
    agreements_parameters_id_mapping = sync_agreement_parameters(
        mpt_client,
        file_handler,
        product,
        agreements_parameters,
        parameters_groups_id_mapping,
        stats,
        status,
    )

    item_parameters = file_handler.get_data_from_horizontal_sheet(
        constants.TAB_ITEM_PARAMETERS, constants.PARAMETERS_FIELDS
    )
    item_parameters_id_mapping = sync_item_parameters(
        mpt_client,
        file_handler,
        product,
        item_parameters,
        parameters_groups_id_mapping,
        stats,
        status,
    )

    request_parameters = file_handler.get_data_from_horizontal_sheet(
        constants.TAB_REQUEST_PARAMETERS, constants.PARAMETERS_FIELDS
    )
    request_parameters_id_mapping = sync_request_parameters(
        mpt_client,
        file_handler,
        product,
        request_parameters,
        parameters_groups_id_mapping,
        stats,
        status,
    )

    subscription_parameters = file_handler.get_data_from_horizontal_sheet(
        constants.TAB_SUBSCRIPTION_PARAMETERS, constants.PARAMETERS_FIELDS
    )
    subscription_parameters_id_mapping = sync_subscription_parameters(
        mpt_client,
        file_handler,
        product,
        subscription_parameters,
        parameters_groups_id_mapping,
        stats,
        status,
    )

    items = file_handler.get_values_for_dynamic_sheet(
        constants.TAB_ITEMS, constants.ITEMS_FIELDS, [re.compile(r"Parameter\.*")]
    )
    sync_items(
        mpt_client,
        file_handler,
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

    templates = file_handler.get_data_from_horizontal_sheet(
        constants.TAB_TEMPLATES, constants.TEMPLATES_FIELDS
    )
    sync_templates(
        mpt_client,
        file_handler,
        product,
        templates,
        all_parameters_id_mapping,
        stats,
        status,
    )

    return stats, product


def update_product_definition(
    mpt_client: MPTClient,
    file_handler: ExcelFileHandler,
    active_account: Account,
    stats: ProductStatsCollector,
    status: Status,
) -> tuple[ProductStatsCollector, Optional[Product]]:
    general_values = file_handler.get_data_from_vertical_sheet(
        constants.TAB_GENERAL, constants.GENERAL_FIELDS
    )
    product_id = general_values[constants.GENERAL_PRODUCT_ID]["value"]
    items = file_handler.get_values_for_dynamic_sheet(
        constants.TAB_ITEMS, constants.ITEMS_FIELDS, [re.compile(r"Parameter\.*")]
    )
    update_items(
        mpt_client,
        file_handler,
        product_id,
        items,
        active_account,
        stats,
        status,
    )

    return stats, None


def update_items(
    mpt_client: MPTClient,
    file_handler: ExcelFileHandler,
    product_id: str,
    values: SheetDataGenerator,
    active_account: Account,
    stats: ProductStatsCollector,
    status: Status,
) -> None:
    sheet_name = constants.TAB_ITEMS
    for sheet_value in values:
        try:
            action = ItemAction(sheet_value[constants.ITEMS_ACTION]["value"])
            if action not in (ItemAction.SKIP, ItemAction.SKIPPED, ItemAction.CREATE):
                item_vendor_id = sheet_value[constants.ITEMS_VENDOR_ITEM_ID]["value"]
                item = get_item(mpt_client, product_id, item_vendor_id)

            match ItemAction(action):
                case ItemAction.REVIEW:
                    review_item(mpt_client, item.id)
                    stats.add_synced(sheet_name)
                case ItemAction.PUBLISH:
                    publish_item(mpt_client, item.id)
                    stats.add_synced(sheet_name)
                case ItemAction.UNPUBLISH:
                    unpublish_item(mpt_client, item.id)
                    stats.add_synced(sheet_name)
                case ItemAction.UPDATE:
                    update_item(mpt_client, active_account, item.id, product_id, sheet_value)
                    stats.add_synced(sheet_name)
                case ItemAction.CREATE:
                    create_item(
                        mpt_client,
                        active_account,
                        product_id,
                        file_handler,
                        sheet_name,
                        sheet_value,
                    )
                    stats.add_synced(sheet_name)
                case _:
                    stats.add_skipped(sheet_name)
        except Exception as e:
            add_or_create_error(file_handler, sheet_name, sheet_value, e)
            stats.add_error(sheet_name)
        finally:
            step_text = status_step_text(stats, sheet_name)
            status.update(f"Syncing {sheet_name}: {step_text}")


def update_item(
    mpt_client: MPTClient,
    account: Account,
    item_id: str,
    product_id: str,
    sheet_value: SheetData,
) -> None:
    data = deepcopy(sheet_value)
    data["product_id"] = product_id
    data["is_operations"] = account.is_operations()
    mpt_update_item(mpt_client, item_id, ItemData.from_dict(data).to_json())


def sync_parameters_groups(
    mpt_client: MPTClient,
    file_handler: ExcelFileHandler,
    product: Product,
    values: SheetDataGenerator,
    stats: ProductStatsCollector,
    status: Status,
) -> SyncResult[ParameterGroup]:
    """
    Sync product parameters groups
    Returns mapping if ids {"<excel-id>": ParameterGroup}
    """
    id_mapping = {}
    sheet_name = constants.TAB_PARAMETERS_GROUPS
    for sheet_value in values:
        try:
            parameter_group_data = ParameterGroupData.from_dict(sheet_value)
            parameter_group = create_parameter_group(
                mpt_client, product, parameter_group_data.to_json()
            )
            id_mapping[parameter_group_data.id] = parameter_group
            # TODO: refactor, should be done out of this function
            file_handler.write(
                [{sheet_name: {parameter_group_data.coordinate: parameter_group.id}}]
            )
            stats.add_synced(sheet_name)
        except Exception as e:
            add_or_create_error(file_handler, sheet_name, sheet_value, e)
            stats.add_error(sheet_name)
        finally:
            step_text = status_step_text(stats, sheet_name)
            status.update(f"Syncing {sheet_name}: {step_text}")

    return id_mapping


def sync_items_groups(
    mpt_client: MPTClient,
    file_handler: ExcelFileHandler,
    product: Product,
    values: SheetDataGenerator,
    stats: ProductStatsCollector,
    status: Status,
) -> SyncResult[ItemGroup]:
    """
    Sync item parameters groups
    Returns mapping if ids {"<excel-id>": ItemGroup}
    """
    id_mapping = {}
    sheet_name = constants.TAB_ITEMS_GROUPS
    for sheet_value in values:
        try:
            item_group_data = ItemGroupData.from_dict(sheet_value)
            new_item_group = create_item_group(mpt_client, product, item_group_data.to_json())

            id_mapping[item_group_data.id] = new_item_group
            # TODO: refactor, should be done out of this function
            file_handler.write([{sheet_name: {item_group_data.coordinate: new_item_group.id}}])
            stats.add_synced(sheet_name)
        except Exception as e:
            add_or_create_error(file_handler, sheet_name, sheet_value, e)
            stats.add_error(sheet_name)
        finally:
            step_text = status_step_text(stats, sheet_name)
            status.update(f"Syncing {sheet_name}: {step_text}")

    return id_mapping


def sync_parameters(
    scope: str,
    mpt_client: MPTClient,
    file_handler: ExcelFileHandler,
    product: Product,
    values: SheetDataGenerator,
    parameter_groups_mapping: dict[str, ParameterGroup],
    stats: ProductStatsCollector,
    status: Status,
) -> SyncResult[Parameter]:
    """
    Sync parameters by scope
    Returns mapping if ids {"<excel-id>": Parameter}
    """
    id_mapping = {}
    sheet_name = getattr(constants, f"TAB_{scope.upper()}_PARAMETERS")
    for sheet_value in values:
        sheet_value["scope"] = scope
        sheet_value["parameter_groups_mapping"] = {
            k: ParameterGroupData(**v.model_dump()) for k, v in parameter_groups_mapping.items()
        }
        parameter_data = ParametersData.from_dict(sheet_value)
        try:
            new_parameter = create_parameter(mpt_client, product, parameter_data.to_json())

            id_mapping[parameter_data.id] = new_parameter
            fields_to_update = {parameter_data.coordinate: new_parameter.id}
            if parameter_data.is_order_request() and parameter_data.created_group_id is not None:
                fields_to_update[parameter_data.created_group_coordinate] = (
                    parameter_data.created_group_id
                )

            # TODO: refactor, should be done out of this function
            file_handler.write([{sheet_name: fields_to_update}])
            stats.add_synced(sheet_name)
        except Exception as e:
            add_or_create_error(file_handler, sheet_name, sheet_value, e)
            stats.add_error(sheet_name)
        finally:
            step_text = status_step_text(stats, sheet_name)
            status.update(f"Syncing {sheet_name}: {step_text}")

    return id_mapping


sync_agreement_parameters = partial(sync_parameters, "Agreement")
sync_item_parameters = partial(sync_parameters, "Item")
sync_request_parameters = partial(sync_parameters, "Request")
sync_subscription_parameters = partial(sync_parameters, "Subscription")


def sync_items(
    mpt_client: MPTClient,
    file_handler: ExcelFileHandler,
    product: Product,
    values: SheetDataGenerator,
    items_groups_mapping: dict[str, ItemGroup],
    item_parameters_id_mapping: dict[str, Parameter],
    stats: ProductStatsCollector,
    status: Status,
) -> None:
    """
    Sync parameters by scope
    """
    id_mapping = {}
    sheet_name = constants.TAB_ITEMS
    for new_sheet_value in values:
        parameters = []
        for key, value in find_values_by_pattern(re.compile(r"Parameter\.*"), new_sheet_value):
            _, external_id = key.split(".")
            parameter = find_first(
                lambda p, ext_id=external_id: p.external_id == ext_id,
                item_parameters_id_mapping.values(),
            )
            if parameter is None:
                continue

            parameters.append({"id": parameter.id, "value": value["value"]})

        group_id = new_sheet_value[constants.ITEMS_GROUP_ID]["value"]
        created_group = items_groups_mapping[group_id]
        new_sheet_value["group_id"] = created_group.id
        new_sheet_value["parameters"] = parameters
        new_sheet_value["product_id"] = product.id
        try:
            new_sheet_value = setup_unit_of_measure(mpt_client, new_sheet_value)
            item_data = ItemData.from_dict(new_sheet_value)
            item = mpt_create_item(mpt_client, item_data.to_json())

            id_mapping[item_data.id] = item
            # TODO: refactor, should be done out of this function
            file_handler.write(
                [
                    {
                        sheet_name: {
                            item_data.coordinate: item.id,
                            item_data.unit_coordinate: item_data.group_id,
                            item_data.group_coordinate: created_group.id,
                        }
                    }
                ]
            )
            stats.add_synced(sheet_name)
        except Exception as e:
            add_or_create_error(file_handler, sheet_name, new_sheet_value, e)
            stats.add_error(sheet_name)
        finally:
            step_text = status_step_text(stats, sheet_name)
            status.update(f"Syncing {sheet_name}: {step_text}")


def create_item(
    mpt_client: MPTClient,
    active_account: Account,
    product_id: str,
    file_handler: ExcelFileHandler,
    sheet_name: str,
    sheet_value: SheetData,
) -> None:
    new_sheet_value = setup_unit_of_measure(mpt_client, sheet_value)
    new_sheet_value["product_id"] = product_id
    new_sheet_value["is_operations"] = active_account.is_operations()
    item_data = ItemData.from_dict(new_sheet_value)
    item = mpt_create_item(mpt_client, item_data.to_json())
    # TODO: refactor, should be done out of this function
    file_handler.write(
        [
            {
                sheet_name: {
                    item_data.coordinate: item.id,
                    item_data.unit_coordinate: item_data.unit_id,
                }
            }
        ]
    )


def setup_unit_of_measure(mpt_client: MPTClient, values: SheetData) -> SheetData:
    unit_name = values[constants.ITEMS_UNIT_NAME]["value"]
    uom = search_uom_by_name(mpt_client, unit_name)
    return set_value(constants.ITEMS_UNIT_ID, values, uom.id)


def sync_templates(
    mpt_client: MPTClient,
    file_handler: ExcelFileHandler,
    product: Product,
    values: SheetDataGenerator,
    all_parameters_id_mapping: dict[str, Parameter],
    stats: ProductStatsCollector,
    status: Status,
) -> SyncResult[Template]:
    """
    Sync templates
    Returns mapping if ids {"<excel-id>": Template}
    """
    id_mapping = {}
    sheet_name = constants.TAB_TEMPLATES
    for sheet_value in values:
        try:
            sheet_value = replace_parameter_variables(sheet_value, all_parameters_id_mapping)
            template_data = TemplateData.from_dict(sheet_value)
            template = create_template(mpt_client, product, template_data.to_json())
            id_mapping[template_data.id] = template
            # TODO: refactor, should be done out of this function
            file_handler.write(
                [
                    {
                        sheet_name: {
                            template_data.coordinate: template.id,
                            template_data.content_coordinate: template_data.content,
                        }
                    }
                ]
            )
            stats.add_synced(sheet_name)
        except Exception as e:
            add_or_create_error(file_handler, sheet_name, sheet_value, e)
            stats.add_error(sheet_name)
        finally:
            step_text = status_step_text(stats, sheet_name)
            status.update(f"Syncing {sheet_name}: {step_text}")

    return id_mapping


def replace_parameter_variables(
    values: SheetData, parameter_mapping: dict[str, Parameter]
) -> SheetData:
    content = values[constants.TEMPLATES_CONTENT]["value"]
    for sheet_param_id, param in parameter_mapping.items():
        content = content.replace(sheet_param_id, param.id)

    return set_value(constants.TEMPLATES_CONTENT, values, content)


def check_product_exists(mpt_client: MPTClient, product_definition_path: Path) -> Product | None:
    file_handler = ExcelFileHandler(product_definition_path)
    general_values = file_handler.get_data_from_vertical_sheet(
        constants.TAB_GENERAL, constants.GENERAL_FIELDS
    )
    product_id = general_values[constants.GENERAL_PRODUCT_ID]["value"]

    _, products = get_products(mpt_client, 1, 0, query=f"id={product_id}")
    return products[0] if products else None
