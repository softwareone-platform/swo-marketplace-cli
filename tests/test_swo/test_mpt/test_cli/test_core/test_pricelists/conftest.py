import shutil
from datetime import datetime
from pathlib import Path

import pytest
from swo.mpt.cli.core.price_lists.constants import (
    EXTERNAL_ID,
    GENERAL_CREATED,
    GENERAL_CURRENCY,
    GENERAL_DEFAULT_MARKUP,
    GENERAL_EXPORT_DATE,
    GENERAL_MODIFIED,
    GENERAL_NOTES,
    GENERAL_PRECISION,
    GENERAL_PRICELIST_ID,
    GENERAL_PRODUCT_ID,
    GENERAL_PRODUCT_NAME,
    GENERAL_VENDOR_ID,
    GENERAL_VENDOR_NAME,
    PRICELIST_ITEMS_ACTION,
    PRICELIST_ITEMS_BILLING_FREQUENCY,
    PRICELIST_ITEMS_COMMITMENT,
    PRICELIST_ITEMS_ID,
    PRICELIST_ITEMS_ITEM_ERP_ID,
    PRICELIST_ITEMS_ITEM_ID,
    PRICELIST_ITEMS_ITEM_NAME,
    PRICELIST_ITEMS_ITEM_VENDOR_ID,
    PRICELIST_ITEMS_MARKUP,
    PRICELIST_ITEMS_MODIFIED,
    PRICELIST_ITEMS_STATUS,
    PRICELIST_ITEMS_UNIT_LP,
    PRICELIST_ITEMS_UNIT_PP,
)
from swo.mpt.cli.core.price_lists.models import ItemData, PriceListData
from swo.mpt.cli.core.price_lists.models.item import ItemAction, ItemStatus


@pytest.fixture
def price_list_file_root():
    return Path("tests/pricelist_files")


@pytest.fixture
def price_list_file_path(price_list_file_root):
    return price_list_file_root / "PRC-1234-1234-1234.xlsx"


@pytest.fixture
def price_list_new_file(tmp_path, price_list_file_path):
    shutil.copyfile(price_list_file_path, tmp_path / "PRC-1234-1234-1234-copied.xlsx")
    return tmp_path / "PRC-1234-1234-1234-copied.xlsx"


# TODO: create builder for ItemData and PriceListData
@pytest.fixture
def price_list_file_data():
    return {
        GENERAL_PRICELIST_ID: {"value": "PL-1", "coordinate": "B3"},
        GENERAL_CURRENCY: {"value": "USD", "coordinate": "B4"},
        GENERAL_PRODUCT_ID: {"value": "fake_product_id", "coordinate": "B5"},
        GENERAL_PRODUCT_NAME: {"value": "Test Product Name", "coordinate": "B6"},
        GENERAL_VENDOR_ID: {"value": "fake_vendor_id", "coordinate": "B7"},
        GENERAL_VENDOR_NAME: {"value": "Test Vendor Name", "coordinate": "B8"},
        GENERAL_EXPORT_DATE: {"value": datetime(2024, 6, 1, 0, 0), "coordinate": "B9"},
        GENERAL_PRECISION: {"value": 2, "coordinate": "B10"},
        GENERAL_DEFAULT_MARKUP: {"value": 10, "coordinate": "B11"},
        GENERAL_NOTES: {"value": "Test notes", "coordinate": "B12"},
        GENERAL_CREATED: {"value": datetime(2024, 6, 1, 0, 0), "coordinate": "B13"},
        GENERAL_MODIFIED: {"value": datetime(2025, 2, 10, 0, 0), "coordinate": "B14"},
        "type": "operations",
        EXTERNAL_ID: {"value": "test_product_com_usd_global", "coordinate": "A1"},
    }


@pytest.fixture
def price_list_data_from_dict():
    return PriceListData(
        id="PRI-0232-2541-0003-0010",
        currency="EUR",
        product_id="PRD-0232-2541",
        product_name="Test Product Name",
        vendor_id="VND-0232-2541",
        vendor_name="Test Vendor Name",
        export_date="2024-06-01",
        precision=2,
        notes="Note 1",
        coordinate="B3",
        default_markup=10,
        external_id=None,
        type="operations",
    )


@pytest.fixture
def price_list_data_from_json(mpt_price_list_data):
    return PriceListData.from_json(mpt_price_list_data)


