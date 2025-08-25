from cli.core.models import DataCollectionModel
from cli.core.products.services.related_components_base_service import (
    RelatedComponentsBaseService,
)


class TemplateService(RelatedComponentsBaseService):
    """Service for managing template-related operations."""

    def set_new_parameter_group(self, param_groups: DataCollectionModel | None) -> None:
        """
        Update parameter group references in template content.

        Args:
            param_groups: A collection of parameter groups to update.

        """
        if param_groups is None or not param_groups.collection:
            return

        new_ids = {}
        for data_model in self.file_manager.read_data():
            content = data_model.content

            for item_id, item in param_groups.collection.items():
                if item_id not in content:
                    continue

                content = content.replace(item_id, item.id)
                new_ids[data_model.content_coordinate] = content

        if new_ids:
            self.file_manager.write_ids(new_ids)
