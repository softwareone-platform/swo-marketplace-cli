import pytest
from swo.mpt.cli.core.products.models import ItemActionEnum, ItemData


def test_item_data_from_dict(item_file_data):
    result = ItemData.from_dict(item_file_data)

    assert result.id == "PRI-3969-9403-0001-0035"
    assert result.commitment == "1y"
    assert result.description == "Description"
    assert result.group_id == "IGR-4944-4118-0002"
    assert result.name == "XD for Teams; existing XD customers only.;"
    assert result.period == "1m"
    assert result.quantity_not_applicable is True
    assert result.unit_id == "UNT-1916"
    assert result.vendor_id == "30006419CB"
    assert result.coordinate == "A325"


def test_item_data_from_json(mpt_item_data):
    result = ItemData.from_json(mpt_item_data)

    assert result.id == "ITM-0232-2541-0001"
    assert result.name == "Creative Cloud All Apps with Adobe Stock (10 assets per month)"
    assert result.terms == {"period": "one-time"}


def test_item_data_to_json(item_data_from_dict):
    result = item_data_from_dict.to_json()

    assert result["name"] == "XD for Teams; existing XD customers only.;"
    assert result["description"] == "Description"
    assert result["externalIds"] == {"vendor": "NAV12345"}
    assert result["group"] == {"id": "IGR-4944-4118-0002"}
    assert result["product"] == {"id": "PRD-0232-2541"}
    assert result["quantityNotApplicable"] is True
    assert result["terms"] == {"period": "1m", "commitment": "1y"}
    assert result["unit"] == {"id": "UNT-1916"}
    assert result["parameters"] == []


@pytest.mark.parametrize(
    ("action", "attr"),
    [
        (ItemActionEnum.CREATE, "to_create"),
        (ItemActionEnum.PUBLISH, "to_publish"),
        (ItemActionEnum.REVIEW, "to_review"),
        (ItemActionEnum.SKIP, "to_skip"),
        (ItemActionEnum.SKIPPED, "to_skip"),
        (ItemActionEnum.UNPUBLISH, "to_unpublish"),
        (ItemActionEnum.UPDATE, "to_update"),
    ],
)
def test_item_to_create(action, attr, item_data_from_dict):
    item_data_from_dict.action = action

    result = getattr(item_data_from_dict, attr)

    assert result is True
