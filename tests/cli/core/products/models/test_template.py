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
    assert result.template_content == "Querying template for Adobe VIP Marketplace"
    assert result.content_coordinate == "F3"
    assert result.default is False


def test_template_data_from_json(mpt_template_data):
    result = TemplateData.from_json(mpt_template_data)

    assert result.id == "TPL-0232-2541-0005"
    assert result.name == "Default Processing Template"
    assert result.type == "OrderProcessing"
    assert result.template_content == (
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
        "content": (
            "## Your order is complete\n\n"
            "Your order has completed and your subscriptions are ready for use.\n\n"
            "You can continue to use the Adobe Admin Console to assign licenses to users in your "
            "organization.\n"
            "<br />Your existing username and password for the Adobe Admin Console remain "
            "unchanged.\n\n"
            "[Adobe Admin Console](https://adminconsole.adobe.com/)\n\n"
            "You can view and manage your agreements and subscriptions within the SoftwareOne "
            "Marketplace.\n\n"
            "***\n\n"
            "## Completed steps\n\n"
            "We have completed the following steps:\n\n"
            "1\\. We changed the quantities of any subscriptions you modified in the order.\n\n"
            "2\\. We created any new subscriptions based on items added to your order.\n\n"
            "***\n\n"
            "## Need help?\n\n"
            "If you have any questions regarding your order, please contact your SoftwareOne "
            "account team.\n\n"
            "Thanks for choosing SoftwareOne.\n"
        ),
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
