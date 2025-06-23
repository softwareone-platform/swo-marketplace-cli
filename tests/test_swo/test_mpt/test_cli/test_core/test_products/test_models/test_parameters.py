import pytest
from swo.mpt.cli.core.products.models.parameters import ParamScopeEnum


@pytest.mark.parametrize(
    ("is_order_request", "expected_result"), [(True, {"id": "PGR-9939-6700-0001"}), (False, None)]
)
def test_group_property(is_order_request, expected_result, mocker, parameters_data_from_dict):
    mocker.patch.object(
        parameters_data_from_dict, "is_order_request", return_value=is_order_request
    )

    assert parameters_data_from_dict.group == expected_result


def test_is_order_request(mocker, parameters_data_from_dict):
    mocker.patch.object(parameters_data_from_dict, "phase", "Order")
    mocker.patch.object(parameters_data_from_dict, "scope", ParamScopeEnum.AGREEMENT)

    assert parameters_data_from_dict.is_order_request() is True


def test_is_order_request_scope_false(mocker, parameters_data_from_dict):
    mocker.patch.object(parameters_data_from_dict, "phase", "Order")
    mocker.patch.object(parameters_data_from_dict, "scope", ParamScopeEnum.ITEM)

    assert parameters_data_from_dict.is_order_request() is False


def test_is_order_request_phase_false(mocker, parameters_data_from_dict):
    mocker.patch.object(parameters_data_from_dict, "phase", "Fullfillment")
    mocker.patch.object(parameters_data_from_dict, "scope", ParamScopeEnum.ITEM)

    assert parameters_data_from_dict.is_order_request() is False
