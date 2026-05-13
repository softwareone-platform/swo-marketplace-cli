import datetime as dt

from cli.core.products import constants as product_constants
from cli.core.products.models import ItemGroupData


def test_item_group_data_from_dict(item_group_file_data):
    result = ItemGroupData.from_dict(item_group_file_data)

    expected_data = {
        "id": "IGR-0232-2541-0001",
        "name": "Items",
        "action": "-",
        "label": "Items",
        "display_order": 100,
        "description": "Default item group",
        "default": True,
        "multiple": True,
        "required": True,
    }
    assert {
        field_name: getattr(result, field_name) for field_name in expected_data
    } == expected_data


def test_item_group_data_from_json(mpt_item_group_data):
    result = ItemGroupData.from_json(mpt_item_group_data)

    expected_data = {
        "id": "IGR-0232-2541-0001",
        "name": "Items",
        "label": "Items",
        "description": "Default item group",
        "display_order": 100,
        "default": True,
        "multiple": True,
        "required": True,
        "created_date": dt.date(2024, 3, 19),
        "updated_date": None,
    }
    assert {
        field_name: getattr(result, field_name) for field_name in expected_data
    } == expected_data


def test_item_group_data_to_json(item_group_data_from_dict):
    result = item_group_data_from_dict.to_json()

    assert result == {
        "name": "Items",
        "label": "Select items",
        "description": (
            "About this step:\n"
            "1. If you are creating a Change order for an existing agreement, you may add items "
            "or increase\nthe quantities of existing subscriptions.\n"
            "2. If you are creating a Purchase order for a new cloud account, you may add new "
            "items and set the\nquantities of those items.\n"
            "3. If you are creating a Purchase order to migrate from Adobe VIP, the items will "
            "be added for you.\nYou may not add items or adjust the quantity of items. You will "
            "not be billed for this order until\nyour anniversary date since these items have "
            "already been paid for under the Adobe VIP program for\nthe current term."
        ),
        "displayOrder": 10,
        "default": True,
        "multiple": True,
        "required": True,
    }


def test_item_group_to_xlsx(item_group_data_from_json):
    result = item_group_data_from_json.to_xlsx()

    assert result == {
        product_constants.ITEMS_GROUPS_ID: "IGR-0232-2541-0001",
        product_constants.ITEMS_GROUPS_NAME: "Items",
        product_constants.ITEMS_GROUPS_ACTION: "-",
        product_constants.ITEMS_GROUPS_LABEL: "Items",
        product_constants.ITEMS_GROUPS_DISPLAY_ORDER: 100,
        product_constants.ITEMS_GROUPS_DESCRIPTION: "Default item group",
        product_constants.ITEMS_GROUPS_DEFAULT: "True",
        product_constants.ITEMS_GROUPS_MULTIPLE_CHOICES: "True",
        product_constants.ITEMS_GROUPS_REQUIRED: "True",
        product_constants.ITEMS_GROUPS_CREATED: dt.date(2024, 3, 19),
        product_constants.ITEMS_GROUPS_MODIFIED: None,
    }
