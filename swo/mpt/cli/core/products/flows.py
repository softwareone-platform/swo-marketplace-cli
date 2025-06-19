import enum
import re
from functools import partial
from pathlib import Path
from typing import Optional, TypeAlias, TypeVar

from rich.status import Status
from swo.mpt.cli.core.accounts.models import Account
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
    create_template,
    search_uom_by_name,
)
from swo.mpt.cli.core.mpt.models import (
    ItemGroup,
    Parameter,
    ParameterGroup,
    Template,
)
from swo.mpt.cli.core.products import constants
from swo.mpt.cli.core.products.api import ItemAPIService, ProductAPIService
from swo.mpt.cli.core.products.handlers import ItemExcelFileManager, ProductExcelFileManager
from swo.mpt.cli.core.products.models import (
    ItemData,
    ItemGroupData,
    ParameterGroupData,
    ParametersData,
    ProductData,
    TemplateData,
)
from swo.mpt.cli.core.products.services import ItemService, ProductService
from swo.mpt.cli.core.services.service_context import ServiceContext
from swo.mpt.cli.core.stats import ProductStatsCollector
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


def get_definition_file(path: str) -> Path:
    """
    Returns product definition file path. If only product id is passed assumed
    that product definition file is in the same folder with .xlsx file extension
    """
    return ExcelFileHandler.normalize_file_path(path)


def sync_product_definition(
    mpt_client: MPTClient,
    definition_path: Path,
    action: ProductAction,
    active_account: Account,
    stats: ProductStatsCollector,
    status: Status,
) -> tuple[ProductStatsCollector, Optional[ProductData]]:
    """
    Sync product definition to the marketplace platform
    """
    product_service_context = ServiceContext(
        account=active_account,
        api=ProductAPIService(mpt_client),
        data_model=ProductData,
        file_manager=ProductExcelFileManager(str(definition_path)),
        stats=stats,
    )
    product_service = ProductService(product_service_context)
    if action == ProductAction.UPDATE:
        result = product_service.retrieve()
        if not result.success or result.model is None:
            return stats, None

        product = result.model
        item_service_context = ServiceContext(
            account=active_account,
            api=ItemAPIService(mpt_client),
            data_model=ItemData,
            file_manager=ItemExcelFileManager(str(definition_path)),
            stats=stats,
        )
        item_service = ItemService(item_service_context)
        item_service.update(product.id)

        return stats, product

    else:
        result = product_service.create()
        if not result.success or result.model is None:
            return stats, None

        product = result.model
        file_handler = ExcelFileHandler(file_path=definition_path)
        stats, product = create_product_definition(mpt_client, file_handler, stats, status, product)

    return stats, product


def create_product_definition(
    mpt_client: MPTClient,
    file_handler: ExcelFileHandler,
    stats: ProductStatsCollector,
    status: Status,
    product: ProductData,
) -> tuple[ProductStatsCollector, Optional[ProductData]]:
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


def sync_parameters_groups(
    mpt_client: MPTClient,
    file_handler: ExcelFileHandler,
    product: ProductData,
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
    product: ProductData,
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
    product: ProductData,
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
    product: ProductData,
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
        item_data = ItemData.from_dict(new_sheet_value)
        item_data.product_id = product.id
        try:
            set_unit_of_measure(mpt_client, item_data)
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


def set_unit_of_measure(mpt_client: MPTClient, item: ItemData) -> None:
    item.unit_id = search_uom_by_name(mpt_client, item.unit_name).id


def sync_templates(
    mpt_client: MPTClient,
    file_handler: ExcelFileHandler,
    product: ProductData,
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
