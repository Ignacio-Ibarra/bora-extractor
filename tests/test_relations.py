import pytest
from spacy.util import is_package

from bora_extractor.ner import load_nlp
from bora_extractor.relations import RelationExtractor
from bora_extractor.schema import Entity


@pytest.mark.skipif(not is_package("es_core_news_sm"), reason="es_core_news_sm model is not installed")
def test_relation_extractor_builds_simple_entity_relations() -> None:
    text = "Juan Pérez trabaja en Acme S.A. en Buenos Aires."
    nlp = load_nlp()
    doc = nlp(text)

    entities = [
        Entity(
            text=ent.text,
            label=ent.label_,
            start_char=ent.start_char,
            end_char=ent.end_char,
            sentence=ent.sent.text if ent.sent is not None else None,
        )
        for ent in doc.ents
    ]

    extractor = RelationExtractor.default()
    relations = extractor.extract_relations(doc, entities)

    assert any(relation.predicate == "associated_with" for relation in relations)
