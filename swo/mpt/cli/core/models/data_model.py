from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, TypeVar

DataModel = TypeVar("DataModel", bound="BaseDataModel")


@dataclass
class BaseDataModel(ABC):
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseDataModel":
        raise NotImplementedError

    @abstractmethod
    def to_json(self) -> dict[str, Any]:
        raise NotImplementedError
