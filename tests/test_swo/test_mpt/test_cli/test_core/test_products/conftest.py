import shutil
from datetime import datetime
from pathlib import Path

import pytest
from freezegun import freeze_time
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
    ITEMS_GROUPS_ACTION,
    ITEMS_GROUPS_CREATED,
    ITEMS_GROUPS_DEFAULT,
    ITEMS_GROUPS_DESCRIPTION,
    ITEMS_GROUPS_DISPLAY_ORDER,
    ITEMS_GROUPS_ID,
    ITEMS_GROUPS_LABEL,
    ITEMS_GROUPS_MODIFIED,
    ITEMS_GROUPS_MULTIPLE_CHOICES,
    ITEMS_GROUPS_NAME,
    ITEMS_GROUPS_REQUIRED,
    ITEMS_ID,
    ITEMS_MODIFIED,
    ITEMS_NAME,
    ITEMS_QUANTITY_APPLICABLE,
    ITEMS_STATUS,
    ITEMS_UNIT_ID,
    ITEMS_UNIT_NAME,
    ITEMS_VENDOR_ITEM_ID,
    PARAMETERS_ACTION,
    PARAMETERS_CONSTRAINTS,
    PARAMETERS_CREATED,
    PARAMETERS_DESCRIPTION,
    PARAMETERS_DISPLAY_ORDER,
    PARAMETERS_EXTERNALID,
    PARAMETERS_GROUP_ID,
    PARAMETERS_GROUP_NAME,
    PARAMETERS_GROUPS_CREATED,
    PARAMETERS_GROUPS_DEFAULT,
    PARAMETERS_GROUPS_DESCRIPTION,
    PARAMETERS_GROUPS_DISPLAY_ORDER,
    PARAMETERS_GROUPS_ID,
    PARAMETERS_GROUPS_LABEL,
    PARAMETERS_GROUPS_MODIFIED,
    PARAMETERS_GROUPS_NAME,
    PARAMETERS_ID,
    PARAMETERS_MODIFIED,
    PARAMETERS_NAME,
    PARAMETERS_OPTIONS,
    PARAMETERS_PHASE,
    PARAMETERS_TYPE,
    TEMPLATES_ACTION,
    TEMPLATES_CONTENT,
    TEMPLATES_CREATED,
    TEMPLATES_DEFAULT,
    TEMPLATES_ID,
    TEMPLATES_MODIFIED,
    TEMPLATES_NAME,
    TEMPLATES_TYPE,
)
from swo.mpt.cli.core.products.models import (
    AgreementParametersData,
    ItemData,
    ItemGroupData,
    ParameterGroupData,
    ProductData,
    SettingsData,
    TemplateData,
)
from swo.mpt.cli.core.products.models.items import ItemAction
from swo.mpt.cli.core.products.models.product import SettingsItem


@pytest.fixture
def product_file_root():
    return Path("tests/product_files")


@pytest.fixture
def product_empty_file(product_file_root):
    return product_file_root / "PRD-0000-0000-empty.xlsx"


@pytest.fixture
def product_file_path(product_file_root):
    return product_file_root / "PRD-1234-1234-1234-file.xlsx"


@pytest.fixture
def product_new_file(tmp_path, product_file_path):
    shutil.copyfile(product_file_path, tmp_path / "PRD-1234-1234-1234-copied.xlsx")
    return str(tmp_path / "PRD-1234-1234-1234-copied.xlsx")


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
        settings=SettingsData(items=[SettingsItem(name="Item selection validation", value="Off")]),
    )


@pytest.fixture
@freeze_time("2025-05-30")
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
        unit_coordinate="J38272",
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


