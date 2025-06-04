from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, TypeVar

DataModel = TypeVar("DataModel", bound="BaseDataModel")


@dataclass
class BaseDataModel(ABC):
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseDataModel":  # pragma: no cover
        raise NotImplementedError

    @classmethod
    # TODO: uncomment when the method is implemented for all subclasses
    # @abstractmethod
    def from_json(cls, data: dict[str, Any]) -> "BaseDataModel":  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def to_json(self) -> dict[str, Any]:  # pragma: no cover
        raise NotImplementedError
