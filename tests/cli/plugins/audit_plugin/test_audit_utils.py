import pytest
from cli.plugins.audit_plugin.utils import (
    display_audit_records,
    flatten_dict,
    format_json_path,
    get_external_id,
    is_valid_path,
)


@pytest.mark.parametrize(
    ("input_dict", "expected_result"),
    [
        ({"a": 1, "b": 2}, {"a": 1, "b": 2}),  # simple dict
        ({"a": {"b": 1, "c": {"d": 2}}}, {"a.b": 1, "a.c.d": 2}),  # nested_dict
        ({"a": [{"b": 1}, {"c": 2}]}, {"a[0].b": 1, "a[1].c": 2}),  # dict with a list
        ({"a": [1, 2, 3]}, {"a[0]": 1, "a[1]": 2, "a[2]": 3}),  # dict with a primitive list
    ],
)
def test_flatten_dict(input_dict, expected_result):
    assert flatten_dict(input_dict) == expected_result


@pytest.mark.parametrize(
    ("path", "source", "target", "expected_result"),
    [
        ("simple.path", {"object": {"name": "test"}}, {"object": {"name": "test2"}}, "simple.path"),
        (
            "items[0].value",
            {"items": [{"value": "old", "externalId": "EXT123"}]},
            {"items": [{"value": "new", "externalId": "EXT123"}]},
            "items[0].value (externalId: EXT123)",
        ),  # array path with external id
        (
            "invalid.path[0]",
            {"different": "structure"},
            {"another": "structure"},
            "invalid.path[0]",
        ),  # invalid path
    ],
)
def test_format_json_path(path, source, target, expected_result):
    assert format_json_path(path, source, target) == expected_result


@pytest.mark.parametrize(
    ("obj", "index", "expected_result"),
    [
        ([{"externalId": "EXT123", "value": "old"}], 0, "EXT123"),
        ([{"key": "error"}], 0, None),
        ([{"index": "error"}], 2, None),
    ],
)
def test_get_external_id_path(obj, index, expected_result):
    result = get_external_id(obj, index)

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


def test_display_records(capsys):
    records = [
        {
            "id": "audit1",
            "timestamp": "2024-01-01T10:00:00Z",
            "actor": {"name": "Test User", "account": {"name": "Test Account"}},
            "event": "platform.commerce.create",
            "details": "Created object",
        }
    ]
    display_audit_records(records)
    captured = capsys.readouterr()
    output = captured.out

    # Check for key elements in the output
    assert "Available Audit Records" in output
    assert "2024-01-01T10:00:00Z" in output
    assert "audit1" in output
    assert "Test User" in output
    assert "(Test" in output
    assert "Account)" in output
    assert "create" in output
    assert "Created" in output
    assert "object" in output


def test_display_records_missing_fields(capsys):
    records = [{"id": "audit1", "timestamp": "2024-01-01T10:00:00Z"}]
    display_audit_records(records)
    captured = capsys.readouterr()
    output = captured.out

    # Check individual elements instead of exact string matches
    assert "audit1" in output
    assert "2024-01-01T10:00:00Z" in output
    assert "N/A" in output  # For missing fields
