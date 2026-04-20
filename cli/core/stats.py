from abc import ABC, abstractmethod
from typing import TypedDict

from cli.core.stats_mixins import StatsMutationMixin, StatsStateMixin
from rich import box
from rich.table import Table


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
        lines: list[str] = []
        for section_name, section in self._sections.items():
            section_messages = section.get("", [])
            if section_messages:
                lines.append(f"{section_name}: {', '.join(section_messages)}")
            else:
                lines.append(f"{section_name}:")

            for item_name, item_messages in section.items():
                if not item_name:
                    continue

                lines.append(f"\t\t{item_name}: {', '.join(item_messages)}")

        return "\n".join(lines)


class StatsCollector(StatsStateMixin, StatsMutationMixin, ABC):
    """Abstract base class for collecting and managing operation statistics."""

    def __init__(self, tabs: dict[str, TabResults]) -> None:
        self.errors = ErrorMessagesCollector()
        self._stat_id: str | None = None
        self._has_error = False
        self._tab_aliases = tabs

    def to_table(self) -> Table:
        """Generate a rich Table representation of the collected stats.

        Returns:
            A Table object displaying the statistics for each tab.

        """
        table = Table(self._get_table_title(), box=box.ROUNDED)
        columns = ["Total", "Synced", "Errors", "Skipped"]
        for column in columns:
            table.add_column(column)

        for tab_name, tab_stats in self.tabs.items():
            table.add_row(
                tab_name,
                f"[blue]{tab_stats['total']}",
                f"[green]{tab_stats['synced']}",
                f"[red bold]{tab_stats['error']}",
                f"[white]{tab_stats['skipped']}",
            )
        return table

    @abstractmethod
    def _get_table_title(self) -> str:
        raise NotImplementedError


class ProductStatsCollector(StatsCollector):
    """Statistics collector specifically for product synchronization operations."""

    def __init__(self) -> None:
        general: TabResults = default_results()
        parameters_groups: TabResults = default_results()
        items_groups: TabResults = default_results()
        agreements_parameters: TabResults = default_results()
        asset_parameters: TabResults = default_results()
        item_parameters: TabResults = default_results()
        request_parameters: TabResults = default_results()
        subscription_parameters: TabResults = default_results()
        item_rows: TabResults = default_results()
        templates: TabResults = default_results()

        tabs = {
            "General": general,
            "Parameters Groups": parameters_groups,
            "Items Groups": items_groups,
            "Agreements Parameters": agreements_parameters,
            "Assets Parameters": asset_parameters,
            "Item Parameters": item_parameters,
            "Request Parameters": request_parameters,
            "Subscription Parameters": subscription_parameters,
            "Items": item_rows,
            "Templates": templates,
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
