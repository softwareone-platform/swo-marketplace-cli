from dataclasses import dataclass

from cli.core.products.models import DataActionEnum, ItemActionEnum


@dataclass(kw_only=True)
class ActionMixin:
    """Mixin class providing action-related functionality for data models."""

    action: DataActionEnum = DataActionEnum.SKIP

    @property
    def to_create(self) -> bool:
        """Check if the object is marked for creation.

        Returns:
            True if the object should be created, False otherwise.
        """
        return self.action == DataActionEnum.CREATE

    @property
    def to_update(self) -> bool:
        """Check if the object is marked for update.

        Returns:
            True if the object should be updated, False otherwise.
        """
        return self.action == DataActionEnum.UPDATE

    @property
    def to_delete(self) -> bool:
        """Check if the object is marked for deletion.

        Returns:
            True if the object should be deleted, False otherwise.
        """
        return self.action == DataActionEnum.DELETE

    @property
    def to_skip(self) -> bool:
        """Check if the object should be skipped.

        Returns:
            True if the object should be skipped, False otherwise.
        """
        return self.action in (DataActionEnum.SKIP, DataActionEnum.SKIPPED)


@dataclass
class ItemActionMixin(ActionMixin):
    """Mixin class providing item-specific action functionality."""

    @property
    def to_review(self) -> bool:
        """Check if the object is marked for review.

        Returns:
            True if the object should be reviewed, False otherwise.
        """
        return self.action == ItemActionEnum.REVIEW

    @property
    def to_publish(self) -> bool:
        """Check if the object is marked for publication.

        Returns:
            True if the object should be published, False otherwise.
        """
        return self.action == ItemActionEnum.PUBLISH

    @property
    def to_unpublish(self) -> bool:
        """Check if the object is marked for unpublication.

        Returns:
            True if the object should be unpublished, False otherwise.
        """
        return self.action == ItemActionEnum.UNPUBLISH
