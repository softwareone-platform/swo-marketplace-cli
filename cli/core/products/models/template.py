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
    template_content: str

    coordinate: str | None = None
    content_coordinate: str | None = None
    default: bool | None = None
    created_date: dt.date | None = None
    updated_date: dt.date | None = None

    @classmethod
    @override
    def from_dict(cls, row_data: dict[str, Any]) -> Self:
        default = row_data[constants.TEMPLATES_DEFAULT]["value"]
        return cls(
            id=row_data[constants.TEMPLATES_ID]["value"],
            coordinate=row_data[constants.TEMPLATES_ID]["coordinate"],
            action=DataActionEnum(row_data[constants.TEMPLATES_ACTION]["value"]),
            name=row_data[constants.TEMPLATES_NAME]["value"],
            type=row_data[constants.TEMPLATES_TYPE]["value"],
            template_content=row_data[constants.TEMPLATES_CONTENT]["value"],
            content_coordinate=row_data[constants.TEMPLATES_CONTENT]["coordinate"],
            default=None if default is None else default == "True",
        )

    @classmethod
    @override
    def from_json(cls, json_data: dict[str, Any]) -> Self:
        updated = json_data["audit"].get("updated", {}).get("at")
        return cls(
            id=json_data["id"],
            name=json_data["name"],
            type=json_data["type"],
            template_content=json_data["content"],
            default=json_data.get("default"),
            created_date=parser.parse(json_data["audit"]["created"]["at"]).date(),
            updated_date=(updated and parser.parse(updated).date()) or None,
        )

    @override
    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "content": self.template_content,
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
            constants.TEMPLATES_CONTENT: self.template_content,
            constants.TEMPLATES_CREATED: self.created_date,
            constants.TEMPLATES_MODIFIED: self.updated_date,
        }