@pytest.fixture
def item_group_file_data():
    return {
        ITEMS_GROUPS_ID: {"value": "IGR-0232-2541-0001", "coordinate": "A10234"},
        ITEMS_GROUPS_NAME: {"value": "Items", "coordinate": "B10234"},
        ITEMS_GROUPS_ACTION: {"value": "-", "coordinate": "C10234"},
        ITEMS_GROUPS_LABEL: {"value": "Items", "coordinate": "D10234"},
        ITEMS_GROUPS_DISPLAY_ORDER: {"value": 100, "coordinate": "E10234"},
        ITEMS_GROUPS_DESCRIPTION: {"value": "Default item group", "coordinate": "F10234"},
        ITEMS_GROUPS_DEFAULT: {"value": "True", "coordinate": "G10234"},
        ITEMS_GROUPS_MULTIPLE_CHOICES: {"value": "True", "coordinate": "H10234"},
        ITEMS_GROUPS_REQUIRED: {"value": "True", "coordinate": "I10234"},
        ITEMS_GROUPS_CREATED: {"value": datetime(2025, 6, 23, 0, 0), "coordinate": "J10234"},
        ITEMS_GROUPS_MODIFIED: {"value": datetime(2025, 6, 23, 0, 0), "coordinate": "K10234"},
    }


@pytest.fixture
def item_group_data_from_json(mpt_item_group_data):
    return ItemGroupData.from_json(mpt_item_group_data)


@pytest.fixture
def item_group_data_from_dict():
    return ItemGroupData(
        id="IGR-0400-9557-0002",
        coordinate="J2",
        name="Items",
        label="Select items",
        description="""About this step:
1. If you are creating a Change order for an existing agreement, you may add items or increase
the quantities of existing subscriptions.
2. If you are creating a Purchase order for a new cloud account, you may add new items and set the
quantities of those items.
3. If you are creating a Purchase order to migrate from Adobe VIP, the items will be added for you.
You may not add items or adjust the quantity of items. You will not be billed for this order until
your anniversary date since these items have already been paid for under the Adobe VIP program for
the current term.""",
        display_order=10,
        default=True,
        multiple=True,
        required=True,
    )


@pytest.fixture
def mpt_item_group_data():
    return {
        "id": "IGR-0232-2541-0001",
        "name": "Items",
        "label": "Items",
        "description": "Default item group",
        "displayOrder": 100,
        "default": True,
        "multiple": True,
        "required": True,
        "itemCount": 761,
        "product": {
            "id": "PRD-0232-2541",
            "name": "[DO NOT USE] Adobe VIP Marketplace for Commercial",
            "externalIds": {"operations": ""},
            "icon": "/v1/catalog/products/PRD-0232-2541/icon",
            "status": "Unpublished",
        },
        "audit": {
            "created": {
                "at": "2024-03-19T11:16:57.932Z",
                "by": {
                    "id": "USR-0000-0022",
                    "name": "User22",
                    "icon": "/v1/accounts/users/USR-0000-0022/icon",
                },
            }
        },
    }


@pytest.fixture
def parameters_file_data():
    return {
        PARAMETERS_ID: {"value": "PAR-5159-0756-0001", "coordinate": "A325"},
        PARAMETERS_NAME: {"value": "Agreement type", "coordinate": "B325"},
        PARAMETERS_EXTERNALID: {"value": "agreementType", "coordinate": "C325"},
        PARAMETERS_ACTION: {"value": "-", "coordinate": "D325"},
        PARAMETERS_PHASE: {"value": "Order", "coordinate": "E325"},
        PARAMETERS_TYPE: {"value": "Choice", "coordinate": "F325"},
        PARAMETERS_DESCRIPTION: {
            "value": "When you are creating a new agreement with SoftwareOne, you have the option "
            "to create a new Adobe VIP Marketplace account or migrate your existing Adobe "
            "VIP account to Adobe VIP Marketplace.",
            "coordinate": "G325",
        },
        PARAMETERS_DISPLAY_ORDER: {"value": 101, "coordinate": "H325"},
        PARAMETERS_GROUP_ID: {"value": "PGR-5159-0756-0002", "coordinate": "I325"},
        PARAMETERS_GROUP_NAME: {"value": "Agreement", "coordinate": "J325"},
        PARAMETERS_OPTIONS: {
            "value": """{"defaultValue": "Buyer","hintText": "Address.","label": "Address"}""",
            "coordinate": "K325",
        },
        PARAMETERS_CONSTRAINTS: {
            "value": (
                """{"hidden": false, "readonly": false, "optional": false, "required": true}"""
            ),
            "coordinate": "L325",
        },
        PARAMETERS_CREATED: {"value": datetime(2024, 5, 23, 0, 0), "coordinate": "M325"},
        PARAMETERS_MODIFIED: {"value": datetime(2024, 8, 14, 0, 0), "coordinate": "N325"},
    }


