import pytest
from mpt_api_client.models import Collection
from mpt_api_client.models.meta import Pagination


@pytest.fixture
def mpt_products():
    return [
        {
            "id": "PRD-1234-1234",
            "name": "Adobe for Commercial",
            "status": "Published",
            "vendor": {
                "id": "ACC-4321",
                "name": "Adobe",
                "type": "Vendor",
            },
        },
        {
            "id": "PRD-4321-4321",
            "name": "Azure CSP Commercial",
            "status": "Draft",
            "vendor": {
                "id": "ACC-1234",
                "name": "Microsoft",
                "type": "Vendor",
            },
        },
    ]


@pytest.fixture
def wrap_to_mpt_page(mocker):
    def wrapper(page_response):
        mock_page = mocker.MagicMock(spec=Collection())
        mock_page.meta.pagination = Pagination(limit=10, offset=0, total=len(page_response))
        mock_page.to_list.return_value = page_response
        return mock_page

    return wrapper


@pytest.fixture
def mpt_products_page(wrap_to_mpt_page, mpt_products):
    return wrap_to_mpt_page(mpt_products)


@pytest.fixture
def wrap_to_mpt_list_response():
    def wrapper(list_response):
        return {
            "data": list_response,
            "$meta": {
                "pagination": {
                    "limit": 10,
                    "offset": 0,
                    "total": len(list_response),
                },
            },
        }

    return wrapper


@pytest.fixture
def mpt_uom():
    return {
        "id": "UM-1234-1234",
        "name": "User",
    }


@pytest.fixture
def mpt_uoms_response(wrap_to_mpt_list_response, mpt_uom):
    return wrap_to_mpt_list_response([mpt_uom])


@pytest.fixture
def mpt_uoms_page(wrap_to_mpt_page, mpt_uom):
    return wrap_to_mpt_page([mpt_uom])
