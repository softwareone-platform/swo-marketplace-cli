import pytest
from cli.core.price_lists.models import ItemData


@pytest.fixture
def item_data_from_json(mpt_item_data):
    return ItemData.from_json(mpt_item_data)
