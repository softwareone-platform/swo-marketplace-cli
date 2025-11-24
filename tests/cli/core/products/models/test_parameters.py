import datetime as dt

import pytest
from cli.core.products.constants import (
    PARAMETERS_ACTION,
    PARAMETERS_CONSTRAINTS,
    PARAMETERS_CREATED,
    PARAMETERS_DESCRIPTION,
    PARAMETERS_DISPLAY_ORDER,
    PARAMETERS_EXTERNALID,
    PARAMETERS_GROUP_ID,
    PARAMETERS_GROUP_NAME,
    PARAMETERS_ID,
    PARAMETERS_MODIFIED,
    PARAMETERS_NAME,
    PARAMETERS_OPTIONS,
    PARAMETERS_PHASE,
    PARAMETERS_TYPE,
)
from cli.core.products.models import AgreementParametersData, DataActionEnum
from cli.core.products.models.parameters import ParamScopeEnum


def test_parameters_data_from_dict(parameters_file_data):
    result = AgreementParametersData.from_dict(parameters_file_data)

    assert result.id == "PAR-5159-0756-0001"
    assert result.coordinate == "A325"
    assert (
        result.description
        == "When you are creating a new agreement with SoftwareOne, you have the option to create "
        "a new Adobe VIP Marketplace account or migrate your existing Adobe VIP account to "
        "Adobe VIP Marketplace."
    )
    assert result.display_order == 101
    assert result.external_id == "agreementType"
    assert result.name == "Agreement type"
    assert result.phase == "Order"
    assert result.type == "Choice"
    assert result.constraints == {
        "hidden": False,
        "readonly": False,
        "optional": False,
        "required": True,
    }
    assert result.options == {"defaultValue": "Buyer", "hintText": "Address.", "label": "Address"}
    assert result.group_id == "PGR-5159-0756-0002"
    assert result.group_id_coordinate == "I325"


def test_parameters_data_from_json(mpt_agreement_parameter_data):
    result = AgreementParametersData.from_json(mpt_agreement_parameter_data)

    assert result.id == "PAR-0232-2541-0001"
    assert (
        result.description
        == "When you are creating a new agreement with SoftwareOne, you have the option to create "
        "a new Adobe VIP Marketplace account or migrate your existing Adobe VIP account to "
        "Adobe VIP Marketplace."
    )
    assert result.display_order == 101
    assert result.external_id == "agreementType"
    assert result.name == "Agreement type"
    assert result.phase == "Order"
    assert result.type == "Choice"
    assert result.constraints == {
        "hidden": False,
        "readonly": False,
        "required": True,
    }
    assert result.options == {
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
                "description": "Migrate from Adobe VIP if you are currently purchasing products "
                "under the Adobe VIP licensing program. This comes with several "
                "advantages including the ability to self-service manage your "
                "subscriptions within the SoftwareOne Marketplace. You will need to "
                "provide details such as your company address and contacts, and you "
                "will be required to accept both the Adobe Terms and Conditions as "
                "well as SoftwareOne's terms and conditions.\n\nNote: If you are "
                "purchasing Adobe products under a different licensing program such "
                "as CLP or TLP, you cannot use this option.",
            },
        ],
        "defaultValue": "New",
        "hintText": "Some hint text",
    }
    assert result.group_id == "PGR-0232-2541-0002"
    assert result.group_id_coordinate is None
    assert result.created_date == dt.date(2024, 3, 19)
    assert result.updated_date == dt.date(2024, 3, 19)


def test_parameters_data_to_json(parameters_data_from_dict):
    result = parameters_data_from_dict.to_json()

    assert result == {
        "name": "Agreement type",
        "description": "When you are creating a new agreement with SoftwareOne, you have the option"
        " to create a new Adobe VIP Marketplace account or migrate your existing "
        "Adobe VIP account to Adobe VIP Marketplace.",
        "scope": str(ParamScopeEnum.AGREEMENT),
        "phase": "Order",
        "type": "Choice",
        "options": {
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
        },
        "constraints": {"hidden": False, "readonly": False, "optional": True, "required": False},
        "externalId": "agreementType",
        "displayOrder": 101,
        "group": {"id": "PGR-0232-2541-0001"},
    }
    assert result["options"].get("label") is None


