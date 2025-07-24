from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Self, TypeVar

DataModel = TypeVar("DataModel", bound="BaseDataModel")
type CollectionModel[DataModel] = dict[str, DataModel]


@dataclass
class BaseDataModel(ABC):
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:  # pragma: no cover
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_json(cls, data: dict[str, Any]) -> Self:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def to_json(self) -> dict[str, Any]:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def to_xlsx(self) -> dict[str, Any]:  # pragma: no cover
        raise NotImplementedError


@dataclass
class DataCollectionModel(Generic[DataModel]):
    collection: CollectionModel

    def add(self, collection: CollectionModel) -> None:
        self.collection.update(collection)

    def retrieve_by_id(self, item_id: str) -> DataModel:
        return self.collection[item_id]
