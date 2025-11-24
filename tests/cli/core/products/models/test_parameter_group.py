import datetime as dt

from cli.core.products.models import ParameterGroupData


def test_parameter_data_from_dict(parameter_group_file_data):
    result = ParameterGroupData.from_dict(parameter_group_file_data)

    assert result.id == "IGR-3114-5854-0002"
    assert result.coordinate == "A325"
    assert result.default is False
    assert result.description == "Fake Description"
    assert result.display_order == 232
    assert result.label == "Agreement details"
    assert result.name == "Details"


def test_parameter_data_from_json(mpt_parameter_group_data):
    result = ParameterGroupData.from_json(mpt_parameter_group_data)

    assert result.id == "PGR-0232-2541-0002"
    assert result.default is True
    assert result.description == (
        "When you are creating a new agreement with SoftwareOne, you have the option to establish "
        "a new Microsoft account or connect it to an existing account you already hold with Adobe."
    )
    assert result.display_order == 101
    assert result.label == "Create agreement"
    assert result.name == "Create agreement"
    assert result.created_date == dt.date(2024, 3, 19)
    assert result.updated_date == dt.date(2025, 6, 10)


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
