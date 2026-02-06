import datetime as dt
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Self, override

from cli.core.models import BaseDataModel
from cli.core.price_lists import constants


class ItemAction(StrEnum):
    """Enumeration of possible actions for a price list item."""

    SKIP = "-"
    SKIPPED = ""
    UPDATE = "update"

    @classmethod
    def _missing_(cls, value: object) -> "ItemAction":  # noqa: WPS120
        if value is None:
            return cls.SKIP
        return super()._missing_(value)


class ItemStatus(StrEnum):
    """Enumeration of possible statuses for a price list item."""

    DRAFT = "Draft"
    FOR_SALE = "ForSale"
    PRIVATE = "Private"


@dataclass
class ItemData(BaseDataModel):
    """Data model representing a price list item."""

    id: str
    billing_frequency: str
    commitment: str | None
    erp_id: str | None
    item_id: str
    item_name: str
    markup: float | None
    status: ItemStatus
    unit_lp: float | None
    unit_pp: float | None
    unit_sp: float | None
    vendor_id: str

    action: ItemAction = ItemAction.SKIP
    coordinate: str | None = None
    currency: str | None = None
    lp_x1: float | None = None
    lp_xm: float | None = None
    lp_xy: float | None = None
    modified_date: dt.date | None = None
    precision: int | None = None
    pp_x1: float | None = None
    pp_xm: float | None = None
    pp_xy: float | None = None
    sp_x1: float | None = None
    sp_xm: float | None = None
    sp_xy: float | None = None
    type: str | None = None

    def is_operations(self) -> bool:
        """Check if the item type is 'operations'."""
        return self.type == "operations"

    def is_vendor(self) -> bool:
        """Check if the item type is 'vendor'."""
        return self.type == "vendor"

    def to_update(self) -> bool:
        """Check if the item action is 'UPDATE'."""
        return self.action == ItemAction.UPDATE

    @classmethod
    @override
    def from_dict(cls, source_dict: dict[str, Any]) -> Self:
        return cls(
            id=source_dict[constants.PRICELIST_ITEMS_ID]["value"],
            coordinate=source_dict[constants.PRICELIST_ITEMS_ID]["coordinate"],
            billing_frequency=source_dict[constants.PRICELIST_ITEMS_BILLING_FREQUENCY]["value"],
            commitment=source_dict[constants.PRICELIST_ITEMS_COMMITMENT]["value"],
            erp_id=source_dict[constants.PRICELIST_ITEMS_ITEM_ERP_ID]["value"],
            item_id=source_dict[constants.PRICELIST_ITEMS_ITEM_ID]["value"],
            item_name=source_dict[constants.PRICELIST_ITEMS_ITEM_NAME]["value"],
            markup=source_dict.get(constants.PRICELIST_ITEMS_MARKUP, {}).get("value"),
            status=ItemStatus(source_dict[constants.PRICELIST_ITEMS_STATUS]["value"]),
            unit_lp=source_dict[constants.PRICELIST_ITEMS_UNIT_LP]["value"],
            unit_pp=source_dict[constants.PRICELIST_ITEMS_UNIT_PP]["value"],
            unit_sp=source_dict.get(constants.PRICELIST_ITEMS_UNIT_SP, {}).get("value"),
            vendor_id=source_dict[constants.PRICELIST_ITEMS_ITEM_VENDOR_ID]["value"],
            action=ItemAction(source_dict[constants.PRICELIST_ITEMS_ACTION]["value"]),
            type=source_dict.get("type"),
        )

    @classmethod
    @override
    def from_json(cls, json_dict: dict[str, Any]) -> Self:
        return cls(
            id=json_dict.get("id", ""),
            billing_frequency=json_dict["item"]["terms"]["period"],
            currency=json_dict["priceList"]["currency"],
            commitment=json_dict["item"]["terms"].get("commitment"),
            erp_id=json_dict["item"]["externalIds"].get("operations"),
            item_id=json_dict["item"]["id"],
            item_name=json_dict["item"]["name"],
            lp_x1=json_dict.get("LPx1"),
            lp_xm=json_dict.get("LPxM"),
            lp_xy=json_dict.get("LPxY"),
            markup=json_dict.get("markup"),
            precision=json_dict["priceList"]["precision"],
            pp_x1=json_dict.get("PPx1"),
            pp_xm=json_dict.get("PPxM"),
            pp_xy=json_dict.get("PPxY"),
            sp_x1=json_dict.get("SPx1"),
            sp_xm=json_dict.get("SPxM"),
            sp_xy=json_dict.get("SPxY"),
            status=ItemStatus(json_dict["status"]),
            unit_lp=json_dict.get("unitLP"),
            unit_pp=json_dict.get("unitPP"),
            unit_sp=json_dict.get("unitSP"),
            vendor_id=json_dict["item"]["externalIds"]["vendor"],
            action=ItemAction.SKIP,
        )

    @override
    def to_json(self) -> dict[str, Any]:
        json_output: dict[str, Any] = {
            "unitLP": self.unit_lp,
            "unitPP": self.unit_pp,
        }
        if self.is_vendor():
            json_output["status"] = self.status.value

        if self.is_operations():
            json_output["markup"] = self.markup
            if self.unit_sp is not None:
                json_output["unitSP"] = self.unit_sp

            if self.status != "Draft":
                json_output["status"] = self.status.value

        return json_output

    @override
    def to_xlsx(self) -> dict[str, Any]:
        return {
            constants.PRICELIST_ITEMS_ID: self.id,
            constants.PRICELIST_ITEMS_ITEM_ID: self.item_id,
            constants.PRICELIST_ITEMS_ITEM_NAME: self.item_name,
            constants.PRICELIST_ITEMS_ITEM_VENDOR_ID: self.vendor_id,
            constants.PRICELIST_ITEMS_ITEM_ERP_ID: self.erp_id,
            constants.PRICELIST_ITEMS_BILLING_FREQUENCY: self.billing_frequency,
            constants.PRICELIST_ITEMS_COMMITMENT: self.commitment,
            constants.PRICELIST_ITEMS_UNIT_LP: self.unit_lp,
            constants.PRICELIST_ITEMS_UNIT_PP: self.unit_pp,
            constants.PRICELIST_ITEMS_MARKUP: self.markup,
            constants.PRICELIST_ITEMS_PPx1: self.pp_x1,
            constants.PRICELIST_ITEMS_PPxM: self.pp_xm,
            constants.PRICELIST_ITEMS_PPxY: self.pp_xy,
            constants.PRICELIST_ITEMS_UNIT_SP: self.unit_sp,
            constants.PRICELIST_ITEMS_SPx1: self.sp_x1,
            constants.PRICELIST_ITEMS_SPxM: self.sp_xm,
            constants.PRICELIST_ITEMS_SPxY: self.sp_xy,
            constants.PRICELIST_ITEMS_LPx1: self.lp_x1,
            constants.PRICELIST_ITEMS_LPxM: self.lp_xm,
            constants.PRICELIST_ITEMS_LPxY: self.lp_xy,
            constants.PRICELIST_ITEMS_STATUS: self.status.value,
            constants.PRICELIST_ITEMS_ACTION: self.action.value,
            constants.PRICELIST_ITEMS_MODIFIED: self.modified_date,
        }
