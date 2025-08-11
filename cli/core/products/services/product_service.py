import json

from typing_extensions import override

from cli.core.errors import MPTAPIError
from cli.core.handlers.errors import RequiredFieldsError, RequiredSheetsError
from cli.core.products.handlers import SettingsExcelFileManager
from cli.core.products.models import DataActionEnum, SettingsData
from cli.core.services.base_service import BaseService
from cli.core.services.service_result import ServiceResult
from requests_toolbelt import MultipartEncoder  # type: ignore


class ProductService(BaseService):
    @override
    def create(self) -> ServiceResult:
        product = self.file_manager.read_data()
        data = MultipartEncoder(
            fields={
                "product": json.dumps(product.to_json()),
                "icon": ("icon.png", product.icon, "image/png"),
            }
        )
        headers = {"Content-Type": data.content_type}
        try:
            new_product_data = self.api.post(data=data, headers=headers)
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

    @override
    def export(self, resource_id: str) -> ServiceResult:
        result = self.retrieve_from_mpt(resource_id)
        product = result.model
        if not result.success or not product:
            return result

        self.file_manager.create_tab()
        self.file_manager.add(product)

        # NOTE: Product Settings don't follow the same structure as other related components.
        # They cannot be retrieved as separate resources, so special handling is required
        # to maintain simple code organization and logic.
        settings_excel_file_manager = SettingsExcelFileManager(
            self.file_manager.file_handler.file_path
        )
        settings_excel_file_manager.create_tab()

        settings_excel_file_manager.add(product.settings.items)

        return ServiceResult(success=True, model=product, stats=self.stats)

    @override
    def retrieve(self) -> ServiceResult:
        product = self.file_manager.read_data()
        if product.id is None:
            return ServiceResult(success=True, model=None, stats=self.stats)

        try:
            exists = self.api.exists({"id": product.id})
        except Exception as e:
            self._set_error(str(e))
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        return ServiceResult(success=True, model=product if exists else None, stats=self.stats)

    @override
    def retrieve_from_mpt(self, resource_id: str) -> ServiceResult:
        try:
            product_data = self.api.get(resource_id)
        except Exception as e:
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        product = self.data_model.from_json(product_data)
        return ServiceResult(success=True, model=product, stats=self.stats)

    def validate_definition(self) -> ServiceResult:
        """Validates the definition of the product file.

        Returns:
            ServiceResult: The result of the validation, including errors if any.

        """
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

    @override
    def update(self) -> ServiceResult:
        product = self.file_manager.read_data()
        settings_excel_file_manager = SettingsExcelFileManager(
            self.file_manager.file_handler.file_path
        )
        items = []
        for setting_data in settings_excel_file_manager.read_data():
            for item in setting_data.items:  # type: ignore[attr-defined]
                if item.action == DataActionEnum.UPDATE:
                    items.append(item)

        try:
            self.api.update(product.id, SettingsData(items=items).to_json())
        except MPTAPIError as e:
            self._set_error(str(e))
            return ServiceResult(success=False, errors=[str(e)], model=None, stats=self.stats)

        return ServiceResult(success=True, model=product, stats=self.stats)
