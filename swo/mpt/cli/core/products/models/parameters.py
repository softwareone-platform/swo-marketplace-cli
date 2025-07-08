import json
from abc import ABC
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Any, Self, TypeVar

from dateutil import parser
from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.products import constants
from swo.mpt.cli.core.products.models import DataActionEnum
from swo.mpt.cli.core.products.models.mixins import ActionMixin

BaseParametersData = TypeVar("BaseParametersData", bound="ParametersData")


class ParamScopeEnum(StrEnum):
    AGREEMENT = "Agreement"
    ITEM = "Item"
    REQUEST = "Request"
    SUBSCRIPTION = "Subscription"


@dataclass
class ParametersData(BaseDataModel, ActionMixin, ABC):
    id: str
    description: str
    display_order: int
    external_id: str | None
    name: str
    phase: str  # TODO: create enum
    type: str
    constraints: dict[str, Any]
    options: dict[str, Any]

    coordinate: str | None = None
    group_id: str | None = None
    group_id_coordinate: str | None = None
    group_name: str | None = None
    scope: ParamScopeEnum | None = None
    created_date: date | None = None
    updated_date: date | None = None

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
            action=DataActionEnum(data[constants.PARAMETERS_ACTION]["value"]),
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

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        updated = data["audit"].get("updated", {}).get("at")
        return cls(
            id=data["id"],
            description=data["description"],
            display_order=data["displayOrder"],
            external_id=data.get("externalId"),
            name=data["name"],
            phase=data["phase"],
            type=data["type"],
            constraints=data["constraints"],
            options=data["options"],
            group_id=data.get("group", {}).get("id"),
            group_name=data.get("group", {}).get("name"),
            created_date=parser.parse(data["audit"]["created"]["at"]).date(),
            updated_date=updated and parser.parse(updated).date() or None,
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

    def to_xlsx(self) -> dict[str, Any]:
        return {
            constants.PARAMETERS_ID: self.id,
            constants.PARAMETERS_NAME: self.name,
            constants.PARAMETERS_EXTERNALID: self.external_id,
            constants.PARAMETERS_ACTION: self.action,
            constants.PARAMETERS_PHASE: self.phase,
            constants.PARAMETERS_TYPE: self.type,
            constants.PARAMETERS_DESCRIPTION: self.description,
            constants.PARAMETERS_DISPLAY_ORDER: self.display_order,
            constants.PARAMETERS_GROUP_ID: self.group_id,
            constants.PARAMETERS_GROUP_NAME: self.group_name,
            constants.PARAMETERS_OPTIONS: json.dumps(self.options),
            constants.PARAMETERS_CONSTRAINTS: json.dumps(self.constraints),
            constants.PARAMETERS_CREATED: self.created_date,
            constants.PARAMETERS_MODIFIED: self.updated_date,
        }


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
