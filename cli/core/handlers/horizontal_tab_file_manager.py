from abc import abstractmethod
from collections.abc import Generator, Mapping
from typing import TYPE_CHECKING, Any, ClassVar, override

from cli.core.handlers.constants import ERROR_COLUMN_NAME
from cli.core.handlers.excel_styles import get_number_format_style, horizontal_tab_style
from cli.core.handlers.file_manager import ExcelFileManager
from openpyxl.styles import NamedStyle

if TYPE_CHECKING:
    from cli.core.models import BaseDataModel


class HorizontalTabFileManager[DataModel: "BaseDataModel"](ExcelFileManager):
    """File manager for handling horizontally-oriented Excel tabs.

    This class manages Excel sheets where data is organized horizontally,
    with field names in the first row and corresponding data in subsequent rows.
    """

    _data_model: type[DataModel]
    _fields: tuple[str, ...]
    _id_field: str
    _required_tabs: tuple[str, ...]
    _required_fields_by_tab: ClassVar[Mapping[str, Any]]
    _sheet_name: str

    def add(self, records: list[DataModel]) -> None:
        """Add a row for each item to the tab.

        Args:
            records: The items to add.
        """
        for row, record in enumerate(
            records, self.file_handler.get_sheet_next_row(self._sheet_name)
        ):
            item_xlsx = record.to_xlsx()
            for col, field in enumerate(self._fields, 1):
                cell_value = item_xlsx.get(field, "")
                style = self._get_style(record, cell_value)
                self.file_handler.write_cell(
                    self._sheet_name,
                    col=col,
                    row=row,
                    cell_value=cell_value,
                    data_validation=self._data_validation_map.get(field, None),
                    style=style,
                )

        self.file_handler.save()

    @override
    def create_tab(self) -> None:
        if not self.file_handler.exists():
            self.file_handler.create()

        for col, field in enumerate(self._fields, 1):
            self.file_handler.write_cell(
                self._sheet_name,
                row=1,
                col=col,
                cell_value=field,
                style=horizontal_tab_style,
            )

    def read_data(self) -> Generator[DataModel, None, None]:
        """Reads all item rows from the sheet and yields them as DataModel objects.

        Yields:
            DataModel: An object containing the data for each item row.
        """
        for row_data in self._read_data():
            yield self._data_model.from_dict(row_data)

    @override
    def write_error(self, error: str, resource_id: str | None = None) -> None:
        item_row = next(
            row
            for row in self.file_handler.get_data_from_horizontal_sheet(
                self._sheet_name, (self._id_field, ERROR_COLUMN_NAME)
            )
            if row[self._id_field]["value"] == resource_id
        )
        try:
            coordinate = item_row[ERROR_COLUMN_NAME]["coordinate"]
            column_letter, row_number = self._get_row_and_column_from_coordinate(coordinate)
        except (KeyError, ValueError):
            column_letter = self.file_handler.get_sheet_next_column(self._sheet_name)
            coordinate = next(iter(item_row.values()))["coordinate"]
            _, row_number = self._get_row_and_column_from_coordinate(coordinate)
            self.file_handler.write([{self._sheet_name: {f"{column_letter}1": ERROR_COLUMN_NAME}}])

        self.file_handler.write([{self._sheet_name: {f"{column_letter}{row_number}": error}}])

    def _get_style(self, record: DataModel, cell_value: Any) -> NamedStyle | None:
        if not isinstance(cell_value, float):
            return None

        try:
            currency = record.currency  # type: ignore[attr-defined]
            precision = record.precision  # type: ignore[attr-defined]
        except AttributeError:
            return None

        if currency is None or precision is None:
            return None

        return get_number_format_style(currency, precision)

    @abstractmethod
    def _read_data(self) -> Generator[dict[str, Any], None, None]:
        raise NotImplementedError
