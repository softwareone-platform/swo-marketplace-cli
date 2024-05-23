from urllib.parse import urljoin

from requests import PreparedRequest, Request, Response, Session
from requests.adapters import HTTPAdapter, Retry
from swo.mpt.cli.core.accounts.models import Account


class MPTClient(Session):
    def __init__(self, base_url: str, api_token: str):
        super().__init__()
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
        return super().request(method, url, *args, **kwargs)

    def prepare_request(self, request: Request, *args, **kwargs) -> PreparedRequest:
        request.url = self.join_url(request.url)
        return super().prepare_request(request, *args, **kwargs)

    def join_url(self, url: str) -> str:
        url = url[1:] if url[0] == "/" else url
        return urljoin(self.base_url, url, allow_fragments=True)


def client_from_account(account: Account) -> MPTClient:
    return MPTClient(account.environment, account.token)
