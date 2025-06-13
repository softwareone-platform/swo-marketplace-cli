from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Self


@dataclass
class BaseDataModel(ABC):
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:  # pragma: no cover
        raise NotImplementedError

    @classmethod
    # TODO: uncomment when the method is implemented for all subclasses
    # @abstractmethod
    def from_json(cls, data: dict[str, Any]) -> Self:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def to_json(self) -> dict[str, Any]:  # pragma: no cover
        raise NotImplementedError

    # TODO: uncomment when the method is implemented for all subclasses
    # @abstractmethod
    def to_xlsx(self) -> dict[str, Any]:  # pragma: no cover
        raise NotImplementedError
