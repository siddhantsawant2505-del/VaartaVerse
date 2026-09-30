"""Shared fixtures: a tiny deterministic index for unit tests."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.inverted_index import InvertedIndex  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # noqa: E402

DOCS = [
    # doc_id, title, body
    ("A", "Tiger fable", "the tiger prowls"),
    ("B", "Jackal and tiger", "a jackal outwits the tiger"),
    ("C", "Lion fable", "the lion sleeps"),
    ("D", "Jackal tale", "a clever jackal story"),
]


@pytest.fixture()
def tiny_index() -> InvertedIndex:
    idx = InvertedIndex()
    for doc_id, title, body in DOCS:
        idx.add_document(doc_id, doc_id, title, body, "T", "", "", "", "", "")
    return idx
