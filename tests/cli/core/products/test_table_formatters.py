import pytest
from cli.core.mpt.models import Account as MPTAccount
from cli.core.products.table_formatters import wrap_product_status, wrap_vendor


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ("Draft", "[white]Draft"),
        ("Pending", "[blue]Pending"),
        ("Published", "[green bold]Published"),
        ("Unpublished", "[red]Unpublished"),
        ("Unknown", "Unknown"),
    ],
)
def test_wrap_product_status(status, expected):
    result = wrap_product_status(status)

    assert result == expected


def test_wrap_vendor():
    vendor = MPTAccount(id="ACC-0001", name="Vendor Name", type="Vendor")

    result = wrap_vendor(vendor)

    assert result == "ACC-0001 (Vendor Name)"