@pytest.fixture
def mpt_price_list_data():
    return {
        "id": "PRC-0232-2541-0002",
        "currency": "USD",
        "precision": 2,
        "defaultMarkup": 42.0000000000,
        "notes": "another price list",
        "externalIds": {},
        "statistics": {
            "sellers": 0,
            "listings": 0,
            "priceListItems": 609,
            "purchasePriceItems": 609,
            "purchasePriceCompleteness": 100,
            "salesPriceItems": 609,
            "salesPriceCompleteness": 100,
            "averageMarkup": 0.4128078817,
            "averageMargin": 0.0000000000,
        },
        "product": {
            "id": "PRD-0232-2541",
            "name": "Adobe VIP Marketplace for Commercial",
            "shortDescription": "Adobe’s groundbreaking innovations empower everyone, everywhere "
            "to imagine, create, and bring any digital experience to life.",
            "longDescription": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcv"
            "MjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCIgdmlld0JveD0iMCAwIDQ4ID"
            "Q4IiBmaWxsPSJub25lIj4KICA8cGF0aCBkPSJNMTcuNzYyOCAzSDBWNDUuNDU4Mkwx"
            "Ny43NjI4IDNaIiBmaWxsPSIjRkEwQzAwIi8+CiAgPHBhdGggZD0iTTMwLjI2MDQgM0"
            "g0OFY0NS40NTgyTDMwLjI2MDQgM1oiIGZpbGw9IiNGQTBDMDAiLz4KICA8cGF0aCBk"
            "PSJNMjQuMDExNiAxOC42NDg2TDM1LjMxNzMgNDUuNDU4MkgyNy44OTk3TDI0LjUyMD"
            "ggMzYuOTIyNkgxNi4yNDY5TDI0LjAxMTYgMTguNjQ4NloiIGZpbGw9IiNGQTBDMDAi"
            "Lz4KPC9zdmc+",
            "externalIds": {},
            "website": "https://www.adobe.com/",
            "icon": "/v1/catalog/products/PRD-0232-2541/icon",
            "status": "Unpublished",
            "vendor": {
                "id": "ACC-9226-9856",
                "type": "Vendor",
                "status": "Active",
                "name": "Adobe",
            },
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
                "ordersPlacedCount": 315,
                "agreementCount": 340,
                "subscriptionCount": 107,
                "requestCount": 0,
            },
            "audit": {
                "unpublished": {
                    "at": "2024-07-05T01:38:38.635Z",
                    "by": {
                        "id": "USR-0249-0848",
                        "name": "User0848",
                    },
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
                    "at": "2025-04-14T13:08:54.883Z",
                    "by": {
                        "id": "USR-0000-0031",
                        "name": "User31",
                    },
                },
            },
        },
        "vendor": {
            "id": "ACC-9226-9856",
            "externalIds": {"pyraTenantId": "1b877881-39a8-4f4e-850d-08dc2eea2f44"},
            "externalId": "ADOB",
            "type": "Vendor",
            "status": "Active",
            "serviceLevel": "Strategics",
            "address": {
                "addressLine1": "345 Park Ave",
                "city": "San Jose",
                "state": "California",
                "country": "US",
            },
            "technicalSupportEmail": "support.adobe@mpt.softwareone.com",
            "website": "https://www.adobe.com",
            "description": "Adobe jest wybitne",
            "name": "Adobe",
            "audit": {
                "created": {
                    "at": "2023-12-14T13:28:16.547Z",
                    "by": {
                        "id": "USR-0000-0001",
                        "name": "User1",
                        "icon": "/v1/accounts/users/USR-0000-0001/icon",
                    },
                },
                "updated": {
                    "at": "2025-05-12T14:05:05.098Z",
                    "by": {
                        "id": "USR-0000-0006",
                        "name": "User6",
                        "icon": "/v1/accounts/users/USR-0000-0006/icon",
                    },
                },
            },
        },
        "audit": {
            "created": {
                "at": "2024-04-04T16:26:50.982Z",
                "by": {"id": "USR-0000-0022", "name": "User22"},
            }
        },
    }


@pytest.fixture
def item_file_data():
    return {
        PRICELIST_ITEMS_ID: {"value": "PRI-3969-9403-0001-0035", "coordinate": "A325"},
        PRICELIST_ITEMS_ITEM_ID: {"value": "ITM-9939-6700-0280", "coordinate": "B325"},
        PRICELIST_ITEMS_ITEM_NAME: {
            "value": "XD for Teams; existing XD customers only.;",
            "coordinate": "C325",
        },
        PRICELIST_ITEMS_ITEM_ERP_ID: {"value": "30006419CB", "coordinate": "D325"},
        PRICELIST_ITEMS_ITEM_VENDOR_ID: {"value": "AO03.25842.MN", "coordinate": "E325"},
        PRICELIST_ITEMS_BILLING_FREQUENCY: {"value": "1y", "coordinate": "F325"},
        PRICELIST_ITEMS_COMMITMENT: {"value": "1y", "coordinate": "G325"},
        PRICELIST_ITEMS_ACTION: {"value": "update", "coordinate": "H325"},
        PRICELIST_ITEMS_UNIT_LP: {"value": 119.88, "coordinate": "I325"},
        PRICELIST_ITEMS_UNIT_PP: {"value": 107.88, "coordinate": "J325"},
        PRICELIST_ITEMS_MARKUP: {"value": 11.1111111111111, "coordinate": "K325"},
        PRICELIST_ITEMS_STATUS: {"value": "Draft", "coordinate": "L325"},
        PRICELIST_ITEMS_MODIFIED: {"value": datetime(2025, 5, 23, 0, 0), "coordinate": "M325"},
    }


