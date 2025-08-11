from dataclasses import dataclass
from datetime import date
from typing import Any, Self, override

from cli.core.models import BaseDataModel
from cli.core.products import constants
from cli.core.products.models import DataActionEnum
from cli.core.products.models.mixins import ActionMixin
from dateutil import parser


@dataclass
class TemplateData(BaseDataModel, ActionMixin):
    id: str
    name: str
    type: str
    content: str
    default: bool

    coordinate: str | None = None
    content_coordinate: str | None = None
    created_date: date | None = None
    updated_date: date | None = None

    @classmethod
    @override
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            id=data[constants.TEMPLATES_ID]["value"],
            coordinate=data[constants.TEMPLATES_ID]["coordinate"],
            action=DataActionEnum(data[constants.TEMPLATES_ACTION]["value"]),
            name=data[constants.TEMPLATES_NAME]["value"],
            type=data[constants.TEMPLATES_TYPE]["value"],
            content=data[constants.TEMPLATES_CONTENT]["value"],
            content_coordinate=data[constants.TEMPLATES_CONTENT]["coordinate"],
            default=data[constants.TEMPLATES_DEFAULT]["value"] == "True",
        )

    @classmethod
    @override
    def from_json(cls, data: dict[str, Any]) -> Self:
        updated = data["audit"].get("updated", {}).get("at")
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            content=data["content"],
            default=data["default"],
            created_date=parser.parse(data["audit"]["created"]["at"]).date(),
            updated_date=(updated and parser.parse(updated).date()) or None,
        )

    @override
    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "content": self.content,
            "default": self.default,
        }

    @override
    def to_xlsx(self) -> dict[str, Any]:
        return {
            constants.TEMPLATES_ID: self.id,
            constants.TEMPLATES_NAME: self.name,
            constants.TEMPLATES_ACTION: self.action,
            constants.TEMPLATES_TYPE: self.type,
            constants.TEMPLATES_DEFAULT: str(self.default),
            constants.TEMPLATES_CONTENT: self.content,
            constants.TEMPLATES_CREATED: self.created_date,
            constants.TEMPLATES_MODIFIED: self.updated_date,
        }
