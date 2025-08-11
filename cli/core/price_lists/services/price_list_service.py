from typing import override

from cli.core.errors import MPTAPIError
from cli.core.services import BaseService
from cli.core.services.service_result import ServiceResult


class PriceListService(BaseService):
    """Service for managing price list operations."""

    @override
    def create(self) -> ServiceResult:
        price_list = self.file_manager.read_data()
        # TODO: this logic should be moved to the price list data model creation
        price_list.type = "operations" if self.account.is_operations() else "vendor"
        try:
            new_price_list_data = self.api.post(json=price_list.to_json())
        except Exception as e:
            self._set_error(str(e))
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        price_list.id = new_price_list_data["id"]
        self._set_synced(price_list.id, price_list.coordinate)

        return ServiceResult(success=True, model=price_list, stats=self.stats)

    @override
    def export(self, resource_id: str) -> ServiceResult:
        result = self.retrieve_from_mpt(resource_id)
        price_list = result.model
        if not result.success or not price_list:
            return result

        self.file_manager.create_tab()
        self.file_manager.add(price_list)

        return ServiceResult(success=True, model=price_list, stats=self.stats)

    @override
    def retrieve(self) -> ServiceResult:
        price_list = self.file_manager.read_data()
        if price_list.id is None:
            return ServiceResult(success=True, model=None, stats=self.stats)

        try:
            exists = self.api.exists({"id": price_list.id})
        except MPTAPIError as e:
            self._set_error(str(e))
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        return ServiceResult(success=True, model=price_list if exists else None, stats=self.stats)

    @override
    def retrieve_from_mpt(self, resource_id: str) -> ServiceResult:
        try:
            price_list_data = self.api.get(resource_id)
        except MPTAPIError as e:
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        price_list = self.data_model.from_json(price_list_data)
        return ServiceResult(success=True, model=price_list, stats=self.stats)

    @override
    def update(self) -> ServiceResult:
        price_list = self.file_manager.read_data()
        # TODO: this logic should be moved to the price list data model creation
        price_list.type = "operations" if self.account.is_operations() else "vendor"
        try:
            self.api.update(price_list.id, price_list.to_json())
        except MPTAPIError as e:
            self._set_error(str(e))
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        return ServiceResult(success=True, model=price_list, stats=self.stats)
