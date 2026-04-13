from pathlib import Path

from bora_extractor.extraction import extract_text_from_html


def test_extract_text_from_html_with_xpath() -> None:
    html = "<html><body><div id='texto'><p>Hola BORA</p></div></body></html>"
    extracted = extract_text_from_html(html, ["//div[@id='texto']//text()"])

    assert "Hola BORA" in extracted


def test_extract_text_from_html_falls_back_to_body_text() -> None:
    html = "<html><body><p>Texto sin xpath</p></body></html>"
    extracted = extract_text_from_html(html, ["//div[@id='inexistente']//text()"])

    assert "Texto sin xpath" in extracted
