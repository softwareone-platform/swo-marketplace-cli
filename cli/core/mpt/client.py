import inspect
import json
import logging
from typing import override
from urllib.parse import urljoin

from cli.core.accounts.models import Account
from cli.core.state import state
from requests import PreparedRequest, Request, Response, Session

logger = logging.getLogger(__name__)


class MPTClient(Session):
    """HTTP client for interacting with MPT API endpoints.

    Attributes:
        debug: Whether to enable debug logging for requests/responses.
        base_url: Base URL for all API requests.
        api_token: Authentication token for API access.
    """

    def __init__(self, base_url: str, api_token: str, *, debug: bool = False):
        super().__init__()
        self.debug = debug
        self.headers.update(
            {
                "User-Agent": "swo-marketplace-cli/1.0",
                "Authorization": f"Bearer {api_token}",
            },
        )
        normalized = base_url.rstrip("/")
        self.base_url = urljoin(normalized, "/public/v1/")

        self.api_token = api_token

    @override
    def request(self, method: str | bytes, url: str | bytes, *args, **kwargs) -> Response:
        url = self.join_url(str(url))

        if self.debug:
            caller_frame = inspect.currentframe().f_back  # type: ignore[union-attr]
            caller_info = inspect.getframeinfo(caller_frame)  # type: ignore[arg-type]

            logger.debug(
                "HTTP Request from %s:%s\nMethod: %r\nURL: %s",
                caller_info.filename,
                caller_info.lineno,
                repr(method),
                url,
            )

        response = super().request(method, url, *args, **kwargs)

        if self.debug:
            logger.debug(
                "Response Status: %s\nResponse Body: %s",
                response.status_code,
                json.dumps(response.json(), indent=2) if response.text else "No body",
            )

        return response

    @override
    def prepare_request(self, request: Request, *args, **kwargs) -> PreparedRequest:
        request.url = self.join_url(request.url)
        return super().prepare_request(request, *args, **kwargs)

    def join_url(self, url: str) -> str:
        """Join the base URL with the provided URL path.

        Args:
            url: The URL path to join with the base URL.

        Returns:
            The full URL as a string.

        """
        url = url[1:] if url and url[0] == "/" else url
        return urljoin(self.base_url, url, allow_fragments=True)


def client_from_account(account: Account) -> MPTClient:
    """Creates MPT Client from the Account."""
    return MPTClient(api_token=account.token, base_url=account.environment, debug=state.verbose)
