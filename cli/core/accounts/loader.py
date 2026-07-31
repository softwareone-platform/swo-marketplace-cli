"""Read-only loading of the accounts stored by the marketplace CLI.

Unlike ``get_or_create_accounts``, the accounts file is never created when missing, so
authentication providers can fail with a clear error instead of an empty file.
"""

import json
from pathlib import Path

from cli.core.accounts.flows import find_account, find_active_account
from cli.core.accounts.handlers import JsonFileHandler
from cli.core.accounts.models import Account
from cli.core.errors import CLIAccountError
from pydantic import ValidationError


def load_account(file_path: Path | str | None = None, account_id: str | None = None) -> Account:
    """Read the accounts file and select the requested account.

    Args:
        file_path: Accounts file to read. Defaults to ``~/.swocli/accounts.json``.
        account_id: When set, select this account; otherwise select the active one.

    Returns:
        The selected account.

    Raises:
        CLIAccountError: If the accounts file is missing or invalid.
        AccountNotFoundError: If ``account_id`` does not match any account.
        NoActiveAccountFoundError: If no account is active.
    """
    json_file_handler = JsonFileHandler(Path(file_path)) if file_path else JsonFileHandler()
    raw_accounts = _read_raw_accounts(json_file_handler)
    accounts = _validate_accounts(raw_accounts, json_file_handler.file_path)
    if account_id is not None:
        return find_account(accounts, account_id)
    return find_active_account(accounts)


def _read_raw_accounts(json_file_handler: JsonFileHandler) -> list[dict[str, object]]:
    """Read the raw account entries stored in the accounts file.

    Args:
        json_file_handler: Handler for the accounts file to read.

    Returns:
        The raw account entries.

    Raises:
        CLIAccountError: If the file is missing, is not valid JSON, or is not a JSON list.
    """
    path = json_file_handler.file_path
    if not json_file_handler.exists():
        raise CLIAccountError(
            f"CLI accounts file not found at {path}. "
            "Log in first using 'mpt-cli accounts add TOKEN' command"
        )
    try:
        raw_accounts = json_file_handler.read()
    except json.JSONDecodeError as decode_error:
        raise CLIAccountError(
            f"CLI accounts file {path} is not valid JSON: {decode_error}."
        ) from decode_error
    if not isinstance(raw_accounts, list):
        raise CLIAccountError(f"CLI accounts file {path} must contain a JSON list of accounts.")
    return raw_accounts


def _validate_accounts(raw_accounts: list[dict[str, object]], path: Path) -> list[Account]:
    """Validate raw account entries into account models.

    Args:
        raw_accounts: Raw account entries read from the accounts file.
        path: Accounts file the entries were read from, used in error messages.

    Returns:
        The validated accounts.

    Raises:
        CLIAccountError: If an entry is not a valid account.
    """
    try:
        return [Account.model_validate(raw_account) for raw_account in raw_accounts]
    except ValidationError as validation_error:
        error_details = _format_validation_error(validation_error)
        raise CLIAccountError(
            f"CLI accounts file {path} contains an invalid account: {error_details}."
        ) from validation_error


def _format_validation_error(validation_error: ValidationError) -> str:
    """Summarize a validation error without echoing the invalid input.

    The raw error string includes the offending payload, which may contain account
    tokens, so only the field locations and messages are kept.

    Args:
        validation_error: Validation error raised for an account entry.

    Returns:
        The field locations and messages of the validation issues.
    """
    issues = validation_error.errors(include_input=False, include_url=False)
    return "; ".join(
        "{field}: {message}".format(
            field=".".join(str(location) for location in issue["loc"]),
            message=issue["msg"],
        )
        for issue in issues
    )
