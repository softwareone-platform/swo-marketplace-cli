import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Self, override

from cli.core.models.data_model import BaseDataModel
from cli.core.products import constants
from cli.core.products.models.mixins import ActionMixin
from cli.core.utils import set_dict_value
from dateutil import parser


@dataclass
class SettingsItem(BaseDataModel, ActionMixin):
    """Data model representing a product settings item."""

    name: str
    value: str | bool

    coordinate: str | None = None

    @classmethod
    @override
    def from_dict(cls, source_dict: dict[str, Any]) -> Self:
        return cls(
            action=source_dict[constants.SETTINGS_ACTION]["value"],
            name=source_dict[constants.SETTINGS_SETTING]["value"],
            coordinate=source_dict[constants.SETTINGS_SETTING]["coordinate"],
            value=source_dict[constants.SETTINGS_VALUE]["value"],
        )

    @classmethod
    @override
    def from_json(cls, json_dict: dict[str, Any]) -> Self:
        return cls(name=json_dict["name"], value=cls._parse_json_value(value=json_dict["value"]))

    @override
    def to_json(self) -> dict[str, Any]:
        return {}

    @override
    def to_xlsx(self) -> dict[str, Any]:
        return {
            constants.SETTINGS_SETTING: self.name,
            constants.SETTINGS_ACTION: self.action,
            constants.SETTINGS_VALUE: self.value,
        }

    @staticmethod
    def _parse_json_value(*, value: str | bool) -> str | bool:
        match value:
            case True:
                return "Enabled"
            case False:
                return "Off"

        return value


@dataclass
class SettingsData(BaseDataModel):
    """Data model representing product settings configuration."""

    items: list[SettingsItem] = field(default_factory=list)
    json_path: str | None = None

    @classmethod
    @override
    def from_dict(cls, source_dict: dict[str, Any]) -> Self:
        return cls(items=[SettingsItem.from_dict(source_dict)])

    @classmethod
    @override
    def from_json(cls, json_dict: dict[str, Any]) -> Self:
        formatted_settings = cls._format_data_from_json(json_dict)
        items = [
            SettingsItem.from_json({"name": key, "value": formatted_settings.get(value)})
            for key, value in constants.SETTINGS_API_MAPPING.items()
        ]
        return cls(items=items)

    @override
    def to_json(self) -> dict[str, Any]:
        settings_output: dict[str, Any] = {}
        for setting_item in self.items:
            settings_name = setting_item.name
            settings_value: str | bool = setting_item.value
            json_path = constants.SETTINGS_API_MAPPING[settings_name]

            # Convert value to boolean only for certain paths
            if ".label" not in json_path and ".title" not in json_path:
                settings_value = settings_value == "Enabled"

            settings_output = set_dict_value(settings_output, json_path, settings_value)

        return {"settings": settings_output}

    @override
    def to_xlsx(self) -> dict[str, Any]:
        return {}

    @staticmethod
    def _format_data_from_json(source_dict: dict[str, Any]) -> dict[str, Any]:
        formatted_output = {}
        for key, value in source_dict.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    formatted_output[f"{key}.{sub_key}"] = sub_value
            else:
                formatted_output[key] = value

        return formatted_output


@dataclass
class ProductData(BaseDataModel):
    """Data model representing a complete product."""

    id: str
    name: str
    short_description: str
    long_description: str
    website: str

    settings: SettingsData
    account_id: str | None = None
    account_name: str | None = None
    coordinate: str | None = None
    export_date: dt.date = field(default_factory=dt.date.today)
    icon: bytes | None = None
    status: str | None = None
    created_date: dt.date | None = None
    updated_date: dt.date | None = None

    @classmethod
    @override
    def from_dict(cls, source_dict: dict[str, Any]) -> Self:
        settings = (
            SettingsData.from_dict(source_dict["settings"])
            if "settings" in source_dict
            else SettingsData()
        )
        return cls(
            id=source_dict[constants.GENERAL_PRODUCT_ID]["value"],
            coordinate=source_dict[constants.GENERAL_PRODUCT_ID]["coordinate"],
            name=source_dict[constants.GENERAL_PRODUCT_NAME]["value"],
            short_description=source_dict[constants.GENERAL_CATALOG_DESCRIPTION]["value"],
            long_description=source_dict[constants.GENERAL_PRODUCT_DESCRIPTION]["value"],
            website=source_dict[constants.GENERAL_PRODUCT_WEBSITE]["value"],
            settings=settings,
            account_id=source_dict.get(constants.GENERAL_ACCOUNT_ID),
            account_name=source_dict.get(constants.GENERAL_ACCOUNT_NAME),
            export_date=source_dict.get(constants.GENERAL_EXPORT_DATE, {}).get("value"),
            status=source_dict[constants.GENERAL_STATUS]["value"],
            icon=cls._get_default_icon(),
        )

    @classmethod
    @override
    def from_json(cls, json_dict: dict[str, Any]) -> Self:
        updated = json_dict["audit"].get("updated", {}).get("at")
        return cls(
            id=json_dict["id"],
            name=json_dict["name"],
            account_id=json_dict["vendor"]["id"],
            account_name=json_dict["vendor"]["name"],
            short_description=json_dict["shortDescription"],
            long_description=json_dict["longDescription"],
            website=json_dict["website"],
            status=json_dict["status"],
            created_date=parser.parse(json_dict["audit"]["created"]["at"]).date(),
            updated_date=(updated and parser.parse(updated).date()) or None,
            settings=SettingsData.from_json(json_dict["settings"]),
        )

    @override
    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "shortDescription": self.short_description,
            "longDescription": self.long_description,
            "website": self.website,
        }

    @override
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
        icon_path = Path(Path(__file__).parent) / "icons/fake-icon.png"
        return Path(icon_path).open("rb").read()
