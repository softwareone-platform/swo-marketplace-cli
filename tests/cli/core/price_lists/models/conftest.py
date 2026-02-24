import datetime as dt

import pytest
from cli.core.price_lists.constants import (
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


@pytest.fixture
def price_list_file_data():
    return {
        GENERAL_PRICELIST_ID: {"value": "PL-1", "coordinate": "B3"},
        GENERAL_CURRENCY: {"value": "USD", "coordinate": "B4"},
        GENERAL_PRODUCT_ID: {"value": "fake_product_id", "coordinate": "B5"},
        GENERAL_PRODUCT_NAME: {"value": "Test Product Name", "coordinate": "B6"},
        GENERAL_VENDOR_ID: {"value": "fake_vendor_id", "coordinate": "B7"},
        GENERAL_VENDOR_NAME: {"value": "Test Vendor Name", "coordinate": "B8"},
        GENERAL_EXPORT_DATE: {
            "value": dt.datetime(2024, 6, 1, 0, 0, tzinfo=dt.UTC),
            "coordinate": "B9",
        },
        GENERAL_PRECISION: {"value": 2, "coordinate": "B10"},
        GENERAL_DEFAULT_MARKUP: {"value": 10, "coordinate": "B11"},
        GENERAL_NOTES: {"value": "Test notes", "coordinate": "B12"},
        GENERAL_CREATED: {
            "value": dt.datetime(2024, 6, 1, 0, 0, tzinfo=dt.UTC),
            "coordinate": "B13",
        },
        GENERAL_MODIFIED: {
            "value": dt.datetime(2025, 2, 10, 0, 0, tzinfo=dt.UTC),
            "coordinate": "B14",
        },
        "type": "operations",
        EXTERNAL_ID: {"value": "test_product_com_usd_global", "coordinate": "A1"},
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
        PRICELIST_ITEMS_MODIFIED: {
            "value": dt.datetime(2025, 5, 23, 0, 0, tzinfo=dt.UTC),
            "coordinate": "M325",
        },
    }
