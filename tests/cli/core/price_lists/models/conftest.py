import datetime as dt

import pytest
from cli.core.price_lists import constants as price_list_constants


@pytest.fixture
def price_list_file_data():
    return {
        price_list_constants.GENERAL_PRICELIST_ID: {"value": "PL-1", "coordinate": "B3"},
        price_list_constants.GENERAL_CURRENCY: {"value": "USD", "coordinate": "B4"},
        price_list_constants.GENERAL_PRODUCT_ID: {"value": "fake_product_id", "coordinate": "B5"},
        price_list_constants.GENERAL_PRODUCT_NAME: {
            "value": "Test Product Name",
            "coordinate": "B6",
        },
        price_list_constants.GENERAL_VENDOR_ID: {"value": "fake_vendor_id", "coordinate": "B7"},
        price_list_constants.GENERAL_VENDOR_NAME: {"value": "Test Vendor Name", "coordinate": "B8"},
        price_list_constants.GENERAL_EXPORT_DATE: {
            "value": dt.datetime(2024, 6, 1, 0, 0, tzinfo=dt.UTC),
            "coordinate": "B9",
        },
        price_list_constants.GENERAL_PRECISION: {"value": 2, "coordinate": "B10"},
        price_list_constants.GENERAL_DEFAULT_MARKUP: {"value": 10, "coordinate": "B11"},
        price_list_constants.GENERAL_NOTES: {"value": "Test notes", "coordinate": "B12"},
        price_list_constants.GENERAL_CREATED: {
            "value": dt.datetime(2024, 6, 1, 0, 0, tzinfo=dt.UTC),
            "coordinate": "B13",
        },
        price_list_constants.GENERAL_MODIFIED: {
            "value": dt.datetime(2025, 2, 10, 0, 0, tzinfo=dt.UTC),
            "coordinate": "B14",
        },
        "type": "operations",
        price_list_constants.EXTERNAL_ID: {
            "value": "test_product_com_usd_global",
            "coordinate": "A1",
        },
    }


@pytest.fixture
def item_file_data():
    return {
        price_list_constants.PRICELIST_ITEMS_ID: {
            "value": "PRI-3969-9403-0001-0035",
            "coordinate": "A325",
        },
        price_list_constants.PRICELIST_ITEMS_ITEM_ID: {
            "value": "ITM-9939-6700-0280",
            "coordinate": "B325",
        },
        price_list_constants.PRICELIST_ITEMS_ITEM_NAME: {
            "value": "XD for Teams; existing XD customers only.;",
            "coordinate": "C325",
        },
        price_list_constants.PRICELIST_ITEMS_ITEM_ERP_ID: {
            "value": "30006419CB",
            "coordinate": "D325",
        },
        price_list_constants.PRICELIST_ITEMS_ITEM_VENDOR_ID: {
            "value": "AO03.25842.MN",
            "coordinate": "E325",
        },
        price_list_constants.PRICELIST_ITEMS_BILLING_FREQUENCY: {
            "value": "1y",
            "coordinate": "F325",
        },
        price_list_constants.PRICELIST_ITEMS_COMMITMENT: {"value": "1y", "coordinate": "G325"},
        price_list_constants.PRICELIST_ITEMS_ACTION: {"value": "update", "coordinate": "H325"},
        price_list_constants.PRICELIST_ITEMS_UNIT_LP: {"value": 119.88, "coordinate": "I325"},
        price_list_constants.PRICELIST_ITEMS_UNIT_PP: {"value": 107.88, "coordinate": "J325"},
        price_list_constants.PRICELIST_ITEMS_MARKUP: {
            "value": 11.1111111111111,
            "coordinate": "K325",
        },
        price_list_constants.PRICELIST_ITEMS_STATUS: {"value": "Draft", "coordinate": "L325"},
        price_list_constants.PRICELIST_ITEMS_MODIFIED: {
            "value": dt.datetime(2025, 5, 23, 0, 0, tzinfo=dt.UTC),
            "coordinate": "M325",
        },
    }
