import os
import requests
from requests import Response, RequestException
from dotenv import load_dotenv
from bora_extractor.config import DEFAULT_HEADERS

load_dotenv()


def set_proxy_config() -> None:
    proxy_host = os.getenv("BORA_PROXY_HOST")
    proxy_port = os.getenv("BORA_PROXY_PORT")
    proxy_user = os.getenv("BORA_PROXY_USER")
    proxy_pass = os.getenv("BORA_PROXY_PASS")

    if not all([proxy_host, proxy_port, proxy_user, proxy_pass]):
        return

    proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
    os.environ['HTTP_PROXY'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url


def make_request(url: str, timeout: int = 15) -> Response:
    
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.content.decode('utf-8')
    except RequestException as exc:
        raise RuntimeError(f"Error while fetching {url}: {exc}") from exc
    


