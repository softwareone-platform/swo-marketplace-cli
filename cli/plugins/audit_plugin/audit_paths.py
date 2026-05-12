from typing import Any

type AuditTrail = dict[str, Any]


def get_external_id(current_node: Any, index: int) -> str | None:
    """Get the external ID from an object.

    Args:
        current_node: the object to get the external ID from.
        index: the index of the object to get the external ID from.

    Returns:
        The external ID or ``None``.

    """
    if isinstance(current_node, list) and len(current_node) > index:
        try:
            return current_node[index]["externalId"]
        except (IndexError, KeyError):
            return None

    return None


def is_valid_path(path: str) -> bool:
    """Check if a path is valid.

    Args:
        path: The path to check.

    Returns:
        ``True`` if the path is valid, ``False`` otherwise.

    """
    return "[" in path and "]" in path


def parse_array_path(path: str) -> tuple[list[str], int]:
    """Parse ``a.b.c[N]rest`` into ``(["a", "b", "c"], N)``."""
    array_path = path.split("]", 1)[0]
    base_path, index_str = array_path.split("[")
    return base_path.split("."), int(index_str)


def walk_trail(trail: AuditTrail, parts: list[str]) -> Any:
    """Walk ``trail`` along ``parts``; return the last node or ``None`` if the path is invalid."""
    current_node: Any | None = trail
    for part in parts:
        if not isinstance(current_node, dict) or part not in current_node:
            return None
        current_node = current_node[part]
    return current_node
