import re
from collections.abc import Generator
from typing import Any

type SheetData = dict[str, Any]
type SheetDataGenerator = Generator[SheetData, None, None]
type ColumnPatterns = list[re.Pattern[str]]
