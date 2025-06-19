import re
from unittest.mock import Mock, call

import pytest
from swo.mpt.cli.core.console import console
from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.handlers.excel_file_handler import ExcelFileHandler
from swo.mpt.cli.core.mpt.models import Item
from swo.mpt.cli.core.products import constants
from swo.mpt.cli.core.products.flows import (
    ProductAction,
    sync_items,
    sync_items_groups,
    sync_parameters,
    sync_parameters_groups,
    sync_product_definition,
    sync_templates,
)
from swo.mpt.cli.core.products.services import ItemService, ProductService
from swo.mpt.cli.core.services.service_result import ServiceResult
from swo.mpt.cli.core.stats import ProductStatsCollector


@pytest.fixture
def items():
    # see tests/product_files/PRD-1234-1234-1234-file-update.xlsx file
    return [
        Item(id="ITM-1213-3316-0001", name="Adobe PhotoKios"),
        Item(id="ITM-1213-3316-0002", name="Customer"),
        Item(id="ITM-1213-3316-0003", name="Customer"),
        Item(id="ITM-1213-3316-0005", name="Customer"),
    ]


def test_sync_parameters_groups(mocker, mpt_client, new_product_file, product, parameter_group):
    stats = ProductStatsCollector()
    parameter_group_mock = mocker.patch(
        "swo.mpt.cli.core.products.flows.create_parameter_group", return_value=parameter_group
    )
    file_handler = ExcelFileHandler(new_product_file)
    values = file_handler.get_data_from_horizontal_sheet(
        constants.TAB_PARAMETERS_GROUPS, constants.PARAMETERS_GROUPS_FIELDS
    )

    id_mapping = sync_parameters_groups(
        mpt_client, file_handler, product, values, stats, console.status("")
    )

    assert id_mapping == {
        "PGR-4944-4118-0002": parameter_group,
        "PGR-4944-4118-0003": parameter_group,
    }
    a2_value = file_handler.get_cell_value_by_coordinate(constants.TAB_PARAMETERS_GROUPS, "A2")
    a3_value = file_handler.get_cell_value_by_coordinate(constants.TAB_PARAMETERS_GROUPS, "A3")
    assert (a2_value, a3_value) == (parameter_group.id, parameter_group.id)
    assert parameter_group_mock.mock_calls[0].args == (
        mpt_client,
        product,
        {
            "name": "Agreement",
            "label": "Default Group",
            "description": "Description 1",
            "displayOrder": 10,
            "default": True,
        },
    )
    assert parameter_group_mock.mock_calls[1].args == (
        mpt_client,
        product,
        {
            "name": "Customer",
            "label": "Additional Group",
            "description": "Description 2",
            "displayOrder": 20,
            "default": False,
        },
    )


def test_sync_parameters_groups_exception(mocker, mpt_client, new_product_file, product):
    stats = ProductStatsCollector()
    mocker.patch(
        "swo.mpt.cli.core.products.flows.create_parameter_group",
        side_effect=MPTAPIError("Error", "Error"),
    )

    file_handler = ExcelFileHandler(new_product_file)
    sheet_name = constants.TAB_PARAMETERS_GROUPS
    values = file_handler.get_data_from_horizontal_sheet(
        sheet_name, constants.PARAMETERS_GROUPS_FIELDS
    )

    sync_parameters_groups(mpt_client, file_handler, product, values, stats, console.status(""))

    j2_value = file_handler.get_cell_value_by_coordinate(sheet_name, "J2")
    assert j2_value == "Error with response body Error"


