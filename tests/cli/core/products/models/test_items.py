import pytest
from cli.core.products.models import ItemActionEnum, ItemData
from cli.core.products.models.enums import ItemTermsModelEnum


@pytest.mark.parametrize(
    ("terms_model", "expected_result"),
    [
        (
            ItemTermsModelEnum.ONE_TIME,
            {
                "model": ItemTermsModelEnum.ONE_TIME.value,
                "period": ItemTermsModelEnum.ONE_TIME.value,
            },
        ),
        (
            ItemTermsModelEnum.QUANTITY,
            {"model": ItemTermsModelEnum.QUANTITY.value, "commitment": "1y", "period": "1m"},
        ),
        (
            ItemTermsModelEnum.USAGE,
            {"model": ItemTermsModelEnum.USAGE.value, "commitment": "1y", "period": "1m"},
        ),
    ],
)
def test_item_data_terms_property(mocker, item_data_from_dict, terms_model, expected_result):
    mocker.patch.object(item_data_from_dict, "terms_model", terms_model)

    result = item_data_from_dict.terms

    assert result == expected_result


def test_item_data_from_dict(item_file_data):
    result = ItemData.from_dict(item_file_data)

    assert result.id == "PRI-3969-9403-0001-0035"
    assert result.terms_commitment == "1y"
    assert result.description == "Description"
    assert result.group_id == "IGR-4944-4118-0002"
    assert result.name == "XD for Teams; existing XD customers only.;"
    assert result.terms_period == "1m"
    assert result.terms_model == ItemTermsModelEnum.USAGE
    assert result.quantity_not_applicable is True
    assert result.unit_id == "UNT-1916"
    assert result.vendor_id == "30006419CB"
    assert result.coordinate == "A325"


def test_item_data_from_json(mpt_item_data):
    result = ItemData.from_json(mpt_item_data)

    assert result.id == "ITM-0232-2541-0001"
    assert result.name == "Creative Cloud All Apps with Adobe Stock (10 assets per month)"
    assert result.terms_model == ItemTermsModelEnum.ONE_TIME
    assert result.terms_period == "one-time"
    assert result.terms_commitment is None


def test_item_data_to_json(item_data_from_dict):
    result = item_data_from_dict.to_json()

    assert result == {
        "name": "XD for Teams; existing XD customers only.;",
        "description": "Description",
        "externalIds": {"vendor": "NAV12345"},
        "group": {"id": "IGR-4944-4118-0002"},
        "product": {"id": "PRD-0232-2541"},
        "quantityNotApplicable": True,
        "terms": {"model": "usage", "period": "1m", "commitment": "1y"},
        "unit": {"id": "UNT-1916"},
        "parameters": [],
    }


@pytest.mark.parametrize(
    ("action", "attr"),
    [
        (ItemActionEnum.CREATE, "to_create"),
        (ItemActionEnum.PUBLISH, "to_publish"),
        (ItemActionEnum.REVIEW, "to_review"),
        (ItemActionEnum.SKIP, "to_skip"),
        (ItemActionEnum.SKIPPED, "to_skip"),
        (ItemActionEnum.UNPUBLISH, "to_unpublish"),
        (ItemActionEnum.UPDATE, "to_update"),
    ],
)
def test_item_to_create(action, attr, item_data_from_dict):
    item_data_from_dict.action = action

    result = getattr(item_data_from_dict, attr)

    assert result is True
