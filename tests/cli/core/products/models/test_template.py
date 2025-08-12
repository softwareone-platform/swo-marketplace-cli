import datetime as dt

from cli.core.products.constants import (
    TEMPLATES_ACTION,
    TEMPLATES_CONTENT,
    TEMPLATES_CREATED,
    TEMPLATES_DEFAULT,
    TEMPLATES_ID,
    TEMPLATES_MODIFIED,
    TEMPLATES_NAME,
    TEMPLATES_TYPE,
)
from cli.core.products.models import DataActionEnum, TemplateData


def test_template_data_from_dict(template_file_data):
    result = TemplateData.from_dict(template_file_data)

    assert result.id == "TPL-0232-2541-0005"
    assert result.coordinate == "A3"
    assert result.action == "-"
    assert result.name == "BulkMigrate"
    assert result.type == "OrderCompleted"
    assert result.content == "Querying template for Adobe VIP Marketplace"
    assert result.content_coordinate == "F3"
    assert result.default is False


def test_template_data_from_json(mpt_template_data):
    result = TemplateData.from_json(mpt_template_data)

    assert result.id == "TPL-0232-2541-0005"
    assert result.name == "Default Processing Template"
    assert result.type == "OrderProcessing"
    assert result.content == (
        "#Thanks you for your order  Sit back and enjoy {{ PAR-0232-2541-0002 }} while "
        "we are working on your order."
    )
    assert result.default is False
    assert result.created_date == dt.date(2024, 4, 8)
    assert result.updated_date == dt.date(2024, 5, 3)


def test_template_data_to_json(template_data_from_dict):
    result = template_data_from_dict.to_json()

    assert result == {
        "name": "Change",
        "type": "OrderCompleted",
        "content": r"""## Your order is complete

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
        "default": False,
    }


def test_template_to_xlsx(template_data_from_json):
    result = template_data_from_json.to_xlsx()

    assert result == {
        TEMPLATES_ID: "TPL-0232-2541-0005",
        TEMPLATES_NAME: "Default Processing Template",
        TEMPLATES_ACTION: DataActionEnum.SKIP,
        TEMPLATES_TYPE: "OrderProcessing",
        TEMPLATES_DEFAULT: "False",
        TEMPLATES_CONTENT: (
            "#Thanks you for your order  Sit back and enjoy {{ PAR-0232-2541-0002 }} while we "
            "are working on your order."
        ),
        TEMPLATES_CREATED: dt.date(2024, 4, 8),
        TEMPLATES_MODIFIED: dt.date(2024, 5, 3),
    }
