from cli.core.mpt.models import Account as MPTAccount


def wrap_product_status(status: str) -> str:
    """Apply rich color formatting for product status."""
    match status:
        case "Draft":
            return f"[white]{status}"
        case "Pending":
            return f"[blue]{status}"
        case "Published":
            return f"[green bold]{status}"
        case "Unpublished":
            return f"[red]{status}"
        case _:
            return status


def wrap_vendor(vendor: MPTAccount) -> str:
    """Format vendor account details for table output."""
    return f"{vendor.id} ({vendor.name})"
