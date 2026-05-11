from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List


class ScenarioBuilder:
    def __init__(self) -> None:
        self._terms: List[str] = []
        self._relations: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def add_term(self, term: str) -> None:
        if term not in self._terms:
            self._terms.append(term)

    def add_relation(self, term: str, relation: Dict[str, Any]) -> None:
        self.add_term(term)
        self._relations[term].append(relation)

    def export(self) -> Dict[str, Any]:
        return {
            "terms": list(self._terms),
            "relations": {
                term: list(self._relations.get(term, []))
                for term in self._terms
            },
        }
