import pytest
from cli.plugins.audit_plugin.audit_paths import get_external_id, is_valid_path


@pytest.mark.parametrize(
    ("source_node", "index", "expected_result"),
    [
        ([{"externalId": "EXT123", "value": "old"}], 0, "EXT123"),
        ([{"key": "error"}], 0, None),
        ([{"index": "error"}], 2, None),
    ],
)
def test_get_external_id_path(source_node, index, expected_result):
    result = get_external_id(source_node, index)

    assert result == expected_result


@pytest.mark.parametrize(
    ("path", "expected_result"),
    [
        ("[ foo ]", True),
        ("[ foo ", False),
        (" foo ]", False),
        ("bla", False),
    ],
)
def test_is_valid_path(path, expected_result):
    result = is_valid_path(path)

    assert result == expected_result
