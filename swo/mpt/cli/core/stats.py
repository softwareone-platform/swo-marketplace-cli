import copy
from abc import ABC, abstractmethod
from typing import TypedDict

from rich import box
from rich.table import Table


class Results(TypedDict):
    synced: int
    error: int
    total: int
    skipped: int


DEFAULT_RESULTS: Results = {
    "synced": 0,
    "error": 0,
    "total": 0,
    "skipped": 0,
}


class ErrorMessagesCollector:
    """
    Error messages collector
    """

    def __init__(self) -> None:
        self._sections: dict[str, dict[str, list[str]]] = {}
        self._is_empty: bool = True

    def add_msg(self, section_name: str, item_name: str, msg: str):
        self._is_empty = False

        if section_name not in self._sections:
            self._sections[section_name] = {}

        if item_name not in self._sections[section_name]:
            self._sections[section_name][item_name] = []

        self._sections[section_name][item_name].append(msg)

    def is_empty(self) -> bool:
        return self._is_empty

    def __str__(self) -> str:
        msg = ""

        for section_name, section in self._sections.items():
            msg = f"{msg}{section_name}:"
            if "" in section:
                msg = f"{msg} {', '.join(section[''])}\n"
            else:
                msg += "\n"

            for item_name, item_messages in section.items():
                if item_name == "":
                    continue

                msg = f"{msg}\t\t{item_name}: {', '.join(item_messages)}"

        return msg


class StatsCollector(ABC):
    __id: str | None = None

    def __init__(self, tabs: dict[str, Results]) -> None:
        self.__has_error = False
        self.__tab_aliases = tabs

    def add_error(self, tab_name: str) -> None:
        self.__tab_aliases[tab_name]["error"] += 1
        self.__tab_aliases[tab_name]["total"] += 1
        self.__has_error = True

    def add_synced(self, tab_name: str) -> None:
        self.__tab_aliases[tab_name]["synced"] += 1
        self.__tab_aliases[tab_name]["total"] += 1

    def add_skipped(self, tab_name: str) -> None:
        self.__tab_aliases[tab_name]["skipped"] += 1
        self.__tab_aliases[tab_name]["total"] += 1

    @property
    def tabs(self) -> dict[str, Results]:
        return self.__tab_aliases

    @property
    def is_error(self) -> bool:
        return self.__has_error

    @abstractmethod
    def _get_table_title(self) -> str:  # pragma: no cover
        raise NotImplementedError

    def to_table(self):
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


class ProductStatsCollector(StatsCollector):
    def __init__(self) -> None:
        general: Results = copy.deepcopy(DEFAULT_RESULTS)
        parameters_groups: Results = copy.deepcopy(DEFAULT_RESULTS)
        items_groups: Results = copy.deepcopy(DEFAULT_RESULTS)
        agreements_parameters: Results = copy.deepcopy(DEFAULT_RESULTS)
        item_parameters: Results = copy.deepcopy(DEFAULT_RESULTS)
        request_parameters: Results = copy.deepcopy(DEFAULT_RESULTS)
        subscription_parameters: Results = copy.deepcopy(DEFAULT_RESULTS)
        items: Results = copy.deepcopy(DEFAULT_RESULTS)
        templates: Results = copy.deepcopy(DEFAULT_RESULTS)

        tabs = {
            "General": general,
            "Parameters Groups": parameters_groups,
            "Items Groups": items_groups,
            "Agreements Parameters": agreements_parameters,
            "Item Parameters": item_parameters,
            "Request Parameters": request_parameters,
            "Subscription Parameters": subscription_parameters,
            "Items": items,
            "Templates": templates,
        }

        super().__init__(tabs)

    def _get_table_title(self) -> str:
        status = "[red bold]FAILED" if self.is_error else "[green bold]SUCCEED"
        return f"Product Sync {status}"


class PriceListStatsCollector(StatsCollector):
    def __init__(self) -> None:
        general: Results = copy.deepcopy(DEFAULT_RESULTS)
        price_items: Results = copy.deepcopy(DEFAULT_RESULTS)

        tabs = {
            "General": general,
            "Price Items": price_items,
        }

        super().__init__(tabs)

    @property
    def price_list_id(self) -> str | None:
        return self.__id

    @price_list_id.setter
    def price_list_id(self, value: str) -> None:
        self.__id = value

    def _get_table_title(self) -> str:
        if self.is_error:
            title = "Pricelist sync [red bold]FAILED"
        else:
            title = f"Pricelist {self.price_list_id} sync [green bold]SUCCEED"

        return title