@pytest.fixture
def parameters_data_from_json(mpt_parameters_data):
    return AgreementParametersData.from_json(mpt_parameters_data)


@pytest.fixture
def parameters_data_from_dict():
    return AgreementParametersData(
        id="PAR-9939-6700-0001",
        coordinate="K234",
        name="Agreement type",
        external_id="agreementType",
        phase="Order",
        type="Choice",
        description="When you are creating a new agreement with SoftwareOne, you have the option "
        "to create a new Adobe VIP Marketplace account or migrate your existing Adobe "
        "VIP account to Adobe VIP Marketplace.",
        display_order=101,
        group_id="PGR-9939-6700-0001",
        options={
            "optionsList": [
                {
                    "label": "Create account",
                    "value": "New",
                    "description": """
                    Create a new Adobe VIP Marketplace account if you have never purchased Adobe
       products before, or if you wish to set up a new account in addition to an account you may
       already have. You will need to provide details such as your company address and contacts,
       and you will be required to accept both the Adobe Terms and Conditions as well as
       SoftwareOne\u0027s terms and conditions.""",
                },
                {
                    "label": "Migrate account",
                    "value": "Migrate",
                    "description": """Migrate from Adobe VIP if you are currently purchasing
                    products under the Adobe VIP licensing program. This comes with several
                    advantages including the ability to self-service manage your subscriptions
                    within the SoftwareOne Marketplace. You will need to provide details such as
                    your company address and contacts, and you will be required to accept  both the
                    Adobe Terms and Conditions as well as SoftwareOne\u0027s terms and
                    conditions.\n\n Note: If you are purchasing Adobe products under a different
                    licensing program such as CLP or TLP, you cannot use this option.""",
                },
            ],
            "defaultValue": None,
            "hintText": "Please select one option to continue",
            "label": "Agreement type",
        },
        constraints={"hidden": False, "readonly": False, "optional": True, "required": False},
        group_id_coordinate="I22",
    )


