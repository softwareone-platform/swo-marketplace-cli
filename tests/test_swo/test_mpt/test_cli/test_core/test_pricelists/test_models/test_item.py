from datetime import date

from swo.mpt.cli.core.pricelists.models.item import ItemAction, ItemData, ItemStatus


def test_item_action_missing():
    result = ItemAction(None)

    assert result == ItemAction.SKIP


def test_item_data_from_dict(item_file_data):
    result = ItemData.from_dict(item_file_data)

    assert result.id == "PRI-3969-9403-0001-0035"
    assert result.coordinate == "A325"
    assert result.billing_frequency == "1y"
    assert result.commitment == "1y"
    assert result.erp_id == "30006419CB"
    assert result.item_id == "ITM-9939-6700-0280"
    assert result.item_name == "XD for Teams; existing XD customers only.;"
    assert result.markup == 11.1111111111111
    assert result.status == ItemStatus.DRAFT
    assert result.unit_lp == 119.88
    assert result.unit_pp == 107.88
    assert result.unit_sp is None
    assert result.vendor_id == "AO03.25842.MN"
    assert result.action == ItemAction.UPDATE
    assert result.modified_date == date(2025, 5, 23)
    assert result.type is None


def test_item_data_from_json(mpt_item_data):
    result = ItemData.from_json(mpt_item_data)

    assert result.id == "PRI-0232-2541-0002-0002"
    assert result.coordinate is None
    assert result.billing_frequency == "1y"
    assert result.commitment == "1y"
    assert result.erp_id == "1234567"
    assert result.item_id == "ITM-0232-2541-0002"
    assert result.item_name == "Creative Cloud All Apps with Adobe Stock (10 assets per month)"
    assert result.markup == 123.0
    assert result.status == ItemStatus.FOR_SALE
    assert result.unit_lp == 123.0
    assert result.unit_pp == 123.0
    assert result.unit_sp == 9328.85
    assert result.vendor_id == "65322587CA"
    assert result.action == ItemAction.SKIP
    assert result.modified_date is None
    assert result.type is None


def test_item_data_to_json(item_data_from_dict):
    result = item_data_from_dict.to_json()

    assert result["unitLP"] == 10.28
    assert result["unitPP"] == 12.1
    assert result["markup"] == 0.15
    assert result["unitSP"] == 10.55
    assert result["status"] == ItemStatus.FOR_SALE