def test_sync_items_groups(mocker, mpt_client, new_product_file, product, item_group):
    stats = ProductStatsCollector()
    item_group_mock = mocker.patch(
        "swo.mpt.cli.core.products.flows.create_item_group", return_value=item_group
    )

    file_handler = ExcelFileHandler(new_product_file)
    values = file_handler.get_data_from_horizontal_sheet(
        constants.TAB_ITEMS_GROUPS, constants.ITEMS_GROUPS_FIELDS
    )

    id_mapping = sync_items_groups(
        mpt_client, file_handler, product, values, stats, console.status("")
    )

    assert id_mapping == {
        "IGR-4944-4118-0002": item_group,
        "IGR-4944-4118-0003": item_group,
    }
    a2_value = file_handler.get_cell_value_by_coordinate(constants.TAB_ITEMS_GROUPS, "A2")
    a3_value = file_handler.get_cell_value_by_coordinate(constants.TAB_ITEMS_GROUPS, "A3")
    assert (a2_value, a3_value) == (item_group.id, item_group.id)
    assert item_group_mock.mock_calls[0].args == (
        mpt_client,
        product,
        {
            "name": "Agreement",
            "label": "Default Group",
            "description": "Description 1",
            "displayOrder": 10,
            "default": True,
            "multiple": True,
            "required": True,
        },
    )
    assert item_group_mock.mock_calls[1].args == (
        mpt_client,
        product,
        {
            "name": "Customer",
            "label": "Additional Group",
            "description": "Description 2",
            "displayOrder": 20,
            "default": False,
            "multiple": False,
            "required": True,
        },
    )


def test_sync_items_groups_exception(mocker, mpt_client, new_product_file, product):
    stats = ProductStatsCollector()
    mocker.patch(
        "swo.mpt.cli.core.products.flows.create_item_group",
        side_effect=MPTAPIError("Error", "Error"),
    )

    file_handler = ExcelFileHandler(new_product_file)
    values = file_handler.get_data_from_horizontal_sheet(
        constants.TAB_ITEMS_GROUPS, constants.ITEMS_GROUPS_FIELDS
    )

    sync_items_groups(mpt_client, file_handler, product, values, stats, console.status(""))

    l2_value = file_handler.get_cell_value_by_coordinate(constants.TAB_ITEMS_GROUPS, "L2")
    assert l2_value == "Error with response body Error"


def test_sync_parameters(mocker, mpt_client, new_product_file, product, parameter, parameter_group):
    stats = ProductStatsCollector()
    parameter_mock = mocker.patch(
        "swo.mpt.cli.core.products.flows.create_parameter", return_value=parameter
    )

    file_handler = ExcelFileHandler(new_product_file)
    sheet_name = constants.TAB_AGREEMENT_PARAMETERS
    values = file_handler.get_data_from_horizontal_sheet(sheet_name, constants.PARAMETERS_FIELDS)
    id_mapping = sync_parameters(
        "Agreement",
        mpt_client,
        file_handler,
        product,
        values,
        {
            "PGR-4944-4118-0002": parameter_group,
        },
        stats,
        console.status(""),
    )

    assert id_mapping == {
        "PAR-4944-4118-0001": parameter,
        "PAR-4944-4118-0002": parameter,
    }
    a2_value = file_handler.get_cell_value_by_coordinate(sheet_name, "A2")
    a3_value = file_handler.get_cell_value_by_coordinate(sheet_name, "A3")
    assert (a2_value, a3_value) == (parameter.id, parameter.id)
    assert file_handler.get_cell_value_by_coordinate(sheet_name, "H2") == parameter_group.id
    assert parameter_mock.mock_calls[0].args == (
        mpt_client,
        product,
        {
            "name": "Parameter 1",
            "description": "Test parameter 1",
            "scope": "Agreement",
            "phase": "Order",
            "type": "Choice",
            "group": {
                "id": parameter_group.id,
            },
            "options": {
                "optionsList": [
                    {
                        "label": "Create account",
                        "value": "New",
                        "order": 0,
                        "description": "Description 1",
                    },
                    {
                        "label": "Migrate account",
                        "value": "Migrate",
                        "order": 1,
                        "description": "Description 2",
                    },
                ],
                "defaultValue": "New",
                "hintText": "Some hint text",
            },
            "constraints": {
                "hidden": False,
                "unique": None,
                "readonly": False,
                "optional": False,
            },
            "externalId": "external_1",
            "displayOrder": 100,
        },
    )
    assert parameter_mock.mock_calls[1].args == (
        mpt_client,
        product,
        {
            "name": "Parameter 2",
            "description": "Test parameter 2",
            "scope": "Agreement",
            "phase": "Fulfillment",
            "type": "SingleLineText",
            "options": {
                "hintText": "Retry Count",
                "placeholderText": "Retry Count",
            },
            "constraints": {
                "hidden": False,
                "unique": False,
                "readonly": None,
                "optional": False,
            },
            "externalId": "external_2",
            "displayOrder": 200,
        },
    )


