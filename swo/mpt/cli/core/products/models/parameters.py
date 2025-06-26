import json
from abc import ABC
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Self, TypeVar

from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.products import constants

BaseParametersData = TypeVar("BaseParametersData", bound="ParametersData")


class ParamScopeEnum(StrEnum):
    AGREEMENT = "Agreement"
    ITEM = "Item"
    REQUEST = "Request"
    SUBSCRIPTION = "Subscription"


@dataclass
class ParametersData(BaseDataModel, ABC):
    id: str
    coordinate: str
    description: str
    display_order: int
    external_id: str
    group_id: str
    group_id_coordinate: str
    name: str
    phase: str  # TODO: create enum
    type: str
    constraints: dict[str, Any]
    options: dict[str, Any]
    scope: ParamScopeEnum | None = None

    @property
    def group(self) -> dict[str, Any] | None:
        if self.is_order_request():
            return {"id": self.group_id}

        return None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            id=data[constants.PARAMETERS_ID]["value"],
            coordinate=data[constants.PARAMETERS_ID]["coordinate"],
            description=data[constants.PARAMETERS_DESCRIPTION]["value"],
            display_order=data[constants.PARAMETERS_DISPLAY_ORDER]["value"],
            external_id=data[constants.PARAMETERS_EXTERNALID]["value"],
            name=data[constants.PARAMETERS_NAME]["value"],
            phase=data[constants.PARAMETERS_PHASE]["value"],
            type=data[constants.PARAMETERS_TYPE]["value"],
            constraints=json.loads(data[constants.PARAMETERS_CONSTRAINTS]["value"]),
            options=json.loads(data[constants.PARAMETERS_OPTIONS]["value"]),
            group_id=data[constants.PARAMETERS_GROUP_ID]["value"],
            group_id_coordinate=data[constants.PARAMETERS_GROUP_ID]["coordinate"],
        )

    def is_order_request(self) -> bool:
        return self.phase == "Order" and self.scope not in (
            ParamScopeEnum.ITEM,
            ParamScopeEnum.REQUEST,
        )

    def to_json(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "scope": str(self.scope),
            "phase": self.phase,
            "type": self.type,
            "options": {key: value for key, value in self.options.items() if key != "label"},
            "constraints": self.constraints,
            "externalId": self.external_id,
            "displayOrder": self.display_order,
        }
        if self.group is not None:
            data["group"] = self.group

        return data


@dataclass
class AgreementParametersData(ParametersData):
    scope: ParamScopeEnum = ParamScopeEnum.AGREEMENT


@dataclass
class ItemParametersData(ParametersData):
    scope: ParamScopeEnum = ParamScopeEnum.ITEM


@dataclass
class RequestParametersData(ParametersData):
    scope: ParamScopeEnum = ParamScopeEnum.REQUEST


@dataclass
class SubscriptionParametersData(ParametersData):
    scope: ParamScopeEnum = ParamScopeEnum.SUBSCRIPTION
