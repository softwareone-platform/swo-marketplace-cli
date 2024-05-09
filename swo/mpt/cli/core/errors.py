from functools import wraps
from pathlib import Path
from typing import Callable, ParamSpec, TypeVar

from requests import RequestException

Param = ParamSpec("Param")
RetType = TypeVar("RetType")


class CLIError(Exception):
    pass


class MPTAPIError(CLIError):
    def __init__(self, error_message: str, response_body: str):
        self._response_body = response_body
        self._msg = error_message

    def __str__(self) -> str:
        return f"{self._msg} with response body {self._response_body}"


def wrap_http_error(func: Callable[Param, RetType]) -> Callable[Param, RetType]:
    @wraps(func)
    def _wrapper(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
        try:
            return func(*args, **kwargs)
        except RequestException as e:
            response = (
                str(e.response.content) if e.response is not None else "Empty response"
            )
            raise MPTAPIError(response, str(e))

    return _wrapper


class AccountNotFoundError(CLIError):
    def __init__(self, account_id: str):
        self._account_id = account_id

    def __str__(self) -> str:
        return f"Account {self._account_id} is not found. Add account first."


class NoActiveAccountFoundError(CLIError):
    def __str__(self) -> str:
        return (
            "No active account found. Activate any account first using "
            "'swocli accounts active ACCOUNT-ID' command"
        )


class FileNotExistsError(CLIError):
    def __init__(self, file_path: Path):
        self._path = file_path

    def __str__(self) -> str:
        return f"Provided file path doesn't exist: {self._path}"
