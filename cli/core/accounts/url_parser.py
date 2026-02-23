import re
from urllib.parse import urlsplit, urlunparse

INVALID_ENV_URL_MESSAGE = "Invalid environment URL. Expected scheme://host[:port]"
PATH_TO_REMOVE_RE = re.compile(r"^/$|^/public/?$|^/public/v1/?$")


def protocol_and_host(environment_url: str) -> str:
    """Compose environment URL from input URL removing useless parts."""
    split_result = urlsplit(environment_url, scheme="https")
    if split_result.scheme and split_result.hostname:
        host = (
            f"[{split_result.hostname}]" if ":" in split_result.hostname else split_result.hostname
        )
        port = f":{split_result.port}" if split_result.port else ""
        path = PATH_TO_REMOVE_RE.sub("", split_result.path)
        return urlunparse((split_result.scheme, f"{host}{port}", path, "", "", ""))
    raise ValueError(INVALID_ENV_URL_MESSAGE)
