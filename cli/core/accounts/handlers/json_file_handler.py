import json
from pathlib import Path
from typing import Any

from cli.core.handlers import FileHandler


class JsonFileHandler(FileHandler):
    """File handler for JSON file operations."""

    # TBD: should this be configurable by the user or moved to a constant?
    _default_file_path: Path = Path.home() / ".swocli" / "accounts.json"

    def __init__(self, file_path: Path | None = None):
        if file_path is None:
            file_path = self._default_file_path

        super().__init__(file_path)

    def create(self):
        """Creates a new empty JSON file at the specified file path."""
        self.write([])

    def read(self) -> list[dict[str, Any]]:
        """Reads and returns the data stored in the file.

        If the file does not exist, an empty file will be created first.

        Returns:
            The data stored in the file.
        """
        if not self.exists():
            self.create()

        with Path(self.file_path).open(encoding="utf-8") as f:
            return json.load(f)

    def write(self, data: list[dict[str, Any]]) -> None:
        """Writes data to a file in JSON format.

        Ensures the file path exists before writing, creating it if necessary.

        Args:
            data: the data to be written to the file.
        """
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)
        with Path(self.file_path).open("w+", encoding="utf-8") as f:
            json_data = json.dumps(data, indent=2)
            f.write(json_data)