def test_sync_parameters_exception(mocker, mpt_client, new_product_file, product, parameter_group):
    stats = ProductStatsCollector()
    mocker.patch(
        "swo.mpt.cli.core.products.flows.create_parameter",
        side_effect=MPTAPIError("Error", "Error"),
    )

    file_handler = ExcelFileHandler(new_product_file)
    sheet_name = constants.TAB_AGREEMENT_PARAMETERS
    values = file_handler.get_data_from_horizontal_sheet(sheet_name, constants.PARAMETERS_FIELDS)

    sync_parameters(
        "Agreement",
        mpt_client,
        file_handler,
        product,
        values,
        {
            "PGR-4944-4118-0002": parameter_group,
        },
        stats,
        console.status(""),
    )

    o2_value = file_handler.get_cell_value_by_coordinate(sheet_name, "O2")
    assert o2_value == "Error with response body Error"


def test_sync_item(
    mocker,
    mpt_client,
    new_product_file,
    product,
    parameter,
    another_parameter,
    item,
    item_group,
    uom,
):
    stats = ProductStatsCollector()
    item_mock = mocker.patch("swo.mpt.cli.core.products.flows.mpt_create_item", return_value=item)
    mocker.patch("swo.mpt.cli.core.products.flows.search_uom_by_name", return_value=uom)

    file_handler = ExcelFileHandler(new_product_file)
    values = file_handler.get_values_for_dynamic_sheet(
        constants.TAB_ITEMS, constants.ITEMS_FIELDS, [re.compile(r"Parameter\.*")]
    )

    sync_items(
        mpt_client,
        file_handler,
        product,
        values,
        {
            "IGR-4944-4118-0002": item_group,
        },
        {
            "PAR-0000-0000-00001": parameter,
            "PAR-0000-0000-00002": another_parameter,
        },
        stats,
        console.status(""),
    )

    assert file_handler.get_cell_value_by_coordinate(constants.TAB_ITEMS, "A2") == item.id
    assert file_handler.get_cell_value_by_coordinate(constants.TAB_ITEMS, "A3") == item.id
    assert file_handler.get_cell_value_by_coordinate(constants.TAB_ITEMS, "J2") == item_group.id
    assert file_handler.get_cell_value_by_coordinate(constants.TAB_ITEMS, "J3") == item_group.id
    assert item_mock.call_args_list == [
        call(
            mpt_client,
            {
                "name": "Adobe PhotoKiosk",
                "description": "Description 1",
                "externalIds": {
                    "vendor": "65AB123BASD",
                },
                "group": {
                    "id": item_group.id,
                },
                "product": {
                    "id": product.id,
                },
                "quantityNotApplicable": True,
                "terms": {
                    "commitment": "1y",
                    "period": "1m",
                },
                "unit": {
                    "id": uom.id,
                },
                "parameters": [
                    {
                        "id": parameter.id,
                        "value": "New",
                    },
                    {
                        "id": another_parameter.id,
                        "value": "test ex 21",
                    },
                ],
            },
        ),
        call(
            mpt_client,
            {
                "name": "Customer",
                "description": "Description 2",
                "externalIds": {
                    "vendor": "65AB123BASD",
                },
                "group": {
                    "id": item_group.id,
                },
                "product": {
                    "id": product.id,
                },
                "quantityNotApplicable": False,
                "terms": {
                    "commitment": "1y",
                    "period": "1m",
                },
                "unit": {
                    "id": uom.id,
                },
                "parameters": [
                    {
                        "id": parameter.id,
                        "value": "Migrate",
                    },
                    {
                        "id": another_parameter.id,
                        "value": "test ex 22",
                    },
                ],
            },
        ),
    ]


