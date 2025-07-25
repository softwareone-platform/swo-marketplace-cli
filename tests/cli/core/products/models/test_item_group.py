from datetime import date

from cli.core.products.constants import (
    ITEMS_GROUPS_ACTION,
    ITEMS_GROUPS_CREATED,
    ITEMS_GROUPS_DEFAULT,
    ITEMS_GROUPS_DESCRIPTION,
    ITEMS_GROUPS_DISPLAY_ORDER,
    ITEMS_GROUPS_ID,
    ITEMS_GROUPS_LABEL,
    ITEMS_GROUPS_MODIFIED,
    ITEMS_GROUPS_MULTIPLE_CHOICES,
    ITEMS_GROUPS_NAME,
    ITEMS_GROUPS_REQUIRED,
)
from cli.core.products.models import ItemGroupData


def test_item_group_data_from_dict(item_group_file_data):
    result = ItemGroupData.from_dict(item_group_file_data)

    assert result.id == "IGR-0232-2541-0001"
    assert result.name == "Items"
    assert result.action == "-"
    assert result.label == "Items"
    assert result.display_order == 100
    assert result.description == "Default item group"
    assert result.default is True
    assert result.multiple is True
    assert result.required is True


def test_item_group_data_from_json(mpt_item_group_data):
    result = ItemGroupData.from_json(mpt_item_group_data)

    assert result.id == "IGR-0232-2541-0001"
    assert result.name == "Items"
    assert result.label == "Items"
    assert result.description == "Default item group"
    assert result.display_order == 100
    assert result.default is True
    assert result.multiple is True
    assert result.required is True
    assert result.created_date == date(2024, 3, 19)
    assert result.updated_date is None


def test_item_group_data_to_json(item_group_data_from_dict):
    result = item_group_data_from_dict.to_json()

    assert result == {
        "name": "Items",
        "label": "Select items",
        "description": """About this step:
1. If you are creating a Change order for an existing agreement, you may add items or increase
the quantities of existing subscriptions.
2. If you are creating a Purchase order for a new cloud account, you may add new items and set the
quantities of those items.
3. If you are creating a Purchase order to migrate from Adobe VIP, the items will be added for you.
You may not add items or adjust the quantity of items. You will not be billed for this order until
your anniversary date since these items have already been paid for under the Adobe VIP program for
the current term.""",
        "displayOrder": 10,
        "default": True,
        "multiple": True,
        "required": True,
    }


def test_item_group_to_xlsx(item_group_data_from_json):
    result = item_group_data_from_json.to_xlsx()

    assert result == {
        ITEMS_GROUPS_ID: "IGR-0232-2541-0001",
        ITEMS_GROUPS_NAME: "Items",
        ITEMS_GROUPS_ACTION: "-",
        ITEMS_GROUPS_LABEL: "Items",
        ITEMS_GROUPS_DISPLAY_ORDER: 100,
        ITEMS_GROUPS_DESCRIPTION: "Default item group",
        ITEMS_GROUPS_DEFAULT: "True",
        ITEMS_GROUPS_MULTIPLE_CHOICES: "True",
        ITEMS_GROUPS_REQUIRED: "True",
        ITEMS_GROUPS_CREATED: date(2024, 3, 19),
        ITEMS_GROUPS_MODIFIED: None,
    }
