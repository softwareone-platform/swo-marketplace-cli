from cli.core.accounts.models import Account
from cli.core.accounts.table_formatters import wrap_account_type, wrap_active, wrap_token
from rich import box
from rich.table import Table


class AccountsTableRenderer:
    """Render account collections as rich tables."""

    def render(self, title: str, accounts: list[Account], *, wrap_secret: bool = True) -> Table:
        """Build the accounts table for console output."""
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("ID", no_wrap=True)
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Token", no_wrap=True)
        table.add_column("Environment", no_wrap=True)
        table.add_column("Active", justify="center")

        for account in accounts:
            table.add_row(
                account.id,
                account.name,
                wrap_account_type(account.type),
                wrap_token(account, to_wrap_secret=wrap_secret),
                account.environment,
                wrap_active(is_active=account.is_active),
            )

        return table
