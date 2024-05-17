import shutil
from pathlib import Path

import pytest
import responses
from swo.mpt.cli.core.accounts.models import Account as CLIAccount
from swo.mpt.cli.core.mpt.client import MPTClient
from swo.mpt.cli.core.mpt.models import (
    Account,
    Item,
    ItemGroup,
    Parameter,
    ParameterGroup,
    Pricelist,
    PricelistItem,
    Product,
    Template,
    Uom,
)


@pytest.fixture()
def requests_mocker():
    """
    Allow mocking of http calls made with requests.
    """
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture()
def base_url():
    return "https://example.com"


@pytest.fixture()
def mpt_client(base_url):
    return MPTClient(base_url, "token")


@pytest.fixture()
def wrap_to_mpt_list_response():
    def _wrap_to_list(list_response):
        return {
            "data": list_response,
            "$meta": {
                "pagination": {
                    "limit": 10,
                    "offset": 0,
                    "total": 2,
                },
            },
        }

    return _wrap_to_list


@pytest.fixture()
def mpt_token():
    return {
        "id": "TKN-0000-0000-0001",
        "name": "Adobe Token",
        "token": "TKN-1234",
        "account": {
            "id": "ACC-4321",
            "name": "Adobe",
            "type": "Vendor",
        },
    }


@pytest.fixture()
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


@pytest.fixture()
def mpt_product():
    return {
        "id": "PRD-1234-1234",
        "name": "Adobe for Commercial",
        "status": "Published",
        "vendor": {
            "id": "ACC-4321",
            "name": "Adobe",
            "type": "Vendor",
        },
    }


@pytest.fixture()
def mpt_parameter_group():
    return {
        "id": "PRG-1234-1234",
        "name": "Parameter Group 1",
    }


@pytest.fixture()
def mpt_item_group():
    return {
        "id": "ITG-1234-1234",
        "name": "Item Group 1",
    }


@pytest.fixture()
def mpt_parameter():
    return {
        "id": "PAR-1234-1234-0001",
        "name": "Parameter",
        "externalId": "external-id-1",
    }


@pytest.fixture()
def mpt_item():
    return {
        "id": "ITM-1234-1234-0001",
        "name": "Item 1",
    }


@pytest.fixture()
def mpt_uom():
    return {
        "id": "UM-1234-1234",
        "name": "User",
    }


@pytest.fixture()
def mpt_template():
    return {
        "id": "TPL-1234-1234",
        "name": "Template 1",
    }


@pytest.fixture()
def mpt_pricelist():
    return {
        "id": "PRC-1234-1234",
    }


@pytest.fixture()
def mpt_pricelist_item(mpt_item):
    return {
        "id": "PRI-1234-1234",
        "item": mpt_item,
    }


@pytest.fixture()
def product():
    return Product(
        id="PRD-1234-1234",
        name="Adobe for Commercial",
        status="Draft",
        vendor=Account(id="ACC-4321", name="Adobe", type="Vendor"),
    )


@pytest.fixture()
def parameter_group():
    return ParameterGroup(id="PRG-1234-1234", name="Parameter Group")


@pytest.fixture()
def item_group():
    return ItemGroup(id="ITG-1234-1234", name="Item Group")


@pytest.fixture()
def parameter():
    return Parameter(id="PAR-1234-1234-0001", name="Parameter", externalId="external_1")


@pytest.fixture()
def another_parameter():
    return Parameter(id="PAR-1234-1234-0002", name="Parameter", externalId="external_2")


@pytest.fixture()
def item():
    return Item(id="ITM-1234-1234-0001", name="Item 1")


@pytest.fixture()
def uom():
    return Uom(id="UOM-1234-1234", name="User")


@pytest.fixture()
def template():
    return Template(id="TPL-0000-0000-0001", name="Template")


@pytest.fixture()
def pricelist():
    return Pricelist(id="PRC-1234-1234")


@pytest.fixture()
def pricelist_item(item):
    return PricelistItem(id="PRI-1234-1234", item=item)


@pytest.fixture()
def product_icon_path():
    return Path("swo/mpt/cli/core/icons/fake-icon.png")


@pytest.fixture()
def mpt_products_response(wrap_to_mpt_list_response, mpt_products):
    return wrap_to_mpt_list_response(mpt_products)


@pytest.fixture()
def mpt_uoms_response(wrap_to_mpt_list_response, mpt_uom):
    return wrap_to_mpt_list_response([mpt_uom])


