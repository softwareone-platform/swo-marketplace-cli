from abc import ABC, abstractmethod
from typing import TypedDict

from cli.core.stats_mixins import StatsMutationMixin, StatsStateMixin


class TabResults(TypedDict):
    """TypedDict representing the result statistics for synchronization operations.

    Attributes:
        synced: The number of successfully synchronized items.
        error: The number of items that encountered errors.
        total: The total number of processed items.
        skipped: The number of items that were skipped.

    """

    synced: int
    error: int
    total: int
    skipped: int


def default_results() -> TabResults:
    """Create a fresh statistics container."""
    return {
        "synced": 0,
        "error": 0,
        "total": 0,
        "skipped": 0,
    }


type SectionItems = dict[str, list[str]]


class ErrorMessagesCollector:
    """Error messages collector."""

    def __init__(self) -> None:
        self._sections: dict[str, SectionItems] = {}
        self._is_empty: bool = True

    def add_msg(self, section_name: str, item_name: str, msg: str) -> None:
        """Add an error message to a specific section and item.

        Args:
            section_name: The name of the section to add the message to.
            item_name: The name of the item within the section.
            msg: The error message to add.

        """
        self._is_empty = False

        if section_name not in self._sections:
            self._sections[section_name] = {}

        if item_name not in self._sections[section_name]:
            self._sections[section_name][item_name] = []

        self._sections[section_name][item_name].append(msg)

    def is_empty(self) -> bool:
        """Check if the collector has no error messages.

        Returns:
            True if no error messages have been added, False otherwise.

        """
        return self._is_empty

    def __str__(self) -> str:
        return "\n".join(self._iter_error_lines())

    def _iter_error_lines(self) -> list[str]:
        lines = []
        for section_name, section in self._sections.items():
            lines.append(self._format_section_line(section_name, section.get("", [])))
            for item_name, item_messages in section.items():
                if not item_name:
                    continue
                lines.append(self._format_item_line(item_name, item_messages))

        return lines

    def _format_section_line(self, section_name: str, messages: list[str]) -> str:
        if not messages:
            return f"{section_name}:"

        joined_messages = ", ".join(messages)
        return f"{section_name}: {joined_messages}"

    def _format_item_line(self, item_name: str, messages: list[str]) -> str:
        joined_messages = ", ".join(messages)
        return f"\t\t{item_name}: {joined_messages}"


class StatsCollector(StatsStateMixin, StatsMutationMixin, ABC):
    """Abstract base class for collecting and managing operation statistics."""

    def __init__(self, tabs: dict[str, TabResults]) -> None:
        self.errors = ErrorMessagesCollector()
        self._stat_id: str | None = None
        self._has_error = False
        self._tab_aliases = tabs

    def table_title(self) -> str:
        """Return the semantic title for console renderers."""
        return self._get_table_title()

    @abstractmethod
    def _get_table_title(self) -> str:
        raise NotImplementedError


class ProductStatsCollector(StatsCollector):
    """Statistics collector specifically for product synchronization operations."""

    def __init__(self) -> None:
        tabs = {
            "General": default_results(),
            "Parameters Groups": default_results(),
            "Items Groups": default_results(),
            "Agreements Parameters": default_results(),
            "Assets Parameters": default_results(),
            "Item Parameters": default_results(),
            "Request Parameters": default_results(),
            "Subscription Parameters": default_results(),
            "Items": default_results(),
            "Templates": default_results(),
        }

        super().__init__(tabs)

    def _get_table_title(self) -> str:
        status = "[red bold]FAILED" if self.has_errors else "[green bold]SUCCEED"
        return f"Product Sync {status}"


class PriceListStatsCollector(StatsCollector):
    """Statistics collector specifically for price list synchronization operations.

    This class tracks statistics for price list operations including
    general information and price items.
    """

    def __init__(self) -> None:
        general: TabResults = default_results()
        price_items: TabResults = default_results()

        tabs = {
            "General": general,
            "Price Items": price_items,
        }
        super().__init__(tabs)

    def _get_table_title(self) -> str:
        if self.has_errors:
            title = "Pricelist sync [red bold]FAILED"
        else:
            title = f"Pricelist {self.stat_id} sync [green bold]SUCCEED"

        return title
