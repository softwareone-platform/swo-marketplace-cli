import pytest
from cli.core.errors import MPTAPIError, wrap_http_error
from requests import RequestException, Response


def test_wrap_http_error_no_response(mocker):
    wrapped = wrap_http_error(mocker.Mock(side_effect=RequestException("Connection error")))

    with pytest.raises(MPTAPIError) as error:
        wrapped()

    assert "No response" in str(error.value)


def test_wrap_http_error_non_bad_request(mocker):
    response = mocker.Mock(spec=Response)
    response.status_code = 500
    response.content = b"server error"
    response.text = "server error"
    wrapped = wrap_http_error(
        mocker.Mock(side_effect=RequestException("Bad Request", response=response))
    )

    with pytest.raises(MPTAPIError) as error:
        wrapped()

    assert "server error" in str(error.value)


def test_wrap_http_error_bad_request_fields(mocker):
    response = mocker.Mock(spec=Response)
    response.status_code = 400
    response.json.return_value = {"errors": {"name": ["is required"]}}
    wrapped = wrap_http_error(
        mocker.Mock(side_effect=RequestException("Bad Request", response=response))
    )

    with pytest.raises(MPTAPIError) as error:
        wrapped()

    assert "name: is required" in str(error.value)


def test_wrap_http_error_bad_request_no_fields(mocker):
    response = mocker.Mock(spec=Response)
    response.status_code = 400
    response.json.return_value = {"message": "Invalid payload"}
    response.content = b"invalid payload content"
    response.text = "invalid payload content"
    wrapped = wrap_http_error(
        mocker.Mock(side_effect=RequestException("Bad Request", response=response))
    )

    with pytest.raises(MPTAPIError) as error:
        wrapped()

    assert "invalid payload content" in str(error.value)


def test_wrap_http_error_bad_request_invalid_json(mocker):
    response = mocker.Mock(spec=Response)
    response.status_code = 400
    response.json.side_effect = ValueError("invalid json")
    response.content = b"invalid response content"
    response.text = "invalid response content"
    wrapped = wrap_http_error(
        mocker.Mock(side_effect=RequestException("Bad Request", response=response))
    )

    with pytest.raises(MPTAPIError) as error:
        wrapped()

    assert "invalid response content" in str(error.value)


def test_wrap_http_error_non_list_details(mocker):
    response = mocker.Mock(spec=Response)
    response.status_code = 400
    response.json.return_value = {"errors": {"name": "is required"}}
    wrapped = wrap_http_error(
        mocker.Mock(side_effect=RequestException("Bad Request", response=response))
    )

    with pytest.raises(MPTAPIError) as error:
        wrapped()

    assert "name: is required" in str(error.value)


def test_wrap_http_error_non_dict_payload(mocker):
    response = mocker.Mock(spec=Response)
    response.status_code = 400
    response.json.return_value = ["invalid", "payload"]
    response.content = b"invalid payload content"
    response.text = "invalid payload content"
    wrapped = wrap_http_error(
        mocker.Mock(side_effect=RequestException("Bad Request", response=response))
    )

    with pytest.raises(MPTAPIError) as error:
        wrapped()

    assert "invalid payload content" in str(error.value)
