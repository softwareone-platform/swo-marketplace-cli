from swo.mpt.cli.plugins.audit_plugin.utils import (
    display_audit_records,
    flatten_dict,
    format_json_path,
)


class TestFlattenDict:
    def test_simple_dict(self):
        input_dict = {"a": 1, "b": 2}
        result = flatten_dict(input_dict)
        assert result == {"a": 1, "b": 2}

    def test_nested_dict(self):
        input_dict = {
            "a": {
                "b": 1,
                "c": {
                    "d": 2
                }
            }
        }
        result = flatten_dict(input_dict)
        assert result == {
            "a.b": 1,
            "a.c.d": 2
        }

    def test_dict_with_list(self):
        input_dict = {
            "a": [
                {"b": 1},
                {"c": 2}
            ]
        }
        result = flatten_dict(input_dict)
        assert result == {
            "a[0].b": 1,
            "a[1].c": 2
        }

    def test_dict_with_primitive_list(self):
        input_dict = {
            "a": [1, 2, 3]
        }
        result = flatten_dict(input_dict)
        assert result == {
            "a[0]": 1,
            "a[1]": 2,
            "a[2]": 3
        }


class TestFormatJsonPath:
    def test_simple_path(self):
        path = "object.name"
        source = {"object": {"name": "test"}}
        target = {"object": {"name": "test2"}}
        result = format_json_path(path, source, target)
        assert result == path

    def test_array_path_with_external_id(self):
        path = "items[0].value"
        source = {
            "items": [
                {"value": "old", "externalId": "EXT123"}
            ]
        }
        target = {
            "items": [
                {"value": "new", "externalId": "EXT123"}
            ]
        }
        result = format_json_path(path, source, target)
        assert result == "items[0].value (externalId: EXT123)"

    def test_invalid_path(self):
        path = "invalid.path[0]"
        source = {"different": "structure"}
        target = {"another": "structure"}
        result = format_json_path(path, source, target)
        assert result == path


class TestDisplayAuditRecords:
    def test_display_records(self, capsys):
        records = [
            {
                "id": "audit1",
                "timestamp": "2024-01-01T10:00:00Z",
                "actor": {
                    "name": "Test User",
                    "account": {"name": "Test Account"}
                },
                "event": "platform.commerce.create",
                "details": "Created object"
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

    def test_display_records_missing_fields(self, capsys):
        records = [
            {
                "id": "audit1",
                "timestamp": "2024-01-01T10:00:00Z"
            }
        ]
        display_audit_records(records)
        captured = capsys.readouterr()
        output = captured.out

        # Check individual elements instead of exact string matches
        assert "audit1" in output
        assert "2024-01-01T10:00:00Z" in output
        assert "N/A" in output  # For missing fields