@pytest.fixture
def mpt_parameters_data():
    return {
        "id": "PAR-0232-2541-0001",
        "name": "Agreement type",
        "description": "When you are creating a new agreement with SoftwareOne, you have the option"
        " to create a new Adobe VIP Marketplace account or migrate your existing "
        "Adobe VIP account to Adobe VIP Marketplace.",
        "group": {"id": "PGR-0232-2541-0002", "name": "Create agreement"},
        "scope": "Agreement",
        "phase": "Order",
        "context": "None",
        "externalId": "agreementType",
        "displayOrder": 101,
        "constraints": {"hidden": False, "readonly": False, "required": True},
        "product": {
            "id": "PRD-0232-2541",
            "name": "[DO NOT USE] Adobe VIP Marketplace for Commercial",
            "externalIds": {"operations": ""},
            "icon": "/v1/catalog/products/PRD-0232-2541/icon",
            "status": "Unpublished",
        },
        "options": {
            "optionsList": [
                {
                    "label": "Create account",
                    "value": "New",
                    "description": "Create a new Adobe VIP Marketplace account if you have never "
                    "purchased Adobe products before, or if you wish to set up an "
                    "new account in addition to an account you may already have. "
                    "You will need to provide details such as your company address "
                    "and contacts, and you will be required to accept both the Adobe"
                    " Terms and Conditions as well as SoftwareOne's terms and "
                    "conditions.",
                },
                {
                    "label": "Migrate account",
                    "value": "Migrate",
                    "description": "Migrate from Adobe VIP if you are currently purchasing products"
                    " under the Adobe VIP licensing program. This comes with several"
                    " advantages including the ability to self-service manage your"
                    " subscriptions within the SoftwareOne Marketplace. You will"
                    " need to provide details such as your company address and"
                    " contacts, and you will be required to accept both the Adobe"
                    " Terms and Conditions as well as SoftwareOne's terms and"
                    " conditions.\n\nNote: If you are purchasing Adobe products"
                    " under a different licensing program such as CLP or TLP, you"
                    " cannot use this option.",
                },
            ],
            "defaultValue": "New",
            "hintText": "Some hint text",
        },
        "type": "Choice",
        "status": "Active",
        "audit": {
            "created": {
                "at": "2024-03-19T11:40:12.347Z",
                "by": {
                    "id": "USR-0000-0022",
                    "name": "User22",
                    "icon": "/v1/accounts/users/USR-0000-0022/icon",
                },
            },
            "updated": {
                "at": "2024-03-19T12:03:49.878Z",
                "by": {
                    "id": "USR-0000-0022",
                    "name": "User22",
                    "icon": "/v1/accounts/users/USR-0000-0022/icon",
                },
            },
        },
    }


@pytest.fixture
def parameter_group_file_data():
    return {
        PARAMETERS_GROUPS_ID: {"value": "IGR-3114-5854-0002", "coordinate": "A325"},
        PARAMETERS_GROUPS_NAME: {"value": "Details", "coordinate": "B325"},
        PARAMETERS_ACTION: {"value": "-", "coordinate": "C325"},
        PARAMETERS_GROUPS_LABEL: {"value": "Agreement details", "coordinate": "D325"},
        PARAMETERS_GROUPS_DISPLAY_ORDER: {"value": "232", "coordinate": "E325"},
        PARAMETERS_GROUPS_DESCRIPTION: {"value": "Fake Description", "coordinate": "F325"},
        PARAMETERS_GROUPS_DEFAULT: {"value": "False", "coordinate": "G325"},
        PARAMETERS_GROUPS_CREATED: {"value": datetime(2024, 5, 23, 0, 0), "coordinate": "H325"},
        PARAMETERS_GROUPS_MODIFIED: {"value": datetime(2024, 8, 14, 0, 0), "coordinate": "I325"},
    }


@pytest.fixture
def parameter_group_data_from_dict():
    return ParameterGroupData(
        id="PGR-9939-6700-0001",
        coordinate="A2",
        name="Agreement",
        label="Create agreement",
        description="When you are creating a new agreement with SoftwareOne, you have the option "
        "to create a new Adobe VIP Marketplace account or migrate your existing Adobe "
        "VIP account to Adobe VIP Marketplace.",
        display_order=10,
        default=True,
        created_date=datetime(2024, 5, 6, 0, 0),
        updated_date=datetime(2024, 5, 18, 0, 0),
    )


@pytest.fixture
def mpt_parameter_group_data():
    return {
        "id": "PGR-0232-2541-0002",
        "name": "Create agreement",
        "label": "Create agreement",
        "description": "When you are creating a new agreement with SoftwareOne, you have the option"
        " to establish a new Microsoft account or connect it to an existing account "
        "you already hold with Adobe.",
        "displayOrder": 101,
        "default": True,
        "parameterCount": 3,
        "product": {
            "id": "PRD-0232-2541",
            "name": "[DO NOT USE] Adobe VIP Marketplace for Commercial",
            "externalIds": {"operations": ""},
            "icon": "/v1/catalog/products/PRD-0232-2541/icon",
            "status": "Unpublished",
        },
        "audit": {
            "created": {
                "at": "2024-03-19T11:25:18.976Z",
                "by": {
                    "id": "USR-0000-0022",
                    "name": "User22",
                    "icon": "/v1/accounts/users/USR-0000-0022/icon",
                },
            },
            "updated": {
                "at": "2025-06-10T16:16:51.892Z",
                "by": {"id": "USR-0000-0044", "name": "User44"},
            },
        },
    }


