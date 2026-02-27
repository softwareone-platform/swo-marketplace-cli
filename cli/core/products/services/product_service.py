from typing import override

from cli.core.handlers.errors import RequiredFieldsError, RequiredSheetsError
from cli.core.mpt.api_client import create_api_mpt_client_from_account
from cli.core.products.handlers import SettingsExcelFileManager
from cli.core.products.models import DataActionEnum, SettingsData
from cli.core.services.base_service import BaseService
from cli.core.services.service_result import ServiceResult
from mpt_api_client import RQLQuery
from mpt_api_client.exceptions import MPTAPIError, MPTHttpError


class ProductService(BaseService):
    """Service for managing product operations."""

    @override
    def create(self) -> ServiceResult:
        mpt_client = create_api_mpt_client_from_account(self.account)

        product = self.file_manager.read_data()

        product_request_data = product.to_json()
        product_icon_file = ("icon.png", product.icon, "image/png")

        try:
            new_product_data = mpt_client.catalog.products.create(
                product_request_data, file=product_icon_file
            )
        except (MPTAPIError, MPTHttpError) as error:
            msg = f"Product '{product.id}' creation failed: {error}"
            self._set_error(msg)
            return ServiceResult(success=False, errors=[msg], model=product, stats=self.stats)

        product.id = new_product_data.id

        try:
            product_settings_request_data = product.settings.to_json()

            mpt_client.catalog.products.update_settings(product.id, product_settings_request_data)
        except (MPTAPIError, MPTHttpError) as error:
            self._set_error(str(error))
            return ServiceResult(success=False, errors=[str(error)], model=None, stats=self.stats)

        self._set_synced(product.id, product.coordinate)
        return ServiceResult(success=True, model=product, stats=self.stats)

    @override
    def export(self, resource_id: str) -> ServiceResult:
        mpt_client = create_api_mpt_client_from_account(self.account)

        try:
            product_data = mpt_client.catalog.products.get(resource_id)
        except (MPTAPIError, MPTHttpError) as error:
            self._set_error(str(error))
            return ServiceResult(success=False, errors=[str(error)], model=None, stats=self.stats)

        product = self.data_model.from_json(product_data)

        self.file_manager.create_tab()
        self.file_manager.add(product)

        # NOTE: Product Settings don't follow the same structure as other related components.
        # They cannot be retrieved as separate resources, so special handling is required
        # to maintain simple code organization and logic.
        settings_excel_file_manager = SettingsExcelFileManager(
            self.file_manager.file_handler.file_path
        )
        settings_excel_file_manager.create_tab()

        settings_excel_file_manager.add(product.settings.records)

        return ServiceResult(success=True, model=product, stats=self.stats)

    @override
    def retrieve(self) -> ServiceResult:
        mpt_client = create_api_mpt_client_from_account(self.account)

        product = self.file_manager.read_data()

        if product.id is None:
            return ServiceResult(success=True, model=None, stats=self.stats)

        try:
            limit = 0

            id_query = RQLQuery(id=product.id)

            products_pagination = mpt_client.catalog.products.filter(id_query).fetch_page(
                limit=limit
            )

            products_pagination_total = products_pagination.meta.pagination.total

            exists = products_pagination_total > 0
        except (MPTAPIError, MPTHttpError) as error:
            self._set_error(str(error))
            return ServiceResult(success=False, errors=[str(error)], model=None, stats=self.stats)

        return ServiceResult(success=True, model=product if exists else None, stats=self.stats)

    @override
    def retrieve_from_mpt(self, resource_id: str) -> ServiceResult:
        mpt_client = create_api_mpt_client_from_account(self.account)

        try:
            product = mpt_client.catalog.products.get(resource_id)
        except (MPTAPIError, MPTHttpError) as error:
            self._set_error(str(error))
            return ServiceResult(success=False, errors=[str(error)], model=None, stats=self.stats)

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
        mpt_client = create_api_mpt_client_from_account(self.account)

        product = self.file_manager.read_data()

        settings_excel_file_manager = SettingsExcelFileManager(
            self.file_manager.file_handler.file_path
        )

        setting_items = [
            settings_item
            for setting_data in settings_excel_file_manager.read_data()
            for settings_item in setting_data.records  # type: ignore[attr-defined]
            if settings_item.action == DataActionEnum.UPDATE
        ]

        try:
            settings_request_data = SettingsData(records=setting_items).to_json()

            mpt_client.catalog.products.update_settings(product.id, settings_request_data)
        except (MPTAPIError, MPTHttpError) as error:
            self._set_error(str(error))
            return ServiceResult(success=False, errors=[str(error)], model=None, stats=self.stats)

        return ServiceResult(success=True, model=product, stats=self.stats)
