from dataclasses import dataclass, field
from typing import Any, Self, TypedDict

from swo.mpt.cli.core.models.data_model import BaseDataModel
from swo.mpt.cli.core.products import constants
from swo.mpt.cli.core.utils import set_dict_value


class SettingItem(TypedDict):
    name: str
    value: str
    coordinate: str


@dataclass
class SettingsData(BaseDataModel):
    items: list[SettingItem] = field(default_factory=list)
    json_path: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            items=[
                SettingItem(
                    name=item[constants.SETTINGS_SETTING]["value"],
                    value=item[constants.SETTINGS_VALUE]["value"],
                    coordinate=item[constants.SETTINGS_VALUE]["coordinate"],
                )
                for _, item in data.items()
            ]
        )

    def to_json(self) -> dict[str, Any]:
        settings: dict[str, Any] = {}
        for setting in self.items:
            settings_name = setting["name"]
            settings_value: str | bool = setting["value"]
            json_path = constants.SETTINGS_API_MAPPING[settings_name]

            # Convert value to boolean only for certain paths
            if ".label" not in json_path and ".title" not in json_path:
                settings_value = settings_value == "Enabled"

            settings = set_dict_value(settings, json_path, settings_value)

        return settings


@dataclass
class ProductData(BaseDataModel):
    id: int
    coordinate: str
    name: str
    short_description: str
    long_description: str
    website: int
    settings: SettingsData
    external_ids: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            id=data[constants.GENERAL_PRODUCT_ID]["value"],
            coordinate=data[constants.GENERAL_PRODUCT_ID]["coordinate"],
            name=data[constants.GENERAL_PRODUCT_NAME]["value"],
            short_description=data[constants.GENERAL_CATALOG_DESCRIPTION]["value"],
            long_description=data[constants.GENERAL_PRODUCT_DESCRIPTION]["value"],
            website=data[constants.GENERAL_PRODUCT_WEBSITE]["value"],
            settings=SettingsData.from_dict(data["settings"]),
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "shortDescription": self.short_description,
            "longDescription": self.long_description,
            "website": self.website,
            "externalIds": None,
            "settings": None,
        }
