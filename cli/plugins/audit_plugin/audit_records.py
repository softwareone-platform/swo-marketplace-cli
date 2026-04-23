from typing import Any

from cli.core.console import console
from cli.core.console.renderers.audit import AuditRecordsRenderer

audit_records_renderer = AuditRecordsRenderer()


def flatten_dict(
    source_dict: dict[str, Any], parent_key: str = "", sep: str = "."
) -> dict[str, Any]:
    """Flatten a nested dictionary into a single level with dot notation keys."""
    flattened_items: list = []
    for key, node_value in source_dict.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(node_value, dict):
            flattened_items.extend(flatten_dict(node_value, new_key, sep=sep).items())
            continue

        if isinstance(node_value, list):
            flattened_items.extend(_flatten_list_items(new_key, node_value, sep))
            continue

        flattened_items.append((new_key, node_value))
    return dict(flattened_items)


def format_json_path(path: str, source_trail: dict[str, Any], target_trail: dict[str, Any]) -> str:
    """Format JSON path with additional context from external IDs if available."""
    if "[" not in path or "]" not in path:
        return path

    array_path, _rest = path.split("]", 1)
    base_path, index_str = array_path.split("[")
    index = int(index_str)

    for trail in (source_trail, target_trail):
        external_id = get_external_id(_walk_path(trail, base_path), index)
        if external_id is not None:
            return f"{path} (externalId: {external_id})"

    return path


def get_external_id(current_node: Any, index: int) -> str | None:
    """Get the external ID from an object.

    Args:
        current_node: the object to get the external ID from.
        index: the index of the object to get the external ID from.

    Returns: the external ID or None.

    """
    if isinstance(current_node, list) and len(current_node) > index:
        try:
            return current_node[index]["externalId"]
        except (IndexError, KeyError):
            return None

    return None


def display_audit_records(records: list[Any]) -> None:
    """Display available audit records in a table format."""
    console.print(audit_records_renderer.render(records))


def _flatten_list_items(new_key: str, node_value: list[Any], sep: str) -> list[tuple[str, Any]]:
    flattened_items: list[tuple[str, Any]] = []
    for index, list_entry in enumerate(node_value):
        if isinstance(list_entry, dict):
            flattened_items.extend(flatten_dict(list_entry, f"{new_key}[{index}]", sep=sep).items())
            continue

        flattened_items.append((f"{new_key}[{index}]", list_entry))

    return flattened_items


def _walk_path(trail: dict[str, Any], base_path: str) -> Any | None:
    current_node: Any | None = trail
    for part in base_path.split("."):
        if not isinstance(current_node, dict) or part not in current_node:
            return None
        current_node = current_node[part]
    return current_node
