import os
import requests
from requests import Response, RequestException
from dotenv import load_dotenv
from bora_extractor.config import DEFAULT_HEADERS

load_dotenv()


def set_proxy_config()-> None:
    proxy_host = os.getenv("PROXY_HOST")
    proxy_port = os.getenv("PROXY_PORT")
    proxy_user = os.getenv("PROXY_USER")
    proxy_pass = os.getenv("PROXY_PASS")

    os.environ['HTTP_PROXY']= f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}" 
    os.environ['HTTPS_PROXY'] = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"


def make_request(url: str, timeout: int = 15) -> Response:
    
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.content.decode('utf-8')
    except RequestException as exc:
        raise RuntimeError(f"Error while fetching {url}: {exc}") from exc
    


