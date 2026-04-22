from cli.core.mpt.models import Product as MPTProduct
from cli.core.products.table_formatters import wrap_product_status, wrap_vendor
from rich import box
from rich.table import Table


class ProductsTableRenderer:
    """Render product collections as rich tables."""

    def render(self, title: str, products: list[MPTProduct]) -> Table:
        """Build the products table for console output."""
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("ID")
        table.add_column("Name", no_wrap=True)
        table.add_column("Status")
        table.add_column("Vendor", no_wrap=True)

        for product in products:
            table.add_row(
                product.id,
                product.name,
                wrap_product_status(product.status),
                wrap_vendor(product.vendor),
            )

        return table
