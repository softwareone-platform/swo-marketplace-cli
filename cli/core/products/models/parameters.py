import datetime as dt
import json
from abc import ABC
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Self, TypeVar, override

from cli.core.models import BaseDataModel
from cli.core.products import constants
from cli.core.products.models import DataActionEnum
from cli.core.products.models.mixins import ActionMixin
from dateutil import parser

BaseParametersData = TypeVar("BaseParametersData", bound="ParametersData")


class ParamScopeEnum(StrEnum):
    """Enumeration for parameter scope."""

    AGREEMENT = "Agreement"
    ASSET = "Asset"
    ITEM_SCOPE = "Item"
    REQUEST = "Request"
    SUBSCRIPTION = "Subscription"


@dataclass
class ParametersData(BaseDataModel, ActionMixin, ABC):
    """Abstract data model representing parameters."""

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
    created_date: dt.date | None = None
    updated_date: dt.date | None = None

    @property
    def group(self) -> dict[str, Any] | None:
        if self.is_order_request():
            return {"id": self.group_id}

        return None

    @classmethod
    @override
    def from_dict(cls, row_data: dict[str, Any]) -> Self:
        return cls(
            id=row_data[constants.PARAMETERS_ID]["value"],
            coordinate=row_data[constants.PARAMETERS_ID]["coordinate"],
            action=DataActionEnum(row_data[constants.PARAMETERS_ACTION]["value"]),
            description=row_data[constants.PARAMETERS_DESCRIPTION]["value"],
            display_order=row_data[constants.PARAMETERS_DISPLAY_ORDER]["value"],
            external_id=row_data[constants.PARAMETERS_EXTERNALID]["value"],
            name=row_data[constants.PARAMETERS_NAME]["value"],
            phase=row_data[constants.PARAMETERS_PHASE]["value"],
            type=row_data[constants.PARAMETERS_TYPE]["value"],
            constraints=json.loads(row_data[constants.PARAMETERS_CONSTRAINTS]["value"]),
            options=json.loads(row_data[constants.PARAMETERS_OPTIONS]["value"]),
            group_id=row_data[constants.PARAMETERS_GROUP_ID]["value"],
            group_id_coordinate=row_data[constants.PARAMETERS_GROUP_ID]["coordinate"],
        )

    @classmethod
    @override
    def from_json(cls, json_data: dict[str, Any]) -> Self:
        updated = json_data["audit"].get("updated", {}).get("at")
        return cls(
            id=json_data["id"],
            description=json_data["description"],
            display_order=json_data["displayOrder"],
            external_id=json_data.get("externalId"),
            name=json_data["name"],
            phase=json_data["phase"],
            type=json_data["type"],
            constraints=json_data["constraints"],
            options=json_data["options"],
            group_id=json_data.get("group", {}).get("id"),
            group_name=json_data.get("group", {}).get("name"),
            created_date=parser.parse(json_data["audit"]["created"]["at"]).date(),
            updated_date=(updated and parser.parse(updated).date()) or None,
        )

    def is_order_request(self) -> bool:
        """Determine if the parameter is for an order request.

        Returns:
            True if the phase is 'Order' and the scope is not ITEM_SCOPE or REQUEST,
            otherwise False.

        """
        return self.phase == "Order" and self.scope not in {
            ParamScopeEnum.ITEM_SCOPE,
            ParamScopeEnum.REQUEST,
        }

    @override
    def to_json(self) -> dict[str, Any]:
        json_payload: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "scope": str(self.scope),
            "phase": self.phase,
            "type": self.type,
            "options": {
                key: option_value for key, option_value in self.options.items() if key != "label"
            },
            "constraints": self.constraints,
            "externalId": self.external_id,
            "displayOrder": self.display_order,
        }
        if self.group is not None:
            json_payload["group"] = self.group

        return json_payload

    @override
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
    """Data model representing agreement parameters."""

    scope: ParamScopeEnum = ParamScopeEnum.AGREEMENT


@dataclass
class AssetParametersData(ParametersData):
    """Data model representing agreement parameters."""

    scope: ParamScopeEnum = ParamScopeEnum.ASSET


@dataclass
class ItemParametersData(ParametersData):
    """Data model representing item parameters."""

    scope: ParamScopeEnum = ParamScopeEnum.ITEM_SCOPE


@dataclass
class RequestParametersData(ParametersData):
    """Data model representing request parameters."""

    scope: ParamScopeEnum = ParamScopeEnum.REQUEST


@dataclass
class SubscriptionParametersData(ParametersData):
    """Data model representing subscription parameters."""

    scope: ParamScopeEnum = ParamScopeEnum.SUBSCRIPTION