def test_parameters_data_to_xlsx(parameters_data_from_json):
    result = parameters_data_from_json.to_xlsx()

    assert result == {
        PARAMETERS_ID: "PAR-0232-2541-0001",
        PARAMETERS_NAME: "Agreement type",
        PARAMETERS_EXTERNALID: "agreementType",
        PARAMETERS_ACTION: DataActionEnum.SKIP,
        PARAMETERS_PHASE: "Order",
        PARAMETERS_TYPE: "Choice",
        PARAMETERS_DESCRIPTION: "When you are creating a new agreement with SoftwareOne, you have "
        "the option to create a new Adobe VIP Marketplace account or "
        "migrate your existing Adobe VIP account to Adobe VIP Marketplace.",
        PARAMETERS_DISPLAY_ORDER: 101,
        PARAMETERS_GROUP_ID: "PGR-0232-2541-0002",
        PARAMETERS_GROUP_NAME: "Create agreement",
        PARAMETERS_OPTIONS: '{"optionsList": [{"label": "Create account", "value": "New", '
        '"description": "Create a new Adobe VIP Marketplace account if you '
        "have never purchased Adobe products before, or if you wish to set "
        "up an new account in addition to an account you may already have. "
        "You will need to provide details such as your company address and "
        "contacts, and you will be required to accept both the Adobe Terms "
        "and Conditions as well as SoftwareOne's terms and conditions.\"}, "
        '{"label": "Migrate account", "value": "Migrate", "description": '
        '"Migrate from Adobe VIP if you are currently purchasing products '
        "under the Adobe VIP licensing program. This comes with several "
        "advantages including the ability to self-service manage your "
        "subscriptions within the SoftwareOne Marketplace. You will need "
        "to provide details such as your company address and contacts, and "
        "you will be required to accept both the Adobe Terms and "
        "Conditions as well as SoftwareOne's terms and "
        "conditions.\\n\\nNote: If you are purchasing Adobe products under "
        "a different licensing program such as CLP or TLP, you cannot use "
        'this option."}], "defaultValue": "New", "hintText": "Some hint '
        'text"}',
        PARAMETERS_CONSTRAINTS: '{"hidden": false, "readonly": false, "required": true}',
        PARAMETERS_CREATED: dt.date(2024, 3, 19),
        PARAMETERS_MODIFIED: dt.date(2024, 3, 19),
    }


@pytest.mark.parametrize(
    ("is_order_request", "expected_result"), [(True, {"id": "PGR-0232-2541-0001"}), (False, None)]
)
def test_group_property(is_order_request, expected_result, mocker, parameters_data_from_dict):
    mocker.patch.object(
        parameters_data_from_dict, "is_order_request", return_value=is_order_request
    )

    result = parameters_data_from_dict.group

    assert result == expected_result


def test_is_order_request(mocker, parameters_data_from_dict):
    mocker.patch.object(parameters_data_from_dict, "phase", "Order")
    mocker.patch.object(parameters_data_from_dict, "scope", ParamScopeEnum.AGREEMENT)

    result = parameters_data_from_dict.is_order_request()

    assert result is True


def test_is_order_request_scope_false(mocker, parameters_data_from_dict):
    mocker.patch.object(parameters_data_from_dict, "phase", "Order")
    mocker.patch.object(parameters_data_from_dict, "scope", ParamScopeEnum.ITEM)

    result = parameters_data_from_dict.is_order_request()

    assert result is False


def test_is_order_request_phase_false(mocker, parameters_data_from_dict):
    mocker.patch.object(parameters_data_from_dict, "phase", "Fullfillment")
    mocker.patch.object(parameters_data_from_dict, "scope", ParamScopeEnum.ITEM)

    result = parameters_data_from_dict.is_order_request()

    assert result is False
