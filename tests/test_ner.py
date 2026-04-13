import pytest
from spacy.util import is_package

from bora_extractor.ner import extract_entities


@pytest.mark.skipif(not is_package("es_core_news_sm"), reason="es_core_news_sm model is not installed")
def test_extract_entities_recognizes_person_and_org() -> None:
    text = "Juan Pérez trabaja en Acme S.A."
    entities = extract_entities(text)

    labels = {entity.label for entity in entities}
    assert "PER" in labels or "PERSON" in labels
    assert "ORG" in labels
