import os
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Self, TypedDict

from dateutil import parser
from swo.mpt.cli.core.models.data_model import BaseDataModel
from swo.mpt.cli.core.products import constants
from swo.mpt.cli.core.utils import set_dict_value


class SettingItem(TypedDict):
    name: str
    value: str
    coordinate: str | None


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
    id: str
    name: str
    short_description: str
    long_description: str
    website: str

    settings: SettingsData
    account_id: str | None = None
    account_name: str | None = None
    coordinate: str | None = None
    export_date: date = field(default_factory=date.today)
    icon: bytes | None = None
    status: str | None = None
    created_date: date | None = None
    updated_date: date | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        settings = (
            SettingsData.from_dict(data["settings"]) if "settings" in data else SettingsData()
        )
        return cls(
            id=data[constants.GENERAL_PRODUCT_ID]["value"],
            coordinate=data[constants.GENERAL_PRODUCT_ID]["coordinate"],
            name=data[constants.GENERAL_PRODUCT_NAME]["value"],
            short_description=data[constants.GENERAL_CATALOG_DESCRIPTION]["value"],
            long_description=data[constants.GENERAL_PRODUCT_DESCRIPTION]["value"],
            website=data[constants.GENERAL_PRODUCT_WEBSITE]["value"],
            settings=settings,
            account_id=data.get(constants.GENERAL_ACCOUNT_ID),
            account_name=data.get(constants.GENERAL_ACCOUNT_NAME),
            export_date=data.get(constants.GENERAL_EXPORT_DATE, {}).get("value"),
            status=data[constants.GENERAL_STATUS]["value"],
            icon=cls._get_default_icon(),
        )

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        updated = data["audit"].get("updated", {}).get("at")
        return cls(
            id=data["id"],
            name=data["name"],
            short_description=data["shortDescription"],
            long_description=data["longDescription"],
            website=data["website"],
            export_date=date.today(),
            created_date=parser.parse(data["audit"]["created"]["at"]).date(),
            updated_date=updated and parser.parse(updated).date() or None,
            settings=cls._get_settings_from_json(data["settings"]),
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "shortDescription": self.short_description,
            "longDescription": self.long_description,
            "website": self.website,
        }

    def to_xlsx(self) -> dict[str, Any]:
        return {
            constants.GENERAL_PRODUCT_ID: self.id,
            constants.GENERAL_PRODUCT_NAME: self.name,
            constants.GENERAL_CATALOG_DESCRIPTION: self.short_description,
            constants.GENERAL_PRODUCT_DESCRIPTION: self.long_description,
            constants.GENERAL_PRODUCT_WEBSITE: self.website,
            constants.GENERAL_ACCOUNT_ID: self.account_id,
            constants.GENERAL_ACCOUNT_NAME: self.account_name,
            constants.GENERAL_EXPORT_DATE: self.export_date,
            constants.GENERAL_STATUS: self.status,
            constants.GENERAL_CREATED: self.created_date,
            constants.GENERAL_MODIFIED: self.updated_date,
        }

    @staticmethod
    def _get_default_icon() -> bytes:
        icon = Path(os.path.dirname(__file__)) / "icons/fake-icon.png"
        return open(icon, "rb").read()

    @staticmethod
    def _get_settings_from_json(settings) -> SettingsData:
        items = []
        for key, value in settings.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    items.append(
                        SettingItem(name=f"{key}.{sub_key}", value=sub_value, coordinate=None)
                    )
            else:
                items.append(SettingItem(name=key, value=value, coordinate=None))

        return SettingsData(items=items)
