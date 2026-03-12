from collections.abc import Callable
from functools import partial, update_wrapper
from http import HTTPStatus
from typing import Any, ParamSpec, TypeVar

from mpt_api_client.exceptions import MPTHttpError as APIException
from requests import RequestException, Response

ErrorFactory = Callable[[str, str], Exception]
CallableParams = ParamSpec("CallableParams")
RetType = TypeVar("RetType")


def _parse_bad_request_message(response: Response) -> str:
    try:
        response_body = response.json()
    except ValueError:
        return response.text

    response_errors = response_body.get("errors", {}) if isinstance(response_body, dict) else {}
    if not isinstance(response_errors, dict) or not response_errors:
        return response.text

    return "\n".join(
        (
            f"{field}: {error_details[0]}"
            if isinstance(error_details, (list, tuple)) and error_details
            else f"{field}: {error_details}"
        )
        for field, error_details in response_errors.items()
    )


class HttpErrorWrapper[**CallableParams, RetType]:
    """Wrap callables and normalize RequestException to domain error."""

    def __init__(
        self,
        func: Callable[CallableParams, RetType],
        error_factory: ErrorFactory,
    ):
        self._func = func
        self._error_factory = error_factory
        update_wrapper(self, func)

    def __call__(
        self,
        *args: CallableParams.args,
        **kwargs: CallableParams.kwargs,
    ) -> RetType:
        """Execute wrapped callable and map RequestException to domain error."""
        try:
            return self._func(*args, **kwargs)
        except RequestException as error:
            if error.response is None:
                msg = "No response"
                raise self._error_factory(str(error), msg) from error

            if error.response.status_code != HTTPStatus.BAD_REQUEST:
                msg = error.response.text
                raise self._error_factory(str(error), msg) from error

            msg = _parse_bad_request_message(error.response)
            raise self._error_factory(str(error), msg) from error

    def __get__(self, instance: Any, owner: type[Any] | None = None) -> Any:
        if instance is None:
            return self

        return partial(self.__call__, instance)


class ApiErrorWrapper[**CallableParams, RetType]:
    """Wrap callables and normalize APIException to domain error."""

    def __init__(
        self,
        func: Callable[CallableParams, RetType],
        error_factory: ErrorFactory,
    ):
        self._func = func
        self._error_factory = error_factory
        update_wrapper(self, func)

    def __call__(
        self,
        *args: CallableParams.args,
        **kwargs: CallableParams.kwargs,
    ) -> RetType:
        """Execute wrapped callable and map APIException to domain error."""
        try:
            return self._func(*args, **kwargs)
        except APIException as error:
            raise self._error_factory(str(error), error.body) from error

    def __get__(self, instance: Any, owner: type[Any] | None = None) -> Any:
        if instance is None:
            return self

        return partial(self.__call__, instance)
