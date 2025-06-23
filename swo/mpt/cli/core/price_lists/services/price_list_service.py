from typing import Any

from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.services.base_service import BaseService
from swo.mpt.cli.core.services.service_result import ServiceResult


class PriceListService(BaseService):
    def create(self) -> ServiceResult:
        """
        Creates a new price list using the general data from the file manager.

        Returns:
            ServiceResult: The result of the creation operation.
        """
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

    def export(self, context: dict[str, Any]) -> ServiceResult:
        """
        Exports a price list by retrieving it from the API and writing its data to a
        new tab in a file.

        Args:
            context: A dictionary containing the price_list_id to export.

        Returns:
            ServiceResult: The result of the export operation.
        """
        price_list_id = context["price_list_id"]
        result = self.retrieve_from_mpt(price_list_id)
        price_list = result.model
        if not result.success or not price_list:
            return result

        self.file_manager.create_tab()
        self.file_manager.add(price_list)

        return ServiceResult(success=True, model=price_list, stats=self.stats)

    def retrieve(self) -> ServiceResult:
        """
        Retrieves a price list's existence from the API based on the ID from the general data.
        If the price list exists, returns it; otherwise, returns a success status with no model.

        Returns:
            ServiceResult: The result of the retrieval operation.
        """
        price_list = self.file_manager.read_data()
        if price_list.id is None:
            return ServiceResult(success=True, model=None, stats=self.stats)

        try:
            exists = self.api.exists({"id": price_list.id})
        except MPTAPIError as e:
            self._set_error(str(e))
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        return ServiceResult(success=True, model=price_list if exists else None, stats=self.stats)

    def retrieve_from_mpt(self, resource_id: str) -> ServiceResult:
        """
        Retrieves a price list from the API using its resource ID.

        Args:
            resource_id: The ID of the price list to retrieve.

        Returns:
            ServiceResult: The result of the retrieval operation.
        """
        try:
            price_list_data = self.api.get(resource_id)
        except MPTAPIError as e:
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        price_list = self.data_model.from_json(price_list_data)
        return ServiceResult(success=True, model=price_list, stats=self.stats)

    def update(self, resource_id: str) -> ServiceResult:
        """
        Updates an existing price list by sending the modified general data to the API.

        Args:
            resource_id: The ID of the price list to update.

        Returns:
            ServiceResult: The result of the update operation.
        """
        price_list = self.file_manager.read_data()
        # TODO: this logic should be moved to the price list data model creation
        price_list.type = "operations" if self.account.is_operations() else "vendor"
        try:
            self.api.update(price_list.id, price_list.to_json())
        except MPTAPIError as e:
            self._set_error(str(e))
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        return ServiceResult(success=True, model=price_list, stats=self.stats)
