from typing import Any


class StatsStateMixin:
    """Provide state accessors for stats collectors."""

    _stat_id: str | None
    _tab_aliases: dict[str, Any]
    _has_error: bool

    @property
    def stat_id(self) -> str | None:
        """Get the identifier of the stats collector."""
        return self._stat_id

    @stat_id.setter
    def stat_id(self, stat_value: str | None) -> None:
        self._stat_id = stat_value

    @property
    def tabs(self) -> dict[str, Any]:
        """Get the tab aliases with their results."""
        return self._tab_aliases

    @property
    def has_errors(self) -> bool:
        """Check if any errors have been recorded."""
        return self._has_error


class StatsMutationMixin:
    """Provide mutation helpers for stats collectors."""

    _tab_aliases: dict[str, Any]
    _has_error: bool

    def add_error(self, tab_name: str) -> None:
        """Increment error and total counters for a tab and mark errors as present.

        Args:
            tab_name: The name of the tab to update.

        """
        self._tab_aliases[tab_name]["error"] += 1
        self._tab_aliases[tab_name]["total"] += 1
        self._has_error = True

    def add_synced(self, tab_name: str) -> None:
        """Increment synced and total counters for a tab.

        Args:
            tab_name: The name of the tab to update.

        """
        self._tab_aliases[tab_name]["synced"] += 1
        self._tab_aliases[tab_name]["total"] += 1

    def add_skipped(self, tab_name: str) -> None:
        """Increment skipped and total counters for a tab.

        Args:
            tab_name: The name of the tab to update.

        """
        self._tab_aliases[tab_name]["skipped"] += 1
        self._tab_aliases[tab_name]["total"] += 1
