import datetime as dt
from dataclasses import dataclass
from typing import Any, Self, override

from cli.core.models import BaseDataModel
from cli.core.products import constants
from cli.core.products.models import DataActionEnum
from cli.core.products.models.mixins import ActionMixin
from dateutil import parser


@dataclass
class TemplateData(BaseDataModel, ActionMixin):
    """Data model representing a template resource."""

    id: str
    name: str
    type: str
    content: str

    coordinate: str | None = None
    content_coordinate: str | None = None
    default: bool | None = None
    created_date: dt.date | None = None
    updated_date: dt.date | None = None

    @classmethod
    @override
    def from_dict(cls, source_dict: dict[str, Any]) -> Self:
        default = source_dict[constants.TEMPLATES_DEFAULT]["value"]
        return cls(
            id=source_dict[constants.TEMPLATES_ID]["value"],
            coordinate=source_dict[constants.TEMPLATES_ID]["coordinate"],
            action=DataActionEnum(source_dict[constants.TEMPLATES_ACTION]["value"]),
            name=source_dict[constants.TEMPLATES_NAME]["value"],
            type=source_dict[constants.TEMPLATES_TYPE]["value"],
            content=source_dict[constants.TEMPLATES_CONTENT]["value"],
            content_coordinate=source_dict[constants.TEMPLATES_CONTENT]["coordinate"],
            default=None if default is None else default == "True",
        )

    @classmethod
    @override
    def from_json(cls, json_dict: dict[str, Any]) -> Self:
        updated = json_dict["audit"].get("updated", {}).get("at")
        return cls(
            id=json_dict["id"],
            name=json_dict["name"],
            type=json_dict["type"],
            content=json_dict["content"],
            default=json_dict.get("default"),
            created_date=parser.parse(json_dict["audit"]["created"]["at"]).date(),
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
            constants.TEMPLATES_DEFAULT: str(self.default) if self.default is not None else None,
            constants.TEMPLATES_CONTENT: self.content,
            constants.TEMPLATES_CREATED: self.created_date,
            constants.TEMPLATES_MODIFIED: self.updated_date,
        }
