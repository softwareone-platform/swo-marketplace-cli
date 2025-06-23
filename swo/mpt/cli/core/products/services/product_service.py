import json
from typing import Any

from requests_toolbelt import MultipartEncoder  # type: ignore
from swo.mpt.cli.core.errors import MPTAPIError
from swo.mpt.cli.core.handlers.errors import RequiredFieldsError, RequiredSheetsError
from swo.mpt.cli.core.services.base_service import BaseService
from swo.mpt.cli.core.services.service_result import ServiceResult


class ProductService(BaseService):
    def create(self) -> ServiceResult:
        """
        Creates a new product using the general data from the file manager.

        Returns:
            ServiceResult: The result of the creation operation.
        """
        product = self.file_manager.read_data()
        data = MultipartEncoder(
            fields={
                "product": json.dumps(product.to_json()),
                "icon": product.icon,
            }
        )
        headers = {"Content-Type": data.content_type}
        try:
            new_product_data = self.api.post(data, headers=headers)
        except Exception as e:
            self._set_error(str(e))
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        product.id = new_product_data["id"]
        try:
            self.api.update(f"{product.id}/settings", data=product.settings.to_json())
        except MPTAPIError as e:
            self._set_error(str(e))
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        self._set_synced(product.id, product.coordinate)
        return ServiceResult(success=True, model=product, stats=self.stats)

    def export(self, context: dict[str, Any]) -> ServiceResult:
        """
        Exports a product by retrieving it from the API and writing its data to a
        new tab in a file.

        Args:
            context: A dictionary containing the product_id to export.

        Returns:
            ServiceResult: The result of the export operation.
        """
        product_id = context["product_id"]
        result = self.retrieve_from_mpt(product_id)
        product = result.model
        if not result.success or not product:
            return result

        self.file_manager.create_tab()
        self.file_manager.add(product)

        return ServiceResult(success=True, model=product, stats=self.stats)

    def retrieve(self) -> ServiceResult:
        """
        Retrieves a product's existence from the API based on the ID from the general data.
        If the product exists, returns it; otherwise, returns a success status with no model.

        Returns:
            ServiceResult: The result of the retrieval operation.
        """
        product = self.file_manager.read_data()
        if product.id is None:
            return ServiceResult(success=True, model=None, stats=self.stats)

        try:
            exists = self.api.exists({"id": product.id})
        except Exception as e:
            self._set_error(str(e))
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        return ServiceResult(success=True, model=product if exists else None, stats=self.stats)

    def retrieve_from_mpt(self, resource_id: str) -> ServiceResult:
        """
        Retrieves a product from the API using its resource ID.

        Args:
            resource_id (str): The ID of the product to retrieve.

        Returns:
            ServiceResult: The result of the retrieval operation.
        """
        try:
            product_data = self.api.get(resource_id)
        except Exception as e:
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        product = self.data_model.from_json(product_data)
        return ServiceResult(success=True, model=product, stats=self.stats)

    def validate_definition(self) -> ServiceResult:
        # TODO: Review this logic. It should be implemented in the file_manager
        if not self.file_manager.file_handler.exists():
            msg = "Provided file path doesn't exist"
            self.stats.errors.add_msg("", "", msg)
            return ServiceResult(success=False, errors=[msg], model=None, stats=self.stats)

        try:
            self.file_manager.check_required_tabs()
        except RequiredSheetsError as error:
            for section_name in error.details:
                self.stats.errors.add_msg(section_name, "", "Required tab doesn't exist")

            return ServiceResult(success=False, errors=[str(error)], model=None, stats=self.stats)

        try:
            self.file_manager.check_required_fields_by_section()
        except RequiredFieldsError as error:
            for field_name in error.details:
                self.stats.errors.add_msg(field_name, "", "Required field doesn't exist")

            return ServiceResult(success=False, errors=[str(error)], model=None, stats=self.stats)

        return ServiceResult(success=True, model=None, stats=self.stats)

    def update(self, resource_id: str) -> ServiceResult:
        """
        Updates an existing product by sending the modified general data to the API.

        Args:
            resource_id (str): The ID of the product to update.

        Returns:
            ServiceResult: The result of the update operation.
        """
        product = self.file_manager.read_data()
        try:
            self.api.update(product.id, product.to_json())
        except MPTAPIError as e:
            self._set_error(str(e))
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        return ServiceResult(success=True, model=product, stats=self.stats)
