import logging
from abc import ABC
from collections.abc import Callable
from typing import override

from cli.core.errors import MPTAPIError
from cli.core.models import DataCollectionModel
from cli.core.models.data_model import BaseDataModel as DataModel
from cli.core.products.models import DataActionEnum
from cli.core.services import RelatedBaseService
from cli.core.services.service_result import ServiceResult

logger = logging.getLogger(__name__)


class RelatedComponentsBaseService(RelatedBaseService, ABC):
    """Base service for managing related component operations."""

    @override
    def create(self) -> ServiceResult:
        errors = []
        collection = {}
        for raw_model_data in self.file_manager.read_data():
            data_model = self.prepare_data_model_to_create(raw_model_data)

            try:
                new_item = self.api.post(json=data_model.to_json())
            except MPTAPIError as e:
                errors.append(str(e))
                self._set_error(str(e), data_model.id)
                continue

            old_id = data_model.id
            data_model.id = new_item["id"]
            collection[old_id] = data_model
            self._set_synced(new_item["id"], data_model.coordinate)

        return ServiceResult(
            success=len(errors) == 0,
            errors=errors,
            model=None,
            collection=DataCollectionModel(collection=collection),
            stats=self.stats,
        )

    @override
    def export(self) -> ServiceResult:
        self.file_manager.create_tab()
        params = self.export_params
        while True:
            try:
                response = self.api.list(params=params)
            except MPTAPIError as e:
                self._set_error(str(e))
                return ServiceResult(success=False, model=None, errors=[str(e)], stats=self.stats)

            self.file_manager.add([self.data_model.from_json(item) for item in response["data"]])

            meta_data = response["meta"]
            if meta_data["offset"] + meta_data["limit"] < meta_data["total"]:
                params["offset"] += params["limit"]
            else:
                break

        return ServiceResult(success=True, model=None, stats=self.stats)

    @override
    def retrieve(self) -> ServiceResult:  # pragma: no cover
        return ServiceResult(
            success=False, errors=["Retrieve not implemented"], model=None, stats=self.stats
        )

    @override
    def retrieve_from_mpt(self, resource_id: str) -> ServiceResult:  # pragma: no cover
        return ServiceResult(
            success=False,
            errors=["Retrieve from mpt not implemented"],
            model=None,
            stats=self.stats,
        )

    @override
    def update(self) -> ServiceResult:
        errors = []
        for data_model in self.file_manager.read_data():
            data_model.product_id = self.resource_id
            if data_model.to_skip:
                self._set_skipped()
                continue

            try:
                action_handler = self._get_update_action_handler(data_model.action)
            except ValueError as e:
                errors.append(str(e))
                self._set_error(str(e), data_model.id)
                continue

            try:
                action_handler(data_model)
            except MPTAPIError as e:
                errors.append(str(e))
                self._set_error(str(e), data_model.id)
                continue

            self._set_synced(data_model.id, data_model.coordinate)

        return ServiceResult(success=len(errors) == 0, errors=errors, model=None, stats=self.stats)

    def prepare_data_model_to_create(self, data_model: DataModel) -> DataModel:
        """Hook method to customize the data model before creating it.

        Subclasses can override this method to modify data or add the logic needed before
        sending to API.

        Args:
            data_model: The data model to be customized

        Returns:
             DataModel: The data model to create
        """
        return data_model

    def _action_create_item(self, data_model: DataModel):
        """Creates the item in the API.

        This method could be overridden by subclasses to customize the data model before
        sending to API.

        Args:
            data_model: The data model to be created

        """
        new_data_model = self.api.post(data_model.to_json())
        data_model.id = new_data_model["id"]  # type: ignore[attr-defined]

    def _action_delete_item(self, data_model: DataModel) -> None:
        """Delete the item in the API.

        This method could be overridden by subclasses to customize the data model before
        sending to API.

        Args:
            data_model: The data model to be deleted

        """
        logger.debug("Delete action is not supported yet")

    def _action_update_item(self, data_model: DataModel) -> None:
        """Update the item in the API.

        This method could be overridden by subclasses to customize the data model before
        sending to API.

        Args:
            data_model: The data model to be updated

        """
        self.api.update(data_model.id, data_model.to_json())  # type: ignore[attr-defined]

    def _get_update_action_handler(self, model_action: DataActionEnum) -> Callable:
        """Retrieve the appropriate action handler based onf the action type.

        This method could be overridden by subclasses to add specific actions in subclasses.

        Args:
            model_action: The action type to retrieve the handler for.

        Returns:
            Callable: The action handler for the given action type.

        Raises:
            ValueError: If the action type is not supported.

        """
        if model_action == DataActionEnum.CREATE:
            return self._action_create_item

        if model_action == DataActionEnum.DELETE:
            # TODO: uncomment once the delete action is supported
            # return self._action_delete_item
            raise ValueError(f"Action type {model_action} is not supported")

        if model_action == DataActionEnum.UPDATE:
            return self._action_update_item

        raise ValueError(f"Invalid action: {model_action}")
