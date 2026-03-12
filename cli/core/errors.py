from collections.abc import Callable
from typing import ParamSpec, TypeVar, cast

from cli.core.error_wrappers import ApiErrorWrapper, HttpErrorWrapper

CallableParams = ParamSpec("CallableParams")
RetType = TypeVar("RetType")


class CLIError(Exception):
    """Base exception class for CLI-related errors."""


class MPTAPIError(CLIError):
    """Exception raised when MPT API operations fail."""

    def __init__(self, request_msg: str, response_body: str):
        self._response_body = response_body
        self._request_msg = request_msg

    def __str__(self) -> str:
        return f"{self._request_msg} with response body {self._response_body}"


def wrap_http_error[**CallableParams, RetType](
    func: Callable[CallableParams, RetType],
) -> Callable[CallableParams, RetType]:
    """Decorator to wrap HTTP request functions and handle RequestException.

    Args:
        func: The function to be wrapped, which may raise a RequestException.

    Returns:
        The wrapped function that raises MPTAPIError on HTTP errors.

    """
    return cast(Callable[CallableParams, RetType], HttpErrorWrapper(func, MPTAPIError))


def wrap_mpt_api_error[**CallableParams, RetType](
    func: Callable[CallableParams, RetType],
) -> Callable[CallableParams, RetType]:
    """Decorator to wrap MPT API functions and handle APIException."""
    return cast(Callable[CallableParams, RetType], ApiErrorWrapper(func, MPTAPIError))


class AccountNotFoundError(CLIError):
    """Exception raised when a specified account cannot be found."""

    def __init__(self, account_id: str):
        self._account_id = account_id

    def __str__(self) -> str:
        return f"Account {self._account_id} is not found. Add account first."


class NoActiveAccountFoundError(CLIError):
    """Exception raised when no active account is configured."""

    def __str__(self) -> str:
        return (
            "No active account found. Activate any account first using "
            "'mpt-cli accounts activate ACCOUNT-ID' command"
        )