@pytest.fixture()
def accounts_path():
    return Path("tests/accounts_config/home/.swocli/accounts.json")


@pytest.fixture()
def new_accounts_path(tmp_path, accounts_path):
    shutil.copyfile(accounts_path, tmp_path / "accounts.json")
    return tmp_path / "accounts.json"


@pytest.fixture()
def expected_account():
    return CLIAccount(
        id="ACC-12341",
        name="Account 1",
        type="Vendor",
        token="TKN-0000-0000-0001:secret 1",
        environment="https://example.com",
        is_active=True,
    )


@pytest.fixture()
def another_expected_account():
    return CLIAccount(
        id="ACC-12342",
        name="Account 2",
        type="Vendor",
        token="TKN-0000-0000-0002:secret 2",
        environment="https://example.com",
        is_active=False,
    )


@pytest.fixture()
def active_vendor_account():
    return CLIAccount(
        id="ACC-12341",
        name="Account 1",
        type="Vendor",
        token="TKN-0000-0000-0001:secret 1",
        environment="https://example.com",
        is_active=True,
    )


@pytest.fixture()
def active_operations_account():
    return CLIAccount(
        id="ACC-12341",
        name="Account 1",
        type="Operations",
        token="TKN-0000-0000-0001:secret 1",
        environment="https://example.com",
        is_active=True,
    )


@pytest.fixture()
def product_file_root():
    return Path("tests/product_files")


@pytest.fixture()
def empty_file(product_file_root):
    return product_file_root / "PRD-0000-0000-empty.xlsx"


@pytest.fixture()
def product_file(product_file_root):
    return product_file_root / "PRD-1234-1234-1234-file.xlsx"


@pytest.fixture()
def update_product_file(product_file_root):
    return product_file_root / "PRD-1234-1234-1234-file-update.xlsx"


@pytest.fixture()
def new_product_file(tmp_path, product_file):
    shutil.copyfile(product_file, tmp_path / "PRD-1234-1234-1234-copied.xlsx")
    return tmp_path / "PRD-1234-1234-1234-copied.xlsx"


@pytest.fixture()
def extra_column_product_file(tmp_path, product_file_root):
    shutil.copyfile(
        product_file_root / "PRD-1234-1234-1234-file-extra-column.xlsx",
        tmp_path / "PRD-1234-1234-1234-file-extra-column.xlsx",
    )
    return tmp_path / "PRD-1234-1234-1234-file-extra-column.xlsx"


@pytest.fixture()
def new_update_product_file(tmp_path, update_product_file):
    shutil.copyfile(
        update_product_file, tmp_path / "PRD-1234-1234-1234-file-update-copied.xlsx"
    )
    return tmp_path / "PRD-1234-1234-1234-file-update-copied.xlsx"


@pytest.fixture()
def mock_sync_product(
    mocker,
    parameter_group,
    item_group,
    parameter,
    another_parameter,
    item,
    uom,
    template,
    product,
):
    mocker.patch(
        "swo.mpt.cli.core.products.flows.create_parameter_group",
        return_value=parameter_group,
    )
    mocker.patch(
        "swo.mpt.cli.core.products.flows.create_item_group", return_value=item_group
    )
    mocker.patch(
        "swo.mpt.cli.core.products.flows.create_parameter",
        side_effect=[
            parameter,
            another_parameter,
            parameter,
            another_parameter,
            parameter,
            another_parameter,
            parameter,
            another_parameter,
        ],
    )
    mocker.patch("swo.mpt.cli.core.products.flows.create_item", return_value=item)
    mocker.patch("swo.mpt.cli.core.products.flows.search_uom_by_name", return_value=uom)
    mocker.patch(
        "swo.mpt.cli.core.products.flows.create_template", return_value=template
    )
    mocker.patch("swo.mpt.cli.core.products.flows.create_product", return_value=product)


@pytest.fixture()
def pricelist_file_root():
    return Path("tests/pricelist_files")


@pytest.fixture()
def pricelist_file_path(pricelist_file_root):
    return pricelist_file_root / "PRC-1234-1234-1234.xlsx"


@pytest.fixture()
def pricelist_new_file(tmp_path, pricelist_file_path):
    shutil.copyfile(pricelist_file_path, tmp_path / "PRC-1234-1234-1234-copied.xlsx")
    return tmp_path / "PRC-1234-1234-1234-copied.xlsx"
