import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Self, override

from cli.core.models.data_model import BaseDataModel
from cli.core.nested_dicts import set_dict_value
from cli.core.products import constants
from cli.core.products.models.mixins import ActionMixin
from dateutil import parser


@dataclass
class SettingsRecords(BaseDataModel, ActionMixin):
    """Data model representing a product settings item."""

    name: str
    setting_value: str | bool

    coordinate: str | None = None

    @classmethod
    @override
    def from_dict(cls, row_data: dict[str, Any]) -> Self:
        return cls(
            action=row_data[constants.SETTINGS_ACTION]["value"],
            name=row_data[constants.SETTINGS_SETTING]["value"],
            coordinate=row_data[constants.SETTINGS_SETTING]["coordinate"],
            setting_value=row_data[constants.SETTINGS_VALUE]["value"],
        )

    @classmethod
    @override
    def from_json(cls, json_data: dict[str, Any]) -> Self:
        raw_value = json_data["value"]
        match raw_value:
            case True:
                setting_value = "Enabled"
            case False:
                setting_value = "Off"
            case _:
                setting_value = raw_value

        return cls(
            name=json_data["name"],
            setting_value=setting_value,
        )

    @override
    def to_json(self) -> dict[str, Any]:
        return {}

    @override
    def to_xlsx(self) -> dict[str, Any]:
        return {
            constants.SETTINGS_SETTING: self.name,
            constants.SETTINGS_ACTION: self.action,
            constants.SETTINGS_VALUE: self.setting_value,
        }


@dataclass
class SettingsData(BaseDataModel):
    """Data model representing product settings configuration."""

    records: list[SettingsRecords] = field(default_factory=list)
    json_path: str | None = None

    @classmethod
    @override
    def from_dict(cls, row_data: dict[str, Any]) -> Self:
        return cls(records=[SettingsRecords.from_dict(row_data)])

    @classmethod
    @override
    def from_json(cls, json_data: dict[str, Any]) -> Self:
        formatted_settings = {}
        for key, raw_setting in json_data.items():
            if isinstance(raw_setting, dict):
                for sub_key, sub_value in raw_setting.items():
                    formatted_settings[f"{key}.{sub_key}"] = sub_value
            else:
                formatted_settings[key] = raw_setting

        records = [
            SettingsRecords.from_json({"name": key, "value": formatted_settings.get(setting_path)})
            for key, setting_path in constants.SETTINGS_API_MAPPING.items()
        ]
        return cls(records=records)

    @override
    def to_json(self) -> dict[str, Any]:
        settings: dict[str, Any] = {}
        for setting_item in self.records:
            settings_name = setting_item.name
            settings_value: str | bool = setting_item.setting_value
            json_path = constants.SETTINGS_API_MAPPING[settings_name]

            # Convert value to boolean only for certain paths
            if ".label" not in json_path and ".title" not in json_path:
                settings_value = settings_value == "Enabled"

            settings = set_dict_value(settings, json_path, settings_value)

        return {"settings": settings}

    @override
    def to_xlsx(self) -> dict[str, Any]:
        return {}


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
    def from_dict(cls, row_data: dict[str, Any]) -> Self:
        settings = (
            SettingsData.from_dict(row_data["settings"])
            if "settings" in row_data
            else SettingsData()
        )
        icon_path = Path(Path(__file__).parent) / "icons/fake-icon.png"
        default_icon = Path(icon_path).read_bytes()
        return cls(
            id=row_data[constants.GENERAL_PRODUCT_ID]["value"],
            coordinate=row_data[constants.GENERAL_PRODUCT_ID]["coordinate"],
            name=row_data[constants.GENERAL_PRODUCT_NAME]["value"],
            short_description=row_data[constants.GENERAL_CATALOG_DESCRIPTION]["value"],
            long_description=row_data[constants.GENERAL_PRODUCT_DESCRIPTION]["value"],
            website=row_data[constants.GENERAL_PRODUCT_WEBSITE]["value"],
            settings=settings,
            account_id=row_data.get(constants.GENERAL_ACCOUNT_ID),
            account_name=row_data.get(constants.GENERAL_ACCOUNT_NAME),
            export_date=row_data.get(constants.GENERAL_EXPORT_DATE, {}).get("value"),
            status=row_data[constants.GENERAL_STATUS]["value"],
            icon=default_icon,
        )

    @classmethod
    @override
    def from_json(cls, json_data: dict[str, Any]) -> Self:
        updated = json_data["audit"].get("updated", {}).get("at")
        return cls(
            id=json_data["id"],
            name=json_data["name"],
            account_id=json_data["vendor"]["id"],
            account_name=json_data["vendor"]["name"],
            short_description=json_data["shortDescription"],
            long_description=json_data["longDescription"],
            website=json_data["website"],
            status=json_data["status"],
            created_date=parser.parse(json_data["audit"]["created"]["at"]).date(),
            updated_date=(updated and parser.parse(updated).date()) or None,
            settings=SettingsData.from_json(json_data["settings"]),
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
