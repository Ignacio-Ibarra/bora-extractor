from __future__ import annotations

from bs4 import BeautifulSoup
from lxml import etree, html
from typing import Iterable, List, Optional


DEFAULT_XPATHS = [
    "//div[@class='texto']//text()",
    "//div[@id='texto']//text()",
    "//div[contains(@class,'content')]//text()",
    "//body//text()",
]


def _normalize_text(raw_text: str) -> str:
    return " ".join(raw_text.split())


def extract_text_using_xpaths(html_text: str, xpaths: Iterable[str]) -> List[str]:
    parser = html.HTMLParser(encoding="utf-8")
    document = html.fromstring(html_text, parser=parser)
    extracted_texts: List[str] = []
    for xpath in xpaths:
        try:
            nodes = document.xpath(xpath)
        except etree.XPathError:
            continue
        for node in nodes:
            if isinstance(node, etree._ElementUnicodeResult):
                text_value = str(node)
            elif isinstance(node, etree._Element):
                text_value = node.text_content()
            else:
                text_value = str(node)
            cleaned = _normalize_text(text_value)
            if cleaned:
                extracted_texts.append(cleaned)
    return extracted_texts


def extract_text_from_html(html_text: str, xpaths: Optional[Iterable[str]] = None) -> str:
    xpaths = list(xpaths or DEFAULT_XPATHS)
    extracted_parts = extract_text_using_xpaths(html_text, xpaths)
    if extracted_parts:
        return "\n\n".join(extracted_parts)

    soup = BeautifulSoup(html_text, "lxml")
    fallback = soup.get_text(separator=" ", strip=True)
    return _normalize_text(fallback)
