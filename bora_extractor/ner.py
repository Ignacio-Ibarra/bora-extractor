from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

import spacy
from spacy.language import Language
from spacy.tokens import Doc

from .schema import Entity


@lru_cache(maxsize=1)
def load_nlp(model_name: str = "es_core_news_sm") -> Language:
    return spacy.load(model_name)


def extract_entities(text: str, model_name: str = "es_core_news_sm") -> List[Entity]:
    nlp = load_nlp(model_name)
    doc = nlp(text)
    return [_entity_from_spacy(ent) for ent in doc.ents]


def _entity_from_spacy(spacy_entity: "spacy.tokens.Span") -> Entity:
    sentence_text = spacy_entity.sent.text if spacy_entity.sent is not None else None
    return Entity(
        text=spacy_entity.text,
        label=spacy_entity.label_,
        start_char=spacy_entity.start_char,
        end_char=spacy_entity.end_char,
        sentence=sentence_text,
    )


def extract_entities_from_doc(doc: Doc) -> List[Entity]:
    return [_entity_from_spacy(ent) for ent in doc.ents]


def build_doc(text: str, model_name: str = "es_core_news_sm") -> Doc:
    return load_nlp(model_name)(text)
