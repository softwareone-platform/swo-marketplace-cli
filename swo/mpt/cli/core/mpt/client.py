import inspect
import json
import logging
from urllib.parse import urljoin

from requests import PreparedRequest, Request, Response, Session
from requests.adapters import HTTPAdapter, Retry
from swo.mpt.cli.core.accounts.models import Account
from swo.mpt.cli.core.state import state

logger = logging.getLogger(__name__)


class MPTClient(Session):
    def __init__(self, base_url: str, api_token: str, debug: bool = False):
        super().__init__()
        self.debug = debug
        retries = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504],
        )
        self.mount("http://", HTTPAdapter(max_retries=retries))
        self.headers.update(
            {
                "User-Agent": "swo-marketplace-cli/1.0",
                "Authorization": f"Bearer {api_token}",
            },
        )
        self.base_url = f"{base_url}/" if base_url[-1] != "/" else base_url
        self.api_token = api_token

    def request(
        self, method: str | bytes, url: str | bytes, *args, **kwargs
    ) -> Response:
        url = self.join_url(str(url))

        if self.debug:
            # Get caller info
            caller_frame = inspect.currentframe().f_back  # type: ignore
            caller_info = inspect.getframeinfo(caller_frame) # type: ignore

            # Log request details
            logger.debug(
                f"HTTP Request from {caller_info.filename}:{caller_info.lineno}\n"
                f"Method: {method!r}\n"
                f"URL: {url}"
            )

        response = super().request(method, url, *args, **kwargs)

        if self.debug:
            # Log response details
            logger.debug(
                f"Response Status: {response.status_code}\n"
                f"Response Body: {
                    json.dumps(
                        response.json(),
                        indent=2
                    ) if response.text else 'No body'
                    }"
            )

        return response

    def prepare_request(self, request: Request, *args, **kwargs) -> PreparedRequest:
        request.url = self.join_url(request.url)
        return super().prepare_request(request, *args, **kwargs)

    def join_url(self, url: str) -> str:
        url = url[1:] if url[0] == "/" else url
        return urljoin(self.base_url, url, allow_fragments=True)


def client_from_account(account: Account) -> MPTClient:
    """
    Creates MPT Client from the Account
    """
    return MPTClient(
        api_token=account.token,
        base_url=account.environment,
        debug=state.verbose
    )
