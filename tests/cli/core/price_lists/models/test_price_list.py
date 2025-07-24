from datetime import date

from cli.core.price_lists.models import PriceListData
from freezegun import freeze_time


def test_price_list_data_from_dict(price_list_file_data):
    result = PriceListData.from_dict(price_list_file_data)

    assert result.id == "PL-1"
    assert result.currency == "USD"
    assert result.product_id == "fake_product_id"
    assert result.product_name == "Test Product Name"
    assert result.vendor_id == "fake_vendor_id"
    assert result.vendor_name == "Test Vendor Name"
    assert result.export_date == date(2024, 6, 1)
    assert result.precision == 2
    assert result.notes == "Test notes"
    assert result.coordinate == "B3"
    assert result.default_markup == 10
    assert result.external_id == "test_product_com_usd_global"
    assert result.type == "operations"
    assert result.product == {"id": "fake_product_id"}
    assert result.is_operations() is True


def test_price_list_data_from_json(mpt_price_list_data):
    with freeze_time("2025-04-23"):
        result = PriceListData.from_json(mpt_price_list_data)

    assert result.id == "PRC-0232-2541-0002"
    assert result.currency == "USD"
    assert result.product_id == "PRD-0232-2541"
    assert result.product_name == "Adobe VIP Marketplace for Commercial"
    assert result.vendor_id == "ACC-9226-9856"
    assert result.vendor_name == "Adobe"
    assert result.export_date == date(2025, 4, 23)
    assert result.precision == 2
    assert result.notes == "another price list"
    assert result.coordinate is None
    assert result.default_markup == 42.0
    assert result.external_id is None
    assert result.type is None


def test_price_list_data_to_json(price_list_data_from_dict):
    result = price_list_data_from_dict.to_json()

    assert result["currency"] == "EUR"
    assert result["precision"] == 2
    assert result["notes"] == "Note 1"
    assert result["product"] == {"id": "PRD-0232-2541"}
    assert result["defaultMarkup"] == 10.0
    assert "externalId" not in result