@pytest.fixture
def template_file_data():
    return {
        TEMPLATES_ID: {"value": "TPL-0400-9557-0005", "coordinate": "A3"},
        TEMPLATES_NAME: {"value": "BulkMigrate", "coordinate": "B3"},
        TEMPLATES_ACTION: {"value": "-", "coordinate": "C3"},
        TEMPLATES_TYPE: {"value": "OrderCompleted", "coordinate": "D3"},
        TEMPLATES_DEFAULT: {"value": "False", "coordinate": "E3"},
        TEMPLATES_CONTENT: {
            "value": "Querying template for Adobe VIP Marketplace",
            "coordinate": "F3",
        },
        TEMPLATES_CREATED: {"value": datetime(2025, 5, 23, 0, 0), "coordinate": "G3"},
        TEMPLATES_MODIFIED: {"value": None, "coordinate": "H3"},
    }


@pytest.fixture
def template_data_from_json(mpt_template_data):
    return TemplateData.from_json(mpt_template_data)


@pytest.fixture
def template_data_from_dict():
    return TemplateData(
        id="TPL-0400-9557-0005",
        coordinate="A2",
        name="Change",
        type="OrderCompleted",
        content=r"""## Your order is complete

Your order has completed and your subscriptions are ready for use.

You can continue to use the Adobe Admin Console to assign licenses to users in your organization.
<br />Your existing username and password for the Adobe Admin Console remain unchanged.

[Adobe Admin Console](https://adminconsole.adobe.com/)

You can view and manage your agreements and subscriptions within the SoftwareOne Marketplace.

***

## Completed steps

We have completed the following steps:

1\. We changed the quantities of any subscriptions you modified in the order.

2\. We created any new subscriptions based on items added to your order.

***

## Need help?

If you have any questions regarding your order, please contact your SoftwareOne account team.

Thanks for choosing SoftwareOne.
""",
        content_coordinate="F2",
        default=False,
    )


@pytest.fixture
def mpt_template_data():
    return {
        "id": "TPL-0232-2541-0005",
        "name": "Default Processing Template",
        "content": "#Thanks you for your order  Sit back and enjoy {{ PAR-0232-2541-0002 }} while "
        "we are working on your order.",
        "type": "OrderProcessing",
        "default": False,
        "audit": {
            "created": {
                "at": "2024-04-08T14:56:47.271Z",
                "by": {"id": "USR-6248-5083", "name": "User5083"},
            },
            "updated": {
                "at": "2024-05-03T11:20:41.007Z",
                "by": {"id": "USR-0081-7601", "name": "User7601"},
            },
        },
    }


@pytest.fixture
def settings_file_data():
    return {
        "Change order validation (draft)": {"value": "Enabled", "coordinate": "C2"},
        "Item selection validation": {"value": "Off", "coordinate": "C3"},
        "Order queue changes notification": {"value": "Off", "coordinate": "C4"},
        "Product ordering": {"value": "Enabled", "coordinate": "C5"},
        "Product requests": {"value": "Off", "coordinate": "C6"},
        "Product requests. Request title": {"value": "Off", "coordinate": "C7"},
        "Product requests. Call to action label": {"value": None, "coordinate": "C8"},
        "Product request validation (draft)": {"value": None, "coordinate": "C9"},
        "Purchase order validation (draft)": {"value": "Enabled", "coordinate": "C10"},
        "Purchase order validation (query)": {"value": "Off", "coordinate": "C11"},
        "Termination order validation (draft)": {"value": "Off", "coordinate": "C12"},
    }
