import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class FileHandler(ABC):
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def exists(self):
        """
        Check if the file exists.

        Returns:
            True if the file path exists, False otherwise.
        """
        return os.path.exists(self.file_path)

    @abstractmethod
    def create(self):
        """
        Create an empty file with the name of the file_path
        """
        raise NotImplementedError

    @abstractmethod
    def read(self) -> list[dict[str, Any]]:
        """
        Reads and returns the content of the file.

        Returns:
            The content read from the file.
        """
        raise NotImplementedError

    @abstractmethod
    def write(self, data: list[dict[str, Any]]) -> None:
        """
        Writes data to the file.

        Args:
            data: The data to write to the file.
        """
        raise NotImplementedError
