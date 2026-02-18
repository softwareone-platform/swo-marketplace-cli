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
    def from_raw(cls, raw_input: str | None) -> "ItemAction":
        """Build an ItemAction enum from a raw value.

        Args:
            raw_input: Raw action value from parsed data.

        Returns:
            The normalized item action.

        """
        if raw_input is None:
            return cls.SKIP
        return cls(raw_input)


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
    def from_dict(cls, row_data: dict[str, Any]) -> Self:
        return cls(
            id=row_data[constants.PRICELIST_ITEMS_ID]["value"],
            coordinate=row_data[constants.PRICELIST_ITEMS_ID]["coordinate"],
            billing_frequency=row_data[constants.PRICELIST_ITEMS_BILLING_FREQUENCY]["value"],
            commitment=row_data[constants.PRICELIST_ITEMS_COMMITMENT]["value"],
            erp_id=row_data[constants.PRICELIST_ITEMS_ITEM_ERP_ID]["value"],
            item_id=row_data[constants.PRICELIST_ITEMS_ITEM_ID]["value"],
            item_name=row_data[constants.PRICELIST_ITEMS_ITEM_NAME]["value"],
            markup=row_data.get(constants.PRICELIST_ITEMS_MARKUP, {}).get("value"),
            status=ItemStatus(row_data[constants.PRICELIST_ITEMS_STATUS]["value"]),
            unit_lp=row_data[constants.PRICELIST_ITEMS_UNIT_LP]["value"],
            unit_pp=row_data[constants.PRICELIST_ITEMS_UNIT_PP]["value"],
            unit_sp=row_data.get(constants.PRICELIST_ITEMS_UNIT_SP, {}).get("value"),
            vendor_id=row_data[constants.PRICELIST_ITEMS_ITEM_VENDOR_ID]["value"],
            action=ItemAction.from_raw(row_data[constants.PRICELIST_ITEMS_ACTION]["value"]),
            type=row_data.get("type"),
        )

    @classmethod
    @override
    def from_json(cls, json_data: dict[str, Any]) -> Self:
        return cls(
            id=json_data.get("id", ""),
            billing_frequency=json_data["item"]["terms"]["period"],
            currency=json_data["priceList"]["currency"],
            commitment=json_data["item"]["terms"].get("commitment"),
            erp_id=json_data["item"]["externalIds"].get("operations"),
            item_id=json_data["item"]["id"],
            item_name=json_data["item"]["name"],
            lp_x1=json_data.get("LPx1"),
            lp_xm=json_data.get("LPxM"),
            lp_xy=json_data.get("LPxY"),
            markup=json_data.get("markup"),
            precision=json_data["priceList"]["precision"],
            pp_x1=json_data.get("PPx1"),
            pp_xm=json_data.get("PPxM"),
            pp_xy=json_data.get("PPxY"),
            sp_x1=json_data.get("SPx1"),
            sp_xm=json_data.get("SPxM"),
            sp_xy=json_data.get("SPxY"),
            status=ItemStatus(json_data["status"]),
            unit_lp=json_data.get("unitLP"),
            unit_pp=json_data.get("unitPP"),
            unit_sp=json_data.get("unitSP"),
            vendor_id=json_data["item"]["externalIds"]["vendor"],
            action=ItemAction.SKIP,
        )

    @override
    def to_json(self) -> dict[str, Any]:
        json_payload: dict[str, Any] = {
            "unitLP": self.unit_lp,
            "unitPP": self.unit_pp,
        }
        if self.is_vendor():
            json_payload["status"] = self.status.value

        if self.is_operations():
            json_payload["markup"] = self.markup
            if self.unit_sp is not None:
                json_payload["unitSP"] = self.unit_sp

            if self.status != "Draft":
                json_payload["status"] = self.status.value

        return json_payload

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
