from cli.core.products import constants as product_constants
from cli.core.products.models import DataActionEnum
from cli.core.products.models.product import ProductData, SettingsData, SettingsRecords
from freezegun import freeze_time

SETTINGS_RECORDS_COUNT = 11


def test_product_data_from_dict(product_file_data):
    result = ProductData.from_dict(product_file_data)

    expected_data = {
        "id": "PRD-1234-1234-1234",
        "coordinate": "B3",
        "name": "Test Product Name",
        "short_description": "Catalog description",
        "long_description": "Product description",
        "website": "https://example.com",
    }
    assert {
        field_name: getattr(result, field_name) for field_name in expected_data
    } == expected_data


def test_product_data_from_json(date_factory, mpt_product_data):
    with freeze_time("2025-05-30"):
        result = ProductData.from_json(mpt_product_data)

    expected_data = {
        "id": "PRD-0232-2541",
        "name": "Adobe VIP Marketplace for Commercial",
        "account_id": "ACC-9226-9856",
        "account_name": "Adobe",
        "short_description": (
            "Adobe's groundbreaking innovations empower everyone, everywhere to imagine, "
            "create, and bring any digital experience to life."
        ),
        "long_description": (
            "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwM"
            "C9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgdmlld0JveD0iMCAwIDQ4IDQ4IiBmaWxs"
            "PSJub25lIj4KICA8cGF0aCBkPSJNMTcuNzYyOCAzSDBWNDUuNDU4MkwxNy43NjI4IDNaIiB"
            "maWxsPSIjRkEwQzAwIi8+CiAgPHBhdGggZD0iTTMwLjI2MDQgM0g0OFY0NS40NTgyTDMwLj"
            "I2MDQgM1oiIGZpbGw9IiNGQTBDMDAiLz4KICA8cGF0aCBkPSJNMjQuMDExNiAxOC42NDg2T"
            "DM1LjMxNzMgNDUuNDU4MkgyNy44OTk3TDI0LjUyMDggMzYuOTIyNkgxNi4yNDY5TDI0LjAx"
            "MTYgMTguNjQ4NloiIGZpbGw9IiNGQTBDMDAiLz4KPC9zdmc+"
        ),
        "website": "https://www.adobe.com/",
        "export_date": date_factory("2025-05-30"),
        "status": "Unpublished",
        "created_date": date_factory("2024-03-19"),
        "updated_date": date_factory("2025-06-03"),
    }
    assert {
        field_name: getattr(result, field_name) for field_name in expected_data
    } == expected_data
    assert result.settings is not None


def test_product_data_to_json(product_data_from_dict):
    result = product_data_from_dict.to_json()

    assert result == {
        "name": "Adobe Commerce (CLI Test)",
        "shortDescription": "Catalog description",
        "longDescription": "Product description",
        "website": "https://example.com",
    }


def test_product_to_xlsx(date_factory, product_data_from_json):
    result = product_data_from_json.to_xlsx()

    assert result == {
        product_constants.GENERAL_PRODUCT_ID: "PRD-0232-2541",
        product_constants.GENERAL_PRODUCT_NAME: "Adobe VIP Marketplace for Commercial",
        product_constants.GENERAL_CATALOG_DESCRIPTION: (
            "Adobe's groundbreaking innovations empower everyone, "
            "everywhere to imagine, create, and bring any digital experience to life."
        ),
        product_constants.GENERAL_PRODUCT_DESCRIPTION: (
            "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53M"
            "y5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgdmlld0JveD0iMCAwIDQ4IDQ4IiBmaWxs"
            "PSJub25lIj4KICA8cGF0aCBkPSJNMTcuNzYyOCAzSDBWNDUuNDU4MkwxNy43NjI4IDNaIiB"
            "maWxsPSIjRkEwQzAwIi8+CiAgPHBhdGggZD0iTTMwLjI2MDQgM0g0OFY0NS40NTgyTDMwLj"
            "I2MDQgM1oiIGZpbGw9IiNGQTBDMDAiLz4KICA8cGF0aCBkPSJNMjQuMDExNiAxOC42NDg2T"
            "DM1LjMxNzMgNDUuNDU4MkgyNy44OTk3TDI0LjUyMDggMzYuOTIyNkgxNi4yNDY5TDI0LjAx"
            "MTYgMTguNjQ4NloiIGZpbGw9IiNGQTBDMDAiLz4KPC9zdmc+"
        ),
        product_constants.GENERAL_PRODUCT_WEBSITE: "https://www.adobe.com/",
        product_constants.GENERAL_ACCOUNT_ID: "ACC-9226-9856",
        product_constants.GENERAL_ACCOUNT_NAME: "Adobe",
        product_constants.GENERAL_EXPORT_DATE: date_factory("2025-05-30"),
        product_constants.GENERAL_STATUS: "Unpublished",
        product_constants.GENERAL_CREATED: date_factory("2024-03-19"),
        product_constants.GENERAL_MODIFIED: date_factory("2025-06-03"),
    }


