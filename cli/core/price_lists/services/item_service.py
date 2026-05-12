from typing import override

from cli.core.errors import MPTAPIError
from cli.core.price_lists.constants import (
    TAB_PRICE_ITEMS,
)
from cli.core.services import RelatedBaseService
from cli.core.services.service_result import ServiceResult

EXPORT_PAGE_SIZE = 100
EXPORT_SELECT = "audit,item.terms,priceList.precision,priceList.currency"


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
                    "select": EXPORT_SELECT,
                    "offset": offset,
                    "limit": EXPORT_PAGE_SIZE,
                })
            except MPTAPIError as error:
                self.stats.add_error(TAB_PRICE_ITEMS)
                return ServiceResult(
                    success=False, model=None, errors=[str(error)], stats=self.stats
                )

            self.file_manager.add([
                self.data_model.from_json(record) for record in response["data"]
            ])

            meta = response["meta"]
            if meta["offset"] + meta["limit"] >= meta["total"]:
                return ServiceResult(success=True, model=None, stats=self.stats)
            offset += EXPORT_PAGE_SIZE

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
            error_messages = [str(error)]
            return ServiceResult(success=False, errors=error_messages, model=None, stats=self.stats)

        item_model = self.data_model.from_json(response.json())
        return ServiceResult(success=True, model=item_model, stats=self.stats)

    @override
    def update(self) -> ServiceResult:
        errors = []
        for record in self.file_manager.read_data():
            error_message = self._update_one_record(record)
            if error_message is not None:
                errors.append(error_message)
        success = not errors
        return ServiceResult(success=success, errors=errors, model=None, stats=self.stats)

    def _update_one_record(self, record) -> str | None:
        if not record.to_update():
            self._set_skipped()
            return None

        query_params = {"item.ExternalIds.vendor": record.vendor_id, "limit": 1}
        try:
            response = self.api.list(query_params=query_params)
        except (MPTAPIError, KeyError) as error:
            self._set_error(error, record.id)
            return str(error)

        response_data = response.get("data", [])
        if not response_data:
            missing_item_error = ValueError(
                f"Item {record.id}: no matching item found for vendor {record.vendor_id}"
            )
            self._set_error(missing_item_error, record.id)
            return str(missing_item_error)

        # TODO: this logic should be moved to the price list data model creation
        record.type = "operations" if self.account.is_operations() else "vendor"
        try:
            self.api.update(response_data[0]["id"], record.to_json())
        except MPTAPIError as error:
            self._set_error(error, record.id)
            return f"Item {record.id}: {error!s}"

        self._set_synced(record.id, record.coordinate)
        return None
