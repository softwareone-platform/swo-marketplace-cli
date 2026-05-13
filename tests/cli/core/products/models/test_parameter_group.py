import datetime as dt

from cli.core.products.models import ParameterGroupData


def test_parameter_data_from_dict(parameter_group_file_data):
    result = ParameterGroupData.from_dict(parameter_group_file_data)

    expected_data = {
        "id": "IGR-3114-5854-0002",
        "coordinate": "A325",
        "default": False,
        "description": "Fake Description",
        "display_order": 232,
        "label": "Agreement details",
        "name": "Details",
    }
    assert {
        field_name: getattr(result, field_name) for field_name in expected_data
    } == expected_data


def test_parameter_data_from_json(mpt_parameter_group_data):
    result = ParameterGroupData.from_json(mpt_parameter_group_data)

    expected_data = {
        "id": "PGR-0232-2541-0002",
        "default": True,
        "description": (
            "When you are creating a new agreement with SoftwareOne, you have the option "
            "to establish a new Microsoft account or connect it to an existing account "
            "you already hold with Adobe."
        ),
        "display_order": 101,
        "label": "Create agreement",
        "name": "Create agreement",
        "created_date": dt.date(2024, 3, 19),
        "updated_date": dt.date(2025, 6, 10),
    }
    assert {
        field_name: getattr(result, field_name) for field_name in expected_data
    } == expected_data


def test_parameter_data_to_json(parameter_group_data_from_dict):
    result = parameter_group_data_from_dict.to_json()

    assert result == {
        "default": True,
        "description": (
            "When you are creating a new agreement with SoftwareOne, you have the option "
            "to create a new Adobe VIP Marketplace account or migrate your existing Adobe "
            "VIP account to Adobe VIP Marketplace."
        ),
        "displayOrder": 10,
        "label": "Create agreement",
        "name": "Agreement",
    }
