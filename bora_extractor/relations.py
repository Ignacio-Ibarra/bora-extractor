from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Iterable, List, Optional, Sequence

from spacy.language import Language
from spacy.tokens import Doc

from .schema import Entity, Relation


class RelationRule(ABC):
    @abstractmethod
    def apply(self, doc: Doc, entities: Sequence[Entity]) -> List[Relation]:
        raise NotImplementedError


class SentenceEntityRelationRule(RelationRule):
    def __init__(self, left_label: str, right_label: str, predicate: str) -> None:
        self.left_label = left_label
        self.right_label = right_label
        self.predicate = predicate

    def apply(self, doc: Doc, entities: Sequence[Entity]) -> List[Relation]:
        relations: List[Relation] = []
        sentence_entities = self._entities_by_sentence(entities)
        for sentence, sentence_entities in sentence_entities.items():
            for left in sentence_entities:
                if left.label != self.left_label:
                    continue
                for right in sentence_entities:
                    if left is right or right.label != self.right_label:
                        continue
                    if left.start_char < right.start_char:
                        relations.append(
                            Relation(
                                subject=left.to_dict(),
                                predicate=self.predicate,
                                object=right.to_dict(),
                                sentence=sentence,
                            )
                        )
        return relations

    @staticmethod
    def _entities_by_sentence(entities: Iterable[Entity]) -> Dict[str, List[Entity]]:
        mapping: Dict[str, List[Entity]] = {}
        for ent in entities:
            sentence = ent.sentence or ""
            mapping.setdefault(sentence, []).append(ent)
        return mapping


class RelationExtractor:
    def __init__(self, rules: Optional[Iterable[RelationRule]] = None) -> None:
        self.rules = list(rules or [])

    def extract_relations(self, doc: Doc, entities: Sequence[Entity]) -> List[Relation]:
        relations: List[Relation] = []
        for rule in self.rules:
            relations.extend(rule.apply(doc, entities))
        return relations

    @classmethod
    def default(cls, nlp: Optional[Language] = None) -> "RelationExtractor":
        return cls(
            rules=[
                SentenceEntityRelationRule("PER", "ORG", "associated_with"),
                SentenceEntityRelationRule("PER", "LOC", "mentioned_in"),
                SentenceEntityRelationRule("ORG", "LOC", "located_in"),
            ]
        )


def build_doc(text: str, model_name: str = "es_core_news_sm") -> Doc:
    import spacy

    nlp = spacy.load(model_name)
    return nlp(text)
