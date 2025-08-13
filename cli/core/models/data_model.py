from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Self, TypeVar

DataModel = TypeVar("DataModel", bound="BaseDataModel")


@dataclass
class BaseDataModel(ABC):
    """Abstract base data model with serialization and deserialization methods."""

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create an instance from a dictionary.

        Args:
            data: A dictionary containing the data.

        Returns:
            An instance of the class.

        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        """Create an instance from a JSON-like dictionary.

        Args:
            data: A dictionary representing JSON data.

        Returns:
            An instance of the class.

        """
        raise NotImplementedError

    @abstractmethod
    def to_json(self) -> dict[str, Any]:
        """Convert the instance to a JSON-serializable dictionary.

        Returns:
            A dictionary representing the instance in JSON format.

        """
        raise NotImplementedError

    @abstractmethod
    def to_xlsx(self) -> dict[str, Any]:
        """Convert the instance to a dictionary suitable for XLSX export.

        Returns:
            A dictionary representing the instance for XLSX export.

        """
        raise NotImplementedError


@dataclass
class DataCollectionModel[DataModel]:
    """Generic collection model for managing groups of data models."""

    collection: dict[str, DataModel]

    def add(self, collection: dict[str, DataModel]) -> None:
        """Add items from another collection to this collection.

        Args:
            collection: A collection of items to add.

        """
        self.collection.update(collection)

    def retrieve_by_id(self, item_id: str) -> DataModel:
        """Retrieve an item from the collection by its ID.

        Args:
            item_id: The ID of the item to retrieve.

        Returns:
            The item corresponding to the given ID.

        """
        return self.collection[item_id]
