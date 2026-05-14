import pytest
from cli.plugins.audit_plugin.audit_records import (
    display_audit_records,
    flatten_dict,
    format_json_path,
)


@pytest.mark.parametrize(
    ("input_dict", "expected_result"),
    [
        ({"a": 1, "b": 2}, {"a": 1, "b": 2}),  # simple dict
        ({"a": {"b": 1, "c": {"d": 2}}}, {"a.b": 1, "a.c.d": 2}),  # noqa: WPS221
        ({"a": [{"b": 1}, {"c": 2}]}, {"a[0].b": 1, "a[1].c": 2}),  # noqa: WPS221
        ({"a": [1, 2, 3]}, {"a[0]": 1, "a[1]": 2, "a[2]": 3}),  # dict with a primitive list
    ],
)
def test_flatten_dict(input_dict, expected_result):
    result = flatten_dict(input_dict)

    assert result == expected_result


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
    result = format_json_path(path, source, target)

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

    display_audit_records(records)  # act

    captured = capsys.readouterr()
    output = captured.out
    assert all(
        fragment in output
        for fragment in (
            "Available Audit Records",
            "2024-01-01T10:00:00Z",
            "audit1",
            "Test User",
            "(Test",
            "Account)",
            "create",
            "Created",
            "object",
        )
    )


def test_display_records_missing_fields(capsys):
    records = [{"id": "audit1", "timestamp": "2024-01-01T10:00:00Z"}]

    display_audit_records(records)  # act

    captured = capsys.readouterr()
    output = captured.out
    assert "audit1" in output
    assert "2024-01-01T10:00:00Z" in output
    assert "N/A" in output  # For missing fields
