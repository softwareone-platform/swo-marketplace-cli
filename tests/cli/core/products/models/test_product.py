import datetime as dt

from cli.core.products.constants import (
    GENERAL_ACCOUNT_ID,
    GENERAL_ACCOUNT_NAME,
    GENERAL_CATALOG_DESCRIPTION,
    GENERAL_CREATED,
    GENERAL_EXPORT_DATE,
    GENERAL_MODIFIED,
    GENERAL_PRODUCT_DESCRIPTION,
    GENERAL_PRODUCT_ID,
    GENERAL_PRODUCT_NAME,
    GENERAL_PRODUCT_WEBSITE,
    GENERAL_STATUS,
    SETTINGS_ACTION,
    SETTINGS_SETTING,
    SETTINGS_VALUE,
)
from cli.core.products.models import DataActionEnum
from cli.core.products.models.product import ProductData, SettingsData, SettingsRecords
from freezegun import freeze_time
from mpt_api_client.resources.catalog.products import Product


def test_product_data_from_dict(product_file_data):
    result = ProductData.from_dict(product_file_data)

    assert result.id == "PRD-1234-1234-1234"
    assert result.coordinate == "B3"
    assert result.name == "Test Product Name"
    assert result.short_description == "Catalog description"
    assert result.long_description == "Product description"
    assert result.website == "https://example.com"


def test_product_data_from_json(mpt_product_data):
    with freeze_time("2025-05-30"):
        result = ProductData.from_json(Product(mpt_product_data))

    assert result.id == "PRD-0232-2541"
    assert result.name == "Adobe VIP Marketplace for Commercial"
    assert result.account_id == "ACC-9226-9856"
    assert result.account_name == "Adobe"
    assert result.short_description == (
        "Adobe's groundbreaking innovations empower everyone, everywhere to imagine, "
        "create, and bring any digital experience to life."
    )
    assert result.long_description == (
        "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwM"
        "C9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgdmlld0JveD0iMCAwIDQ4IDQ4IiBmaWxs"
        "PSJub25lIj4KICA8cGF0aCBkPSJNMTcuNzYyOCAzSDBWNDUuNDU4MkwxNy43NjI4IDNaIiB"
        "maWxsPSIjRkEwQzAwIi8+CiAgPHBhdGggZD0iTTMwLjI2MDQgM0g0OFY0NS40NTgyTDMwLj"
        "I2MDQgM1oiIGZpbGw9IiNGQTBDMDAiLz4KICA8cGF0aCBkPSJNMjQuMDExNiAxOC42NDg2T"
        "DM1LjMxNzMgNDUuNDU4MkgyNy44OTk3TDI0LjUyMDggMzYuOTIyNkgxNi4yNDY5TDI0LjAx"
        "MTYgMTguNjQ4NloiIGZpbGw9IiNGQTBDMDAiLz4KPC9zdmc+"
    )
    assert result.website == "https://www.adobe.com/"
    assert result.export_date == dt.date(2025, 5, 30)
    assert result.status == "Unpublished"
    assert result.created_date == dt.date(2024, 3, 19)
    assert result.updated_date == dt.date(2025, 6, 3)
    assert result.settings is not None


def test_product_data_to_json(product_data_from_dict):
    result = product_data_from_dict.to_json()

    assert result == {
        "name": "Adobe Commerce (CLI Test)",
        "shortDescription": "Catalog description",
        "longDescription": "Product description",
        "website": "https://example.com",
    }


def test_product_to_xlsx(product_data_from_json):
    result = product_data_from_json.to_xlsx()

    assert result == {
        GENERAL_PRODUCT_ID: "PRD-0232-2541",
        GENERAL_PRODUCT_NAME: "Adobe VIP Marketplace for Commercial",
        GENERAL_CATALOG_DESCRIPTION: "Adobe's groundbreaking innovations empower everyone, "
        "everywhere to imagine, create, and bring any digital experience to life.",
        GENERAL_PRODUCT_DESCRIPTION: "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53M"
        "y5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgdmlld0JveD0iMCAwIDQ4IDQ4IiBmaWxs"
        "PSJub25lIj4KICA8cGF0aCBkPSJNMTcuNzYyOCAzSDBWNDUuNDU4MkwxNy43NjI4IDNaIiB"
        "maWxsPSIjRkEwQzAwIi8+CiAgPHBhdGggZD0iTTMwLjI2MDQgM0g0OFY0NS40NTgyTDMwLj"
        "I2MDQgM1oiIGZpbGw9IiNGQTBDMDAiLz4KICA8cGF0aCBkPSJNMjQuMDExNiAxOC42NDg2T"
        "DM1LjMxNzMgNDUuNDU4MkgyNy44OTk3TDI0LjUyMDggMzYuOTIyNkgxNi4yNDY5TDI0LjAx"
        "MTYgMTguNjQ4NloiIGZpbGw9IiNGQTBDMDAiLz4KPC9zdmc+",
        GENERAL_PRODUCT_WEBSITE: "https://www.adobe.com/",
        GENERAL_ACCOUNT_ID: "ACC-9226-9856",
        GENERAL_ACCOUNT_NAME: "Adobe",
        GENERAL_EXPORT_DATE: dt.date(2025, 5, 30),
        GENERAL_STATUS: "Unpublished",
        GENERAL_CREATED: dt.date(2024, 3, 19),
        GENERAL_MODIFIED: dt.date(2025, 6, 3),
    }


def test_settings_data_from_dict(settings_file_data):
    result = SettingsData.from_dict({
        SETTINGS_SETTING: {"value": "Change order validation (draft)", "coordinate": "A2"},
        SETTINGS_ACTION: {"value": DataActionEnum.SKIP, "coordinate": "B2"},
        SETTINGS_VALUE: {"value": "Enabled", "coordinate": "C2"},
    })

    assert len(result.records) == 1
    setting_item = result.records[0]
    assert isinstance(setting_item, SettingsRecords)
    assert setting_item.name == "Change order validation (draft)"
    assert setting_item.setting_value == "Enabled"
    assert setting_item.coordinate == "A2"
    assert result.json_path is None


def test_settings_data_from_json(mpt_product_data):
    result = SettingsData.from_json(mpt_product_data["settings"])

    assert len(result.records) == 11
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
        SETTINGS_SETTING: {"value": "Purchase order validation (query)", "coordinate": "A10"},
        SETTINGS_ACTION: {"value": DataActionEnum.DELETE, "coordinate": "B10"},
        SETTINGS_VALUE: {"value": "Off", "coordinate": "C10"},
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
        SETTINGS_SETTING: "Item selection validation",
        SETTINGS_ACTION: "-",
        SETTINGS_VALUE: "Off",
    }
