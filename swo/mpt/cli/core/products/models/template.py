from dataclasses import dataclass
from typing import Any

from swo.mpt.cli.core.models import BaseDataModel
from swo.mpt.cli.core.products import constants


@dataclass
class TemplateData(BaseDataModel):
    id: str
    coordinate: str
    name: str
    type: str
    content: str
    content_coordinate: str
    default: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TemplateData":
        return cls(
            id=data[constants.TEMPLATES_ID]["value"],
            coordinate=data[constants.TEMPLATES_ID]["coordinate"],
            name=data[constants.TEMPLATES_NAME]["value"],
            type=data[constants.TEMPLATES_TYPE]["value"],
            content=data[constants.TEMPLATES_CONTENT]["value"],
            content_coordinate=data[constants.TEMPLATES_CONTENT]["coordinate"],
            default=data[constants.TEMPLATES_DEFAULT]["value"] == "True",
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "content": self.content,
            "default": self.default,
        }
