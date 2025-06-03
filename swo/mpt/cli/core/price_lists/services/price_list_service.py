from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.price_lists.constants import TAB_GENERAL
from swo.mpt.cli.core.services.base_service import BaseService
from swo.mpt.cli.core.services.service_result import ServiceResult


class PriceListService(BaseService):
    def create(self) -> ServiceResult:
        price_list = self.file_handler.read_general_data()
        # TODO: this logic should be moved to the price list data model creation
        price_list.type = "operations" if self.account.is_operations() else "vendor"
        try:
            new_price_list_data = self.api.post(price_list.to_json())
        except Exception as e:
            self._set_error(str(e))
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        price_list.id = new_price_list_data["id"]
        self._set_synced(price_list.id, price_list.coordinate)

        return ServiceResult(success=True, model=price_list, stats=self.stats)

    def retrieve(self) -> ServiceResult:
        price_list = self.file_handler.read_general_data()
        if price_list.id is None:
            return ServiceResult(success=True, model=None, stats=self.stats)

        try:
            exists = self.api.exists({"id": price_list.id})
        except MPTAPIError as e:
            self._set_error(str(e))
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        return ServiceResult(success=True, model=price_list if exists else None, stats=self.stats)

    def retrieve_from_mpt(self, resource_id: str) -> ServiceResult:
        try:
            price_list_data = self.api.get(resource_id)
        except MPTAPIError as e:
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        price_list = self.data_model.from_json(price_list_data.json())
        return ServiceResult(success=True, model=price_list, stats=self.stats)

    def update(self, resource_id: str) -> ServiceResult:
        price_list = self.file_handler.read_general_data()
        # TODO: this logic should be moved to the price list data model creation
        price_list.type = "operations" if self.account.is_operations() else "vendor"
        try:
            self.api.update(price_list.id, price_list.to_json())
        except MPTAPIError as e:
            self._set_error(str(e))
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        return ServiceResult(success=True, model=price_list, stats=self.stats)

    def _set_error(self, error: str) -> None:
        self.file_handler.write_error(error)
        self.stats.add_error(TAB_GENERAL)

    def _set_synced(self, resource_id: str, item_coordinate: str) -> None:
        self.file_handler.write_id(item_coordinate, resource_id)
        self.stats.add_synced(TAB_GENERAL)

    def _set_skipped(self):
        self.stats.add_skipped(TAB_GENERAL)
