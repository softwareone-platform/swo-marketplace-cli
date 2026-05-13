import math

import pytest
from cli.core.price_lists.models.item import ItemAction, ItemData, ItemStatus


def test_item_action_from_raw_none():
    result = ItemAction.from_raw(None)

    assert result == ItemAction.SKIP


def test_item_data_from_dict(item_file_data):
    result = ItemData.from_dict(item_file_data)

    expected_data = {
        "id": "PRI-3969-9403-0001-0035",
        "coordinate": "A325",
        "billing_frequency": "1y",
        "commitment": "1y",
        "erp_id": "30006419CB",
        "item_id": "ITM-9939-6700-0280",
        "item_name": "XD for Teams; existing XD customers only.;",
        "markup": pytest.approx(11.1111111111111),
        "status": ItemStatus.DRAFT,
        "unit_lp": pytest.approx(119.88),
        "unit_pp": pytest.approx(107.88),
        "unit_sp": None,
        "vendor_id": "AO03.25842.MN",
        "action": ItemAction.UPDATE,
        "type": None,
    }
    assert {
        field_name: getattr(result, field_name) for field_name in expected_data
    } == expected_data


def test_item_data_from_json(mpt_item_data):
    result = ItemData.from_json(mpt_item_data)

    expected_data = {
        "id": "PRI-0232-2541-0002-0002",
        "coordinate": None,
        "billing_frequency": "1y",
        "commitment": "1y",
        "erp_id": "1234567",
        "item_id": "ITM-0232-2541-0002",
        "item_name": "Creative Cloud All Apps with Adobe Stock (10 assets per month)",
        "markup": pytest.approx(123.0),
        "status": ItemStatus.FOR_SALE,
        "unit_lp": pytest.approx(123.0),
        "unit_pp": pytest.approx(123.0),
        "unit_sp": pytest.approx(9328.85),
        "vendor_id": "65322587CA",
        "action": ItemAction.SKIP,
        "modified_date": None,
        "type": None,
    }
    assert {
        field_name: getattr(result, field_name) for field_name in expected_data
    } == expected_data


def test_item_data_to_json(item_data_from_dict):
    result = item_data_from_dict.to_json()

    assert math.isclose(result["unitLP"], 10.28)
    assert math.isclose(result["unitPP"], 12.1)
    assert math.isclose(result["markup"], 0.15)
    assert math.isclose(result["unitSP"], 10.55)
    assert result["status"] == ItemStatus.FOR_SALE