def test_sync_item_exception(
    mocker,
    mpt_client,
    new_product_file,
    product,
    parameter,
    another_parameter,
    item_group,
    uom,
):
    stats = ProductStatsCollector()
    mocker.patch(
        "swo.mpt.cli.core.products.flows.mpt_create_item",
        side_effect=MPTAPIError("Error", "Error"),
    )
    mocker.patch("swo.mpt.cli.core.products.flows.search_uom_by_name", return_value=uom)

    file_handler = ExcelFileHandler(new_product_file)
    values = file_handler.get_values_for_dynamic_sheet(
        constants.TAB_ITEMS, constants.ITEMS_FIELDS, [re.compile(r"Parameter\.*")]
    )

    sync_items(
        mpt_client,
        file_handler,
        product,
        values,
        {
            "IGR-4944-4118-0002": item_group,
        },
        {
            "PAR-0000-0000-00001": parameter,
            "PAR-0000-0000-00002": another_parameter,
        },
        stats,
        console.status(""),
    )

    s2_value = file_handler.get_cell_value_by_coordinate(constants.TAB_ITEMS, "S2")
    assert s2_value == "Error with response body Error"


def test_sync_template(
    mocker,
    mpt_client,
    new_product_file,
    product,
    template,
    parameter,
):
    stats = ProductStatsCollector()
    template_mock = mocker.patch(
        "swo.mpt.cli.core.products.flows.create_template", return_value=template
    )

    file_handler = ExcelFileHandler(new_product_file)
    sheet_name = constants.TAB_TEMPLATES
    values = file_handler.get_data_from_horizontal_sheet(sheet_name, constants.TEMPLATES_FIELDS)

    id_mapping = sync_templates(
        mpt_client,
        file_handler,
        product,
        values,
        {
            "PAR-4944-4118-0001": parameter,
        },
        stats,
        console.status(""),
    )

    assert id_mapping == {
        "TPL-4944-4118-0005": template,
        "TPL-4944-4118-0006": template,
    }

    a2_value = file_handler.get_cell_value_by_coordinate(sheet_name, "A2")
    a3_value = file_handler.get_cell_value_by_coordinate(sheet_name, "A3")
    assert (a2_value, a3_value) == (template.id, template.id)
    assert template_mock.mock_calls[0].args == (
        mpt_client,
        product,
        {
            "name": "CLI Order completion",
            "type": "OrderCompleted",
            "default": True,
            "content": "Test content **Azure** {{ " + parameter.id + " }}",
        },
    )
    assert template_mock.mock_calls[1].args == (
        mpt_client,
        product,
        {
            "name": "CLI order quering",
            "type": "OrderQuerying",
            "default": False,
            "content": "Test content **Azure**",
        },
    )


def test_sync_template_exception(
    mocker,
    mpt_client,
    new_product_file,
    product,
    parameter,
):
    stats = ProductStatsCollector()
    mocker.patch(
        "swo.mpt.cli.core.products.flows.create_template",
        side_effect=MPTAPIError("Error", "Error"),
    )

    file_handler = ExcelFileHandler(new_product_file)
    sheet_name = constants.TAB_TEMPLATES
    values = file_handler.get_data_from_horizontal_sheet(sheet_name, constants.TEMPLATES_FIELDS)

    sync_templates(
        mpt_client,
        file_handler,
        product,
        values,
        {
            "PAR-4944-4118-0001": parameter,
        },
        stats,
        console.status(""),
    )

    i2_value = file_handler.get_cell_value_by_coordinate(sheet_name, "I2")
    assert i2_value == "Error with response body Error"


