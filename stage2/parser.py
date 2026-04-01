from __future__ import annotations

import re
from typing import Dict, Optional

from .schemas import QueryConstraints, QueryRequest

STOPWORDS = {
    "where", "is", "the", "a", "an", "please", "find", "show", "me", "nearest",
    "closest", "located", "of", "to", "my", "can", "you", "tell", "what", "are",
    "there", "near", "in", "at", "on", "with", "from"
}

COLOR_WORDS = {
    "red", "blue", "green", "yellow", "black", "white", "brown", "gray", "grey",
    "orange", "purple", "pink", "silver", "gold"
}


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-zA-Z0-9 ]", " ", text.lower())).strip()


def _extract_near_phrase(query: str) -> Optional[str]:
    match = re.search(r"\bnear\s+the\s+([a-zA-Z ]+)|\bnear\s+([a-zA-Z ]+)", query.lower())
    if not match:
        return None
    return next((group.strip() for group in match.groups() if group), None)


def _extract_object_phrase(query: str) -> Optional[str]:
    cleaned = _normalize_text(query)
    tokens = [t for t in cleaned.split() if t not in STOPWORDS]
    if not tokens:
        return None
    return " ".join(tokens)


def parse_query(raw_query: str) -> QueryRequest:
    cleaned = _normalize_text(raw_query)
    intent = "locate_object"
    if cleaned.startswith("describe") or "what is in" in cleaned:
        intent = "describe_scene"
    elif cleaned.startswith("list"):
        intent = "list_objects"

    attributes: Dict[str, str] = {}
    for token in cleaned.split():
        if token in COLOR_WORDS:
            attributes["color"] = token

    constraints = QueryConstraints(
        nearest=("nearest" in cleaned or "closest" in cleaned or True),
        near=_extract_near_phrase(raw_query),
    )

    object_name = None if intent != "locate_object" else _extract_object_phrase(raw_query)
    return QueryRequest(
        raw_query=raw_query,
        intent=intent,
        object_name=object_name,
        attributes=attributes,
        constraints=constraints,
    )
