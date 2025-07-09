import os
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Self

from dateutil import parser
from swo.mpt.cli.core.models.data_model import BaseDataModel
from swo.mpt.cli.core.products import constants
from swo.mpt.cli.core.products.models.mixins import ActionMixin
from swo.mpt.cli.core.utils import set_dict_value


@dataclass
class SettingsItem(BaseDataModel, ActionMixin):
    name: str
    value: str | bool

    coordinate: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            action=data[constants.SETTINGS_ACTION]["value"],
            name=data[constants.SETTINGS_SETTING]["value"],
            coordinate=data[constants.SETTINGS_SETTING]["coordinate"],
            value=data[constants.SETTINGS_VALUE]["value"],
        )

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls(name=data["name"], value=cls._parse_json_value(data["value"]))

    def to_json(self) -> dict[str, Any]:
        return {}

    def to_xlsx(self) -> dict[str, Any]:
        return {
            constants.SETTINGS_SETTING: self.name,
            constants.SETTINGS_ACTION: self.action,
            constants.SETTINGS_VALUE: self.value,
        }

    @staticmethod
    def _parse_json_value(value: str | bool) -> str | bool:
        match value:
            case True:
                return "Enabled"
            case False:
                return "Off"

        return value


@dataclass
class SettingsData(BaseDataModel):
    items: list[SettingsItem] = field(default_factory=list)
    json_path: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(items=[SettingsItem.from_dict(data)])

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        formatted_settings = cls._format_data_from_json(data)
        items = [
            SettingsItem.from_json({"name": key, "value": formatted_settings.get(value)})
            for key, value in constants.SETTINGS_API_MAPPING.items()
        ]
        return cls(items=items)

    def to_json(self) -> dict[str, Any]:
        settings: dict[str, Any] = {}
        for setting_item in self.items:
            settings_name = setting_item.name
            settings_value: str | bool = setting_item.value
            json_path = constants.SETTINGS_API_MAPPING[settings_name]

            # Convert value to boolean only for certain paths
            if ".label" not in json_path and ".title" not in json_path:
                settings_value = settings_value == "Enabled"

            settings = set_dict_value(settings, json_path, settings_value)

        return {"settings": settings}

    def to_xlsx(self) -> dict[str, Any]:
        return {}

    @staticmethod
    def _format_data_from_json(data: dict[str, Any]) -> dict[str, Any]:
        formatted_data = {}
        for key, value in data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    formatted_data[f"{key}.{sub_key}"] = sub_value
            else:
                formatted_data[key] = value

        return formatted_data


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
            account_id=data["vendor"]["id"],
            account_name=data["vendor"]["name"],
            short_description=data["shortDescription"],
            long_description=data["longDescription"],
            website=data["website"],
            status=data["status"],
            created_date=parser.parse(data["audit"]["created"]["at"]).date(),
            updated_date=updated and parser.parse(updated).date() or None,
            settings=SettingsData.from_json(data["settings"]),
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