@pytest.fixture
def item_data_from_json(mpt_item_data):
    return ItemData.from_json(mpt_item_data)


@pytest.fixture
def item_data_from_dict():
    return ItemData(
        id="PRI-0232-2541-0003-0010",
        billing_frequency="1y",
        commitment="1y",
        erp_id=None,
        item_id="Fake-Item-ID",
        item_name="Fake Item Name",
        markup=0.15,
        status=ItemStatus.FOR_SALE,
        unit_lp=10.28,
        unit_pp=12.1,
        unit_sp=10.55,
        vendor_id="65304887CA",
        action=ItemAction.UPDATE,
        coordinate="A38272",
        type="operations",
    )


@pytest.fixture
def mpt_item_data():
    return {
        "id": "PRI-0232-2541-0002-0002",
        "status": "ForSale",
        "unitLP": 123.00000,
        "unitPP": 123.00000,
        "markup": 123.0000000000,
        "margin": 0.0000000000,
        "unitSP": 9328.85000,
        "PPx1": 123.00000,
        "PPxM": 123.00000,
        "PPxY": 123.00000,
        "SPx1": 0.00000,
        "SPxM": 777.40000,
        "SPxY": 9328.85000,
        "priceList": {
            "id": "PRC-0232-2541-0002",
            "currency": "USD",
            "precision": 2,
            "defaultMarkup": 42.0000000000,
            "notes": "another price list",
            "externalIds": {},
            "statistics": {
                "sellers": 0,
                "listings": 0,
                "priceListItems": 609,
                "purchasePriceItems": 609,
                "purchasePriceCompleteness": 100,
                "salesPriceItems": 609,
                "salesPriceCompleteness": 100,
                "averageMarkup": 0.4128078817,
                "averageMargin": 0.0000000000,
            },
            "product": {
                "id": "PRD-0232-2541",
                "name": "[DO NOT USE] Adobe VIP Marketplace for Commercial",
                "externalIds": {},
                "icon": "/v1/catalog/products/PRD-0232-2541/icon",
                "status": "Unpublished",
            },
            "vendor": {
                "id": "ACC-9226-9856",
                "type": "Vendor",
                "status": "Active",
                "name": "Adobe",
            },
            "audit": {
                "created": {
                    "at": "2024-04-04T16:26:50.982Z",
                    "by": {"id": "USR-0000-0022", "name": "User22"},
                }
            },
        },
        "item": {
            "id": "ITM-0232-2541-0002",
            "name": "Creative Cloud All Apps with Adobe Stock (10 assets per month)",
            "description": "ITM-8351-9764 | AO03.15428.EN",
            "externalIds": {"vendor": "65322587CA", "operations": "1234567"},
            "group": {"id": "IGR-0232-2541-0001", "name": "Items"},
            "unit": {
                "id": "UNT-1916",
                "description": "When you purchase a product, a license represents your right to "
                "use software and services. Licenses are used to authenticate and "
                "activate the products on the end user's computers.",
                "name": "user",
            },
            "terms": {"period": "1y", "commitment": "1y"},
            "quantityNotApplicable": False,
            "status": "Published",
            "product": {
                "id": "PRD-0232-2541",
                "name": "[DO NOT USE] Adobe VIP Marketplace for Commercial",
                "externalIds": {},
                "icon": "/v1/catalog/products/PRD-0232-2541/icon",
                "status": "Unpublished",
            },
            "parameters": [
                {
                    "id": "PAR-0232-2541-0004",
                    "externalId": "type",
                    "type": "DropDown",
                    "name": "Type",
                    "value": "Teams",
                    "displayValue": "Teams",
                },
                {
                    "id": "PAR-0232-2541-0005",
                    "externalId": "language",
                    "type": "SingleLineText",
                    "name": "Language",
                    "value": "English - Europe",
                    "displayValue": "English - Europe",
                },
            ],
            "audit": {
                "created": {
                    "at": "2024-03-19T12:03:51.504Z",
                    "by": {"id": "USR-0000-0022", "name": "User22"},
                },
                "updated": {
                    "at": "2024-04-23T11:03:24.411Z",
                    "by": {"id": "USR-0081-7601", "name": "User7601"},
                },
            },
        },
        "audit": {
            "created": {
                "at": "2024-04-16T12:00:00.000Z",
                "by": {"id": "USR-0000-0022", "name": "User22"},
            }
        },
    }
