from cli.core.price_lists.models import PriceListData
from freezegun import freeze_time


def test_price_list_data_from_dict(date_factory, price_list_file_data):
    result = PriceListData.from_dict(price_list_file_data)

    expected_data = {
        "id": "PL-1",
        "currency": "USD",
        "product_id": "fake_product_id",
        "product_name": "Test Product Name",
        "vendor_id": "fake_vendor_id",
        "vendor_name": "Test Vendor Name",
        "export_date": date_factory("2024-06-01"),
        "precision": 2,
        "notes": "Test notes",
        "coordinate": "B3",
        "default_markup": 10,
        "external_id": "test_product_com_usd_global",
        "type": "operations",
        "product": {"id": "fake_product_id"},
    }
    assert {
        field_name: getattr(result, field_name) for field_name in expected_data
    } == expected_data
    assert result.is_operations() is True


def test_price_list_data_from_json(date_factory, mpt_price_list_data):
    with freeze_time("2025-04-23"):
        result = PriceListData.from_json(mpt_price_list_data)

    expected_data = {
        "id": "PRC-0232-2541-0002",
        "currency": "USD",
        "product_id": "PRD-0232-2541",
        "product_name": "Adobe VIP Marketplace for Commercial",
        "vendor_id": "ACC-9226-9856",
        "vendor_name": "Adobe",
        "export_date": date_factory("2025-04-23"),
        "precision": 2,
        "notes": "another price list",
        "coordinate": None,
        "default_markup": 1.0,
        "external_id": None,
        "type": None,
    }
    assert {
        field_name: getattr(result, field_name) for field_name in expected_data
    } == expected_data


def test_price_list_data_to_json(price_list_data_from_dict):
    result = price_list_data_from_dict.to_json()

    expected_data = {
        "currency": "EUR",
        "precision": 2,
        "notes": "Note 1",
        "product": {"id": "PRD-0232-2541"},
        "defaultMarkup": 1.0,
    }
    assert {field_name: result[field_name] for field_name in expected_data} == expected_data
    assert "externalId" not in result
