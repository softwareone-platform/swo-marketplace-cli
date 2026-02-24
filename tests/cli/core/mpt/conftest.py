import pytest


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
def mpt_uom():
    return {
        "id": "UM-1234-1234",
        "name": "User",
    }


@pytest.fixture
def mpt_uoms_response(wrap_to_mpt_list_response, mpt_uom):
    return wrap_to_mpt_list_response([mpt_uom])
