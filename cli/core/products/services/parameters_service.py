from typing import Any

from cli.core.models import DataCollectionModel
from cli.core.products.services.related_components_base_service import (
    RelatedComponentsBaseService,
)


class ParametersService(RelatedComponentsBaseService):
    def set_new_parameter_group(self, parameter_groups: DataCollectionModel | None) -> None:
        """
        Update parameter group references in parameter content.

        Args:
            parameter_groups: A collection of parameter groups to update.

        """
        if parameter_groups is None or not parameter_groups.collection:
            return

        new_ids = {}
        for data_model in self.file_manager.read_data():
            try:
                new_group = parameter_groups.retrieve_by_id(data_model.group_id)
            except KeyError:
                continue

            new_ids[data_model.group_id_coordinate] = new_group.id

        if new_ids:
            self.file_manager.write_ids(new_ids)

        return

    def set_export_params(self) -> dict[str, Any]:
        params = super().set_export_params()
        params.update({"scope": self.data_model.scope})
        return params
