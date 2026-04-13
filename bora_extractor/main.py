from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .extraction import DEFAULT_XPATHS, extract_text_from_html
from .io import (
    collect_links_from_json,
    fetch_html_from_url,
    load_html_from_file,
    load_json_file,
    save_extracted_document,
)
from .ner import build_doc, extract_entities_from_doc, load_nlp
from .relations import RelationExtractor
from .schema import ExtractedDocument

logger = logging.getLogger(__name__)


def _sanitize_filename(value: str) -> str:
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in value)
    return safe[:120] or "document"


def _build_metadata(source_path: Path, url: str, extra: Dict[str, Any]) -> Dict[str, Any]:
    metadata = {"source_file": str(source_path), "url": url}
    metadata.update(extra or {})
    return metadata


def _build_output_path(output_dir: Path, source_path: Path, metadata: Dict[str, Any], index: int) -> Path:
    output_dir = output_dir / source_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    source_id = metadata.get("id") or metadata.get("id_publicacion") or metadata.get("titulo") or metadata.get("title")
    fallback_name = f"document_{index + 1:03d}"
    file_stem = _sanitize_filename(str(source_id)) if source_id else fallback_name
    return output_dir / f"{file_stem}.json"


def process_html(
    html_text: str,
    source_path: Path,
    url: str,
    metadata: Dict[str, Any],
    output_path: Path,
    xpaths: Optional[Iterable[str]] = None,
) -> Path:
    text = extract_text_from_html(html_text, xpaths or DEFAULT_XPATHS)
    doc = build_doc(text)
    entities = extract_entities_from_doc(doc)
    relations = RelationExtractor.default().extract_relations(doc, entities)

    document = ExtractedDocument(metadata=_build_metadata(source_path, url, metadata), text=text, entities=entities, relations=relations)
    save_extracted_document(document, output_path)
    logger.info("Saved extracted JSON to %s", output_path)
    return output_path


def process_url(
    url: str,
    output_path: Path,
    xpaths: Optional[Iterable[str]] = None,
) -> Path:
    html_text = fetch_html_from_url(url)
    return process_html(html_text, Path(url), url, {}, output_path, xpaths=xpaths)


def process_html_file(
    html_path: Path,
    output_path: Path,
    xpaths: Optional[Iterable[str]] = None,
) -> Path:
    html_text = load_html_from_file(html_path)
    return process_html(html_text, html_path, str(html_path), {}, output_path, xpaths=xpaths)


def process_wrapper_json(
    source_path: Path,
    output_dir: Path,
    xpaths: Optional[Iterable[str]] = None,
    url_fields: Optional[Iterable[str]] = None,
    metadata_fields: Optional[Iterable[str]] = None,
) -> List[Path]:
    json_data = load_json_file(source_path)
    output_paths: List[Path] = []
    links = list(collect_links_from_json(json_data, url_fields=url_fields, metadata_fields=metadata_fields))
    if not links:
        logger.warning("No URLs found in %s", source_path)
        return output_paths

    for index, link in enumerate(links):
        url = link["url"]
        metadata = link.get("metadata", {})
        try:
            html_text = fetch_html_from_url(url)
        except Exception as exc:
            logger.warning("Skipping %s: %s", url, exc)
            continue

        output_path = _build_output_path(output_dir, source_path, metadata, index)
        process_html(html_text, source_path, url, metadata, output_path, xpaths=xpaths)
        output_paths.append(output_path)

    return output_paths


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extrae texto, NER y relaciones de páginas BORA.")
    parser.add_argument("--input-json", type=Path, help="Archivo JSON de entrada generado por bora_wrapper.")
    parser.add_argument("--url", type=str, help="URL de una página individual a procesar.")
    parser.add_argument("--html-file", type=Path, help="Archivo HTML local a procesar.")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Directorio donde guardar los JSON de salida.")
    parser.add_argument("--output-file", type=Path, help="Archivo de salida para un solo documento.")
    parser.add_argument("--xpath", action="append", help="XPath de texto a extraer. Puede repetirse.")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = _build_parser()
    args = parser.parse_args(argv)
    xpaths = args.xpath or DEFAULT_XPATHS

    if args.input_json:
        process_wrapper_json(args.input_json, args.output_dir, xpaths=xpaths)
        return 0

    if args.url and args.output_file:
        process_url(args.url, args.output_file, xpaths=xpaths)
        return 0

    if args.html_file and args.output_file:
        process_html_file(args.html_file, args.output_file, xpaths=xpaths)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
