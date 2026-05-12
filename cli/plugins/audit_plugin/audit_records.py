from typing import Any

from cli.core.console import console
from cli.core.console.renderers.audit import AuditRecordsRenderer
from cli.plugins.audit_plugin.audit_paths import (
    AuditTrail,
    get_external_id,
    is_valid_path,
    parse_array_path,
    walk_trail,
)

audit_records_renderer = AuditRecordsRenderer()


def display_audit_records(records: list) -> None:
    """Display available audit records in a table format."""
    console.print(audit_records_renderer.render(records))


def flatten_dict(
    source_dict: dict[str, Any], parent_key: str = "", sep: str = "."
) -> dict[str, Any]:
    """Flatten a nested dictionary into a single level with dot notation keys."""
    flattened_items: list = []
    for key, node_value in source_dict.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(node_value, dict):
            flattened_items.extend(flatten_dict(node_value, new_key, sep=sep).items())
        elif isinstance(node_value, list):
            flattened_items.extend(_flatten_list_entries(node_value, new_key, sep))
        else:
            flattened_items.append((new_key, node_value))
    return dict(flattened_items)


def format_json_path(path: str, source_trail: AuditTrail, target_trail: AuditTrail) -> str:
    """Format JSON path with additional context from external IDs if available."""
    if not is_valid_path(path):
        return path

    parts, index = parse_array_path(path)
    for trail in (source_trail, target_trail):
        external_id = get_external_id(walk_trail(trail, parts), index)
        if external_id is not None:
            return f"{path} (externalId: {external_id})"

    return path


def _flatten_list_entries(list_value: list, prefix: str, sep: str) -> list:
    """Flatten the entries of a list, dispatching dict entries back to ``flatten_dict``."""
    flattened: list = []
    for index, list_entry in enumerate(list_value):
        item_key = f"{prefix}[{index}]"
        if isinstance(list_entry, dict):
            flattened.extend(flatten_dict(list_entry, item_key, sep=sep).items())
        else:
            flattened.append((item_key, list_entry))
    return flattened
