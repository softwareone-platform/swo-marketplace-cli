from cli.core.accounts.models import Account

NEW_TOKEN_MASK_PREFIX_LENGTH = 22
TOKEN_MASK_PREFIX_LENGTH = 4


def wrap_account_type(account_type: str) -> str:
    """Apply rich color formatting for account type."""
    match account_type:
        case "Vendor":
            return f"[cyan]{account_type}"
        case "Operations":
            return f"[white]{account_type}"
        case "Client":
            return f"[magenta]{account_type}"
        case _:
            return account_type


def wrap_active(*, is_active: bool) -> str:
    """Return a marker for active accounts."""
    return "[red bold]\u2714" if is_active else ""


def wrap_token(account: Account, *, to_wrap_secret: bool) -> str:
    """Format token display with optional masking."""
    is_new_token = "idt:TKN-" in account.token
    token = account.token if is_new_token else f"{account.token_id}:{account.token}"

    if to_wrap_secret:
        visible_token_prefix = token[:TOKEN_MASK_PREFIX_LENGTH]
        if is_new_token:
            token = f"{token[:NEW_TOKEN_MASK_PREFIX_LENGTH]}*****{visible_token_prefix}"
        else:
            token = f"{token[:TOKEN_MASK_PREFIX_LENGTH]}*****{visible_token_prefix}"

    return token