def test_sync_product(
    mocker,
    mpt_client,
    new_product_file,
    product,
    parameter_group,
    item,
    item_group,
    uom,
    template,
    parameter,
    another_parameter,
    active_vendor_account,
    product_data_from_json,
):
    parameter_group_mock = mocker.patch(
        "swo.mpt.cli.core.products.flows.create_parameter_group", return_value=parameter_group
    )
    item_group_mock = mocker.patch(
        "swo.mpt.cli.core.products.flows.create_item_group", return_value=item_group
    )
    parameter_mock = mocker.patch(
        "swo.mpt.cli.core.products.flows.create_parameter",
        side_effect=[
            parameter,
            another_parameter,
            parameter,
            another_parameter,
            parameter,
            another_parameter,
            parameter,
            another_parameter,
        ],
    )
    item_mock = mocker.patch("swo.mpt.cli.core.products.flows.mpt_create_item", return_value=item)
    mocker.patch("swo.mpt.cli.core.products.flows.search_uom_by_name", return_value=uom)
    template_mock = mocker.patch(
        "swo.mpt.cli.core.products.flows.create_template", return_value=template
    )
    stats = ProductStatsCollector()
    product_create_mock = mocker.patch.object(
        ProductService,
        "create",
        return_value=ServiceResult(success=True, model=product_data_from_json, stats=stats),
    )

    sync_product_definition(
        mpt_client,
        new_product_file,
        ProductAction.CREATE,
        active_vendor_account,
        stats,
        console.status(""),
    )

    assert parameter_group_mock.call_count == 2
    assert item_group_mock.call_count == 2
    assert parameter_mock.call_count == 8
    assert item_mock.call_count == 2
    assert template_mock.call_count == 2

    product_create_mock.assert_called_once()


def test_sync_product_extra_columns(
    mocker,
    mpt_client,
    extra_column_product_file,
    product,
    parameter_group,
    item,
    item_group,
    uom,
    template,
    parameter,
    another_parameter,
    active_vendor_account,
    product_data_from_json,
):
    parameter_group_mock = mocker.patch(
        "swo.mpt.cli.core.products.flows.create_parameter_group", return_value=parameter_group
    )
    item_group_mock = mocker.patch(
        "swo.mpt.cli.core.products.flows.create_item_group", return_value=item_group
    )
    parameter_mock = mocker.patch(
        "swo.mpt.cli.core.products.flows.create_parameter",
        side_effect=[
            parameter,
            another_parameter,
            parameter,
            another_parameter,
            parameter,
            another_parameter,
            parameter,
            another_parameter,
        ],
    )
    item_mock = mocker.patch("swo.mpt.cli.core.products.flows.mpt_create_item", return_value=item)
    mocker.patch("swo.mpt.cli.core.products.flows.search_uom_by_name", return_value=uom)
    template_mock = mocker.patch(
        "swo.mpt.cli.core.products.flows.create_template", return_value=template
    )
    stats = ProductStatsCollector()
    product_create_mock = mocker.patch.object(
        ProductService,
        "create",
        return_value=ServiceResult(success=True, model=product_data_from_json, stats=stats),
    )

    sync_product_definition(
        mpt_client,
        extra_column_product_file,
        ProductAction.CREATE,
        active_vendor_account,
        stats,
        console.status(""),
    )

    assert parameter_group_mock.call_count == 2
    assert item_group_mock.call_count == 2
    assert parameter_mock.call_count == 8
    assert item_mock.call_count == 2
    assert template_mock.call_count == 2

    product_create_mock.assert_called_once()


def test_sync_product_exception(mocker, mpt_client, new_product_file, active_vendor_account):
    stats = ProductStatsCollector()
    product_create_mock = mocker.patch.object(
        ProductService,
        "create",
        return_value=ServiceResult(success=False, model=None, stats=stats),
    )

    sync_product_definition(
        mpt_client,
        new_product_file,
        ProductAction.CREATE,
        active_vendor_account,
        stats,
        console.status(""),
    )

    product_create_mock.assert_called_once()


def test_sync_product_update_product(
    mocker,
    mpt_client,
    new_update_product_file,
    active_vendor_account,
    uom,
    items,
):
    fake_id = "fake_id"
    retrieve_mock = mocker.patch.object(
        ProductService, "retrieve", return_value=Mock(success=True, model=Mock(id=fake_id))
    )
    update_mock = mocker.patch.object(ItemService, "update")
    stats, _ = sync_product_definition(
        mpt_client,
        new_update_product_file,
        ProductAction.UPDATE,
        active_vendor_account,
        Mock(),
        console.status(""),
    )

    retrieve_mock.assert_called_once()
    update_mock.assert_called_once()
