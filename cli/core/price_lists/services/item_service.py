from typing import override

from cli.core.errors import MPTAPIError
from cli.core.price_lists.constants import (
    TAB_PRICE_ITEMS,
)
from cli.core.services import RelatedBaseService
from cli.core.services.service_result import ServiceResult


class ItemService(RelatedBaseService):
    """Service for managing price list item operations."""

    @override
    def create(self) -> ServiceResult:  # pragma: no cover
        return ServiceResult(
            success=False, errors=["Operation not implemented"], model=None, stats=self.stats
        )

    @override
    def export(self) -> ServiceResult:
        self.file_manager.create_tab()

        offset = 0
        while True:
            try:
                response = self.api.list({
                    "select": "audit,item.terms,priceList.precision,priceList.currency",
                    "offset": offset,
                    "limit": 100,
                })
            except MPTAPIError as error:
                self.stats.add_error(TAB_PRICE_ITEMS)
                error_msg = str(error)
                return ServiceResult(
                    success=False, model=None, errors=[error_msg], stats=self.stats
                )

            records = [self.data_model.from_json(record) for record in response["data"]]
            self.file_manager.add(records)
            if self._has_next_page(response["meta"]):
                offset += response["meta"]["limit"]
            else:
                break

        return ServiceResult(success=True, model=None, stats=self.stats)

    @override
    def retrieve(self) -> ServiceResult:  # pragma: no cover
        return ServiceResult(
            success=False, errors=["Operation not implemented"], model=None, stats=self.stats
        )

    @override
    def retrieve_from_mpt(self, resource_id: str) -> ServiceResult:
        try:
            response = self.api.get(resource_id)
        except MPTAPIError as error:
            error_msg = str(error)
            return ServiceResult(success=False, errors=[error_msg], model=None, stats=self.stats)

        item_model = self.data_model.from_json(response.json())
        return ServiceResult(success=True, model=item_model, stats=self.stats)

    @override
    def update(self) -> ServiceResult:
        errors: list[str] = []
        for record in self.file_manager.read_data():
            error_msg = self._update_record(record)
            if error_msg is not None:
                if error_msg != "SKIPPED":
                    errors.append(error_msg)
                    self._set_error(error_msg, record.id)
                continue
        return ServiceResult(success=not errors, errors=errors, model=None, stats=self.stats)

    def _has_next_page(self, meta_data: dict[str, int]) -> bool:
        return meta_data["offset"] + meta_data["limit"] < meta_data["total"]

    def _retrieve_item_data(self, vendor_id: str) -> dict[str, str] | None:
        response_data = self.api.list(
            query_params={"item.ExternalIds.vendor": vendor_id, "limit": 1}
        )["data"]
        if not response_data:
            return None
        return response_data[0]

    def _update_record(self, record) -> str | None:
        if not record.to_update():
            self._set_skipped()
            return "SKIPPED"
        try:
            item_data = self._retrieve_item_data(record.vendor_id)
        except MPTAPIError as error:
            return str(error)
        if item_data is None:
            return f"Cannot find item by vendor id: {record.vendor_id}"

        # TODO: this logic should be moved to the price list data model creation
        record.type = "operations" if self.account.is_operations() else "vendor"
        try:
            self.api.update(item_data["id"], record.to_json())
        except MPTAPIError as error:
            return f"Item {record.id}: {error!s}"

        self._set_synced(record.id, record.coordinate)
        return None
