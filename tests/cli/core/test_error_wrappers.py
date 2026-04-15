from types import SimpleNamespace

import pytest
from cli.core.error_wrappers import ApiErrorWrapper, HttpErrorWrapper
from mpt_api_client.exceptions import MPTHttpError


def _build_runtime_error(request_msg, response_body):
    return RuntimeError(f"{request_msg}|{response_body}")


@pytest.fixture
def error_factory():
    return _build_runtime_error


@pytest.fixture
def http_error_callable(mocker):
    return mocker.Mock(side_effect=MPTHttpError(500, "err", "boom"))


def test_http_wrapper_get_from_class(error_factory):
    wrapper = HttpErrorWrapper(lambda *_args, **_kwargs: None, error_factory)

    result = wrapper.__get__(None, object)

    assert result is wrapper


def test_api_wrapper_get_from_class(error_factory):
    wrapper = ApiErrorWrapper(lambda *_args, **_kwargs: None, error_factory)

    result = wrapper.__get__(None, object)

    assert result is wrapper


def test_api_wrapper_get_from_instance(error_factory):
    wrapper = ApiErrorWrapper(lambda context: context.payload, error_factory)
    context = SimpleNamespace(payload="bound")

    result = wrapper.__get__(context, None)

    assert result() == "bound"


def test_api_wrapper_raises_factory_error(error_factory, http_error_callable):
    wrapper = ApiErrorWrapper(
        http_error_callable,
        error_factory,
    )

    with pytest.raises(RuntimeError, match="boom"):
        wrapper()