def test_settings_data_from_dict(settings_file_data):
    result = SettingsData.from_dict({
        product_constants.SETTINGS_SETTING: {
            "value": "Change order validation (draft)",
            "coordinate": "A2",
        },
        product_constants.SETTINGS_ACTION: {"value": DataActionEnum.SKIP, "coordinate": "B2"},
        product_constants.SETTINGS_VALUE: {"value": "Enabled", "coordinate": "C2"},
    })

    setting_item = result.records[0]
    expected_data = {
        "records_length": len(result.records),
        "record_type": isinstance(setting_item, SettingsRecords),
        "name": setting_item.name,
        "setting_value": setting_item.setting_value,
        "coordinate": setting_item.coordinate,
        "json_path": result.json_path,
    }
    assert expected_data == {
        "records_length": 1,
        "record_type": True,
        "name": "Change order validation (draft)",
        "setting_value": "Enabled",
        "coordinate": "A2",
        "json_path": None,
    }


def test_settings_data_from_json(mpt_product_data):
    result = SettingsData.from_json(mpt_product_data["settings"])

    assert len(result.records) == SETTINGS_RECORDS_COUNT
    assert isinstance(result.records[0], SettingsRecords)
    assert result.json_path is None


def test_settings_data_to_xlsx(product_data_from_dict):
    result = product_data_from_dict.settings.to_json()

    assert result == {
        "settings": {
            "productOrdering": False,
            "preValidation": {"changeOrderDraft": True},
        }
    }


def test_setting_item_from_dict(settings_file_data):
    result = SettingsRecords.from_dict({
        product_constants.SETTINGS_SETTING: {
            "value": "Purchase order validation (query)",
            "coordinate": "A10",
        },
        product_constants.SETTINGS_ACTION: {"value": DataActionEnum.DELETE, "coordinate": "B10"},
        product_constants.SETTINGS_VALUE: {"value": "Off", "coordinate": "C10"},
    })

    assert result.name == "Purchase order validation (query)"
    assert result.setting_value == "Off"
    assert result.coordinate == "A10"
    assert result.action == DataActionEnum.DELETE


def test_setting_item_from_json(mpt_product_data):
    result = SettingsRecords.from_json({"name": "Product requests", "value": False})

    assert result.name == "Product requests"
    assert result.setting_value == "Off"
    assert result.action == DataActionEnum.SKIP


def test_setting_item_from_json_enabled(mpt_product_data):
    result = SettingsRecords.from_json({"name": "Change order validation (draft)", "value": True})

    assert result.name == "Change order validation (draft)"
    assert result.setting_value == "Enabled"
    assert result.action == DataActionEnum.SKIP


def test_setting_item_to_json():
    result = SettingsRecords(name="Item selection validation", setting_value="Off").to_json()

    assert result == {}


def test_setting_item_to_xlsx():
    result = SettingsRecords(name="Item selection validation", setting_value="Off").to_xlsx()

    assert result == {
        product_constants.SETTINGS_SETTING: "Item selection validation",
        product_constants.SETTINGS_ACTION: "-",
        product_constants.SETTINGS_VALUE: "Off",
    }
