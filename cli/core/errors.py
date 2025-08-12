from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from requests import RequestException

Param = ParamSpec("Param")
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


def wrap_http_error(func: Callable[Param, RetType]) -> Callable[Param, RetType]:
    """Decorator to wrap HTTP request functions and handle RequestException.

    Args:
        func: The function to be wrapped, which may raise a RequestException.

    Returns:
        The wrapped function that raises MPTAPIError on HTTP errors.

    """

    @wraps(func)
    def _wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
        try:
            return func(*args, **kwargs)
        except RequestException as e:
            if e.response is None:
                msg = "No response"
            elif e.response.status_code == 400:
                response_body = e.response.json()

                msg = ""
                if "errors" in response_body:
                    for field, error in response_body["errors"].items():
                        msg += f"{field}: {error[0]}\n"
                else:
                    msg = str(e.response.content)
            else:
                msg = str(e.response.content)

            raise MPTAPIError(str(e), msg)

    return _wrapper


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
