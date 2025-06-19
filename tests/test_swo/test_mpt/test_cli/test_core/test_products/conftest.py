import shutil
from datetime import datetime
from pathlib import Path

import pytest
from swo.mpt.cli.core.products.constants import (
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
    ITEMS_ACTION,
    ITEMS_BILLING_FREQUENCY,
    ITEMS_COMMITMENT_TERM,
    ITEMS_CREATED,
    ITEMS_DESCRIPTION,
    ITEMS_ERP_ITEM_ID,
    ITEMS_GROUP_ID,
    ITEMS_GROUP_NAME,
    ITEMS_ID,
    ITEMS_MODIFIED,
    ITEMS_NAME,
    ITEMS_QUANTITY_APPLICABLE,
    ITEMS_STATUS,
    ITEMS_UNIT_ID,
    ITEMS_UNIT_NAME,
    ITEMS_VENDOR_ITEM_ID,
)
from swo.mpt.cli.core.products.models import ItemData, ProductData, SettingsData
from swo.mpt.cli.core.products.models.items import ItemAction


@pytest.fixture
def product_file_root():
    return Path("tests/product_files")


@pytest.fixture
def product_file_path(product_file_root):
    return product_file_root / "PRD-1234-1234-1234-file.xlsx"


@pytest.fixture
def product_new_file(tmp_path, product_file_path):
    shutil.copyfile(product_file_path, tmp_path / "PRD-1234-1234-1234-copied.xlsx")
    return tmp_path / "PRD-1234-1234-1234-copied.xlsx"


@pytest.fixture
def product_file_data():
    return {
        GENERAL_PRODUCT_ID: {"value": "PRD-1234-1234-1234", "coordinate": "B3"},
        GENERAL_PRODUCT_NAME: {"value": "Test Product Name", "coordinate": "B4"},
        GENERAL_ACCOUNT_ID: {"value": "ACC-1234-1234", "coordinate": "B5"},
        GENERAL_ACCOUNT_NAME: {"value": "Test Account Name", "coordinate": "B6"},
        GENERAL_EXPORT_DATE: {"value": datetime(2024, 1, 1, 0, 0), "coordinate": "B7"},
        GENERAL_PRODUCT_WEBSITE: {"value": "https://example.com", "coordinate": "B8"},
        GENERAL_CATALOG_DESCRIPTION: {"value": "Catalog description", "coordinate": "B9"},
        GENERAL_PRODUCT_DESCRIPTION: {"value": "Product description", "coordinate": "B10"},
        GENERAL_STATUS: {"value": "Draft", "coordinate": "B11"},
        GENERAL_CREATED: {"value": datetime(2024, 1, 1, 0, 0), "coordinate": "B12"},
        GENERAL_MODIFIED: {"value": datetime(2024, 1, 1, 0, 0), "coordinate": "B13"},
    }


@pytest.fixture
def product_data_from_dict():
    return ProductData(
        id="PRD-1234-1234-1234",
        name="Adobe Commerce (CLI Test)",
        account_id="ACC-1234-1234",
        account_name="Adobe",
        export_date=datetime(2024, 1, 1, 0, 0),
        website="https://example.com",
        short_description="Catalog description",
        long_description="Product description",
        status="Draft",
        created_date=datetime(2024, 1, 1, 0, 0),
        updated_date=datetime(2024, 1, 1, 0, 0),
        coordinate="B3",
        settings=SettingsData(),
    )


@pytest.fixture
def product_data_from_json(mpt_product_data):
    return ProductData.from_json(mpt_product_data)


@pytest.fixture
def mpt_product_data():
    return {
        "id": "PRD-0232-2541",
        "name": "Adobe VIP Marketplace for Commercial",
        "shortDescription": "Adobe’s groundbreaking innovations empower everyone, everywhere "
        "to imagine, create, and bring any digital experience to life.",
        "longDescription": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwM"
        "C9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgdmlld0JveD0iMCAwIDQ4IDQ4IiBmaWxs"
        "PSJub25lIj4KICA8cGF0aCBkPSJNMTcuNzYyOCAzSDBWNDUuNDU4MkwxNy43NjI4IDNaIiB"
        "maWxsPSIjRkEwQzAwIi8+CiAgPHBhdGggZD0iTTMwLjI2MDQgM0g0OFY0NS40NTgyTDMwLj"
        "I2MDQgM1oiIGZpbGw9IiNGQTBDMDAiLz4KICA8cGF0aCBkPSJNMjQuMDExNiAxOC42NDg2T"
        "DM1LjMxNzMgNDUuNDU4MkgyNy44OTk3TDI0LjUyMDggMzYuOTIyNkgxNi4yNDY5TDI0LjAx"
        "MTYgMTguNjQ4NloiIGZpbGw9IiNGQTBDMDAiLz4KPC9zdmc+",
        "externalIds": {"operations": ""},
        "website": "https://www.adobe.com/",
        "icon": "/v1/catalog/products/PRD-0232-2541/icon",
        "status": "Unpublished",
        "vendor": {"id": "ACC-9226-9856", "type": "Vendor", "status": "Active", "name": "Adobe"},
        "settings": {
            "productOrdering": True,
            "productRequests": {"enabled": False},
            "itemSelection": True,
            "orderQueueChanges": False,
            "preValidation": {
                "purchaseOrderDraft": True,
                "purchaseOrderQuerying": True,
                "changeOrderDraft": True,
                "configurationOrderDraft": False,
                "terminationOrder": True,
                "productRequest": False,
            },
            "splitBilling": {"enabled": False},
            "subscriptionCessation": {"enabled": True, "mode": "Termination"},
        },
        "statistics": {
            "itemCount": 77,
            "ordersPlacedCount": 317,
            "agreementCount": 340,
            "subscriptionCount": 107,
            "requestCount": 0,
        },
        "audit": {
            "unpublished": {
                "at": "2024-07-05T01:38:38.635Z",
                "by": {"id": "USR-0249-0848", "name": "User848"},
            },
            "created": {
                "at": "2024-03-19T11:16:57.932Z",
                "by": {
                    "id": "USR-0000-0022",
                    "name": "User22",
                    "icon": "/v1/accounts/users/USR-0000-0022/icon",
                },
            },
            "updated": {
                "at": "2025-06-03T13:06:19.743Z",
                "by": {
                    "id": "USR-0000-0032",
                    "name": "User32",
                    "icon": "/v1/accounts/users/USR-0000-0032/icon",
                },
            },
        },
    }


