import json
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from .schema import ExtractedDocument
from .config import DEFAULT_URL_FIELDS, DEFAULT_METADATA_FIELDS, DEFAULT_HEADERS
import os
from dotenv import load_dotenv

load_dotenv()


def set_proxy_config()-> None:
    proxy_host = os.getenv("PROXY_HOST")
    proxy_port = os.getenv("PROXY_PORT")
    proxy_user = os.getenv("PROXY_USER")
    proxy_pass = os.getenv("PROXY_PASS")

    os.environ['HTTP_PROXY']= f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}" 
    os.environ['HTTPS_PROXY'] = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"


def load_json_file(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _is_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def collect_links_from_json(
    data: Any,
    url_fields: Optional[Iterable[str]] = None,
    metadata_fields: Optional[Iterable[str]] = None,
) -> Generator[Dict[str, Any], None, None]:
    url_fields = set(url_fields or DEFAULT_URL_FIELDS)
    metadata_fields = set(metadata_fields or DEFAULT_METADATA_FIELDS)

    def walk(node: Any, ancestor_metadata: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        if isinstance(node, Mapping):
            current_metadata = ancestor_metadata.copy()
            for key, value in node.items():
                lower_key = key.lower()
                if lower_key in metadata_fields and not isinstance(value, (dict, list)):
                    current_metadata[key] = value
            for key, value in node.items():
                lower_key = key.lower()
                if lower_key in url_fields and isinstance(value, str) and _is_url(value):
                    yield {
                        "url": value,
                        "metadata": current_metadata,
                    }
                else:
                    yield from walk(value, current_metadata)
        elif isinstance(node, list):
            for element in node:
                yield from walk(element, ancestor_metadata)

    yield from walk(data, {})


def fetch_html_from_url(url: str, timeout: int = 15) -> str:
    set_proxy_config()
    request = Request(url, headers=DEFAULT_HEADERS)
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode(response.headers.get_content_charset("utf-8"), errors="ignore")
    except HTTPError as exc:
        raise RuntimeError(f"HTTP error while fetching {url}: {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"Unable to fetch {url}: {exc.reason}") from exc


def load_html_from_file(path: Path) -> str:
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def save_extracted_document(document: ExtractedDocument, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(document.to_dict(), handle, indent=2, ensure_ascii=False)
