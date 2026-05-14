import pytest
from cli.core.products import constants as product_constants
from cli.core.products.models import AgreementParametersData, DataActionEnum
from cli.core.products.models.parameters import ParamScopeEnum


def test_parameters_data_from_dict(parameters_file_data):
    result = AgreementParametersData.from_dict(parameters_file_data)

    expected_data = {
        "id": "PAR-5159-0756-0001",
        "coordinate": "A325",
        "description": (
            "When you are creating a new agreement with SoftwareOne, you have the option "
            "to create a new Adobe VIP Marketplace account or migrate your existing Adobe "
            "VIP account to Adobe VIP Marketplace."
        ),
        "display_order": 100,
        "external_id": "agreementType",
        "name": "Agreement type",
        "phase": "Order",
        "type": "Choice",
        "constraints": {
            "hidden": False,
            "readonly": False,
            "optional": False,
            "required": True,
        },
        "options": {"defaultValue": "Buyer", "hintText": "Address.", "label": "Address"},
        "group_id": "PGR-5159-0756-0002",
        "group_id_coordinate": "I325",
    }
    assert {
        field_name: getattr(result, field_name) for field_name in expected_data
    } == expected_data


def test_parameters_data_from_json(date_factory, mpt_agreement_parameter_data):
    result = AgreementParametersData.from_json(mpt_agreement_parameter_data)

    expected_data = {
        "id": "PAR-0232-2541-0001",
        "description": (
            "When you are creating a new agreement with SoftwareOne, you have the option "
            "to create a new Adobe VIP Marketplace account or migrate your existing Adobe "
            "VIP account to Adobe VIP Marketplace."
        ),
        "display_order": 101,
        "external_id": "agreementType",
        "name": "Agreement type",
        "phase": "Order",
        "type": "Choice",
        "constraints": {
            "hidden": False,
            "readonly": False,
            "required": True,
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
                    "description": "Migrate from Adobe VIP if you are currently purchasing "
                    "products "
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
        },
        "group_id": "PGR-0232-2541-0002",
        "group_id_coordinate": None,
        "created_date": date_factory("2024-03-19"),
        "updated_date": date_factory("2024-03-19"),
    }
    assert {
        field_name: getattr(result, field_name) for field_name in expected_data
    } == expected_data


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
                    "description": (
                        "Create a new Adobe VIP Marketplace account if you have never purchased "
                        "Adobe products before, or if you wish to set up a new account in "
                        "addition to an account you may already have. You will need to provide "
                        "details such as your company address and contacts, and you will be "
                        "required to accept both the Adobe Terms and Conditions as well as "
                        "SoftwareOne's terms and conditions."
                    ),
                },
                {
                    "label": "Migrate account",
                    "value": "Migrate",
                    "description": (
                        "Migrate from Adobe VIP if you are currently purchasing products under the "
                        "Adobe VIP licensing program. This comes with several advantages including "
                        "the ability to self-service manage your subscriptions within the "
                        "SoftwareOne Marketplace. You will need to provide details such as your "
                        "company address and contacts, and you will be required to accept both the "
                        "Adobe Terms and Conditions as well as SoftwareOne's terms and "
                        "conditions.\n\n Note: If you are purchasing Adobe products under a "
                        "different licensing program such as CLP or TLP, you cannot use this "
                        "option."
                    ),
                },
            ],
            "defaultValue": None,
            "hintText": "Please select one option to continue",
        },
        "constraints": {"hidden": False, "readonly": False, "optional": True, "required": False},
        "externalId": "agreementType",
        "displayOrder": 100,
        "group": {"id": "PGR-0232-2541-0001"},
    }
    assert result["options"].get("label") is None


def test_parameters_data_to_xlsx(date_factory, parameters_data_from_json):
    result = parameters_data_from_json.to_xlsx()

    assert result == {
        product_constants.PARAMETERS_ID: "PAR-0232-2541-0001",
        product_constants.PARAMETERS_NAME: "Agreement type",
        product_constants.PARAMETERS_EXTERNALID: "agreementType",
        product_constants.PARAMETERS_ACTION: DataActionEnum.SKIP,
        product_constants.PARAMETERS_PHASE: "Order",
        product_constants.PARAMETERS_TYPE: "Choice",
        product_constants.PARAMETERS_DESCRIPTION: (
            "When you are creating a new agreement with SoftwareOne, you have "
            "the option to create a new Adobe VIP Marketplace account or "
            "migrate your existing Adobe VIP account to Adobe VIP Marketplace."
        ),
        product_constants.PARAMETERS_DISPLAY_ORDER: 101,
        product_constants.PARAMETERS_GROUP_ID: "PGR-0232-2541-0002",
        product_constants.PARAMETERS_GROUP_NAME: "Create agreement",
        product_constants.PARAMETERS_OPTIONS: (
            '{"optionsList": [{"label": "Create account", "value": "New", '
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
            r"conditions.\n\nNote: If you are purchasing Adobe products under "
            "a different licensing program such as CLP or TLP, you cannot use "
            'this option."}], "defaultValue": "New", "hintText": "Some hint '
            'text"}'
        ),
        product_constants.PARAMETERS_CONSTRAINTS: (
            '{"hidden": false, "readonly": false, "required": true}'
        ),
        product_constants.PARAMETERS_CREATED: date_factory("2024-03-19"),
        product_constants.PARAMETERS_MODIFIED: date_factory("2024-03-19"),
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


@pytest.mark.parametrize(
    ("phase", "scope", "expected_result"),
    [
        ("Order", ParamScopeEnum.AGREEMENT, True),
        ("Order", ParamScopeEnum.REQUEST, False),
        ("Order", ParamScopeEnum.ITEM_SCOPE, False),
        ("Fulfillment", ParamScopeEnum.ITEM_SCOPE, False),
    ],
)
def test_is_order_request(phase, scope, expected_result, parameters_data_from_dict):
    parameters_data_from_dict.phase = phase
    parameters_data_from_dict.scope = scope

    result = parameters_data_from_dict.is_order_request()

    assert result is expected_result