@pytest.fixture
def item_file_data():
    return {
        ITEMS_ID: {"value": "PRI-3969-9403-0001-0035", "coordinate": "A325"},
        ITEMS_NAME: {
            "value": "XD for Teams; existing XD customers only.;",
            "coordinate": "B325",
        },
        ITEMS_ACTION: {"value": "update", "coordinate": "C325"},
        ITEMS_VENDOR_ITEM_ID: {"value": "30006419CB", "coordinate": "D325"},
        ITEMS_ERP_ITEM_ID: {"value": "NAV12345", "coordinate": "E325"},
        ITEMS_DESCRIPTION: {"value": "Description", "coordinate": "F325"},
        ITEMS_BILLING_FREQUENCY: {"value": "1m", "coordinate": "G325"},
        ITEMS_COMMITMENT_TERM: {"value": "1y", "coordinate": "H325"},
        ITEMS_STATUS: {"value": "Published", "coordinate": "I325"},
        ITEMS_GROUP_ID: {"value": "IGR-4944-4118-0002", "coordinate": "J325"},
        ITEMS_GROUP_NAME: {"value": "Default Group", "coordinate": "K325"},
        ITEMS_UNIT_ID: {"value": "UNT-1916", "coordinate": "L325"},
        ITEMS_UNIT_NAME: {"value": "User", "coordinate": "M325"},
        ITEMS_QUANTITY_APPLICABLE: {"value": "True", "coordinate": "N325"},
        ITEMS_CREATED: {"value": datetime(2025, 5, 23, 0, 0), "coordinate": "Q325"},
        ITEMS_MODIFIED: {"value": datetime(2025, 5, 23, 0, 0), "coordinate": "R325"},
    }


@pytest.fixture
def item_data_from_json(mpt_item_data):
    return ItemData.from_json(mpt_item_data)


@pytest.fixture
def item_data_from_dict():
    return ItemData(
        id="PRI-3969-9403-0001-0035",
        commitment="1y",
        description="Description",
        group_id="IGR-4944-4118-0002",
        name="XD for Teams; existing XD customers only.;",
        period="1m",
        product_id="PRD-0232-2541",
        quantity_not_applicable=True,
        unit_id="UNT-1916",
        vendor_id="NAV12345",
        status="Published",
        action=ItemAction.UPDATE,
        coordinate="A38272",
        item_type="vendor",
    )


@pytest.fixture
def mpt_item_data():
    return {
        "id": "ITM-0232-2541-0001",
        "name": "Creative Cloud All Apps with Adobe Stock (10 assets per month)",
        "description": "ITM-8351-9764 | AO03.15428.EN",
        "externalIds": {"vendor": "65322587CA"},
        "group": {"id": "IGR-0232-2541-0001", "name": "Items"},
        "unit": {
            "id": "UNT-1916",
            "description": "When you purchase a product, a license represents your right to"
            "use software and services. Licenses are used to authenticate and "
            "activate the products on the end user's computers.",
            "name": "user",
        },
        "terms": {"period": "one-time"},
        "quantityNotApplicable": False,
        "status": "Draft",
        "product": {
            "id": "PRD-0232-2541",
            "name": "Adobe VIP Marketplace for Commercial",
            "externalIds": {"operations": ""},
            "icon": "/v1/catalog/products/PRD-0232-2541/icon",
            "status": "Unpublished",
        },
        "audit": {
            "created": {
                "at": "2024-03-19T12:03:51.060Z",
                "by": {"id": "USR-0000-0022", "name": "User22"},
            },
            "updated": {
                "at": "2024-03-27T08:56:26.539Z",
                "by": {"id": "USR-0000-0055", "name": "User55"},
            },
        },
    }
