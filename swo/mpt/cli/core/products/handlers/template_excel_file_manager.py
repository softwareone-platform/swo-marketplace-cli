from collections.abc import Generator
from typing import Any

from swo.mpt.cli.core.handlers.horizontal_tab_file_manager import HorizontalTabFileManager
from swo.mpt.cli.core.products.constants import (
    TAB_TEMPLATES,
    TEMPLATES_FIELDS,
    TEMPLATES_ID,
)
from swo.mpt.cli.core.products.models import TemplateData


class TemplateExcelFileManager(HorizontalTabFileManager):
    _data_model = TemplateData
    _fields = TEMPLATES_FIELDS
    _id_field = TEMPLATES_ID
    _sheet_name = TAB_TEMPLATES

    def _read_data(self) -> Generator[dict[str, Any], None, None]:
        return self.file_handler.get_data_from_horizontal_sheet(self._sheet_name, self._fields)
