import json
from pathlib import Path

from bora_extractor.io import collect_links_from_json, load_json_file, save_extracted_document
from bora_extractor.schema import ExtractedDocument


def test_collect_links_from_json_extracts_urls_and_metadata(tmp_path: Path) -> None:
    example = {
        "search": "test",
        "results": [
            {"url": "https://example.com/1", "id_publicacion": "123"},
            {"href": "https://example.com/2", "fecha": "2026-04-13"},
        ],
    }
    json_path = tmp_path / "sample.json"
    json_path.write_text(json.dumps(example, ensure_ascii=False), encoding="utf-8")

    data = load_json_file(json_path)
    links = list(collect_links_from_json(data))

    assert links[0]["url"] == "https://example.com/1"
    assert links[0]["metadata"]["id_publicacion"] == "123"
    assert links[1]["url"] == "https://example.com/2"
    assert links[1]["metadata"]["fecha"] == "2026-04-13"


def test_save_extracted_document_creates_json(tmp_path: Path) -> None:
    document = ExtractedDocument(metadata={"source_file": "test", "url": "https://example.com"}, text="Hola mundo")
    output_file = tmp_path / "output.json"
    save_extracted_document(document, output_file)

    assert output_file.exists()
    loaded = json.loads(output_file.read_text(encoding="utf-8"))
    assert loaded["metadata"]["url"] == "https://example.com"
    assert loaded["text"] == "Hola mundo"
