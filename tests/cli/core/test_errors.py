import pytest
from cli.core.errors import MPTAPIError, wrap_http_error
from requests import RequestException, Response


def _raise_connection_error() -> None:
    raise RequestException("Connection error")


def _raise_bad_request(response: Response) -> None:
    raise RequestException("Bad Request", response=response)


def test_wrap_http_error_no_response():
    wrapped = wrap_http_error(_raise_connection_error)

    with pytest.raises(MPTAPIError) as error:
        wrapped()

    assert "No response" in str(error.value)


def test_wrap_http_error_bad_request_fields(mocker):
    response = mocker.Mock(spec=Response)
    response.status_code = 400
    response.json.return_value = {"errors": {"name": ["is required"]}}
    wrapped = wrap_http_error(lambda: _raise_bad_request(response))

    with pytest.raises(MPTAPIError) as error:
        wrapped()

    assert "name: is required" in str(error.value)


def test_wrap_http_error_bad_request_no_fields(mocker):
    response = mocker.Mock(spec=Response)
    response.status_code = 400
    response.json.return_value = {"message": "Invalid payload"}
    response.content = b"invalid payload content"
    wrapped = wrap_http_error(lambda: _raise_bad_request(response))

    with pytest.raises(MPTAPIError) as error:
        wrapped()

    assert "invalid payload content" in str(error.value)
