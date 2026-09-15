"""
inverted_index.py — VaartaVerse Classical IR Engine
=====================================================
Hand-crafted inverted index implementation.

Data structures:
    Postings list:  term → {doc_id: PostingEntry}
    PostingEntry:   {tf: int, positions: list[int], zones: dict[str, list[int]]}
    DocRegistry:    doc_id → DocMeta (tale_id, title, tale_type, region, collection, …)

Persistence: serialised to JSON on disk via INDEX_DIR env variable.
The index is built from MongoDB at startup (if persisted index is stale/absent).
"""

import json
import math
import os
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from app.core.preprocessing import preprocess_zones

load_dotenv()

INDEX_DIR = Path(os.getenv("INDEX_DIR", "./data/index"))
POSTINGS_FILE = INDEX_DIR / "postings.json"
DOC_REGISTRY_FILE = INDEX_DIR / "doc_registry.json"


@dataclass
class PostingEntry:
    tf: int = 0
    positions: list[int] = field(default_factory=list)
    # per-zone positions: {"title": [...], "body": [...]}
    zones: dict = field(default_factory=lambda: {"title": [], "body": []})


@dataclass
class DocMeta:
    doc_id: str
    tale_id: str
    title: str
    tale_type: str
    region: str
    tradition: str
    source_collection: str
    translator: str
    collection_era: str
    token_count: int = 0


class InvertedIndex:
    """
    In-memory inverted index with optional JSON disk persistence.

    Usage:
        index = InvertedIndex()
        index.load_or_build()           # load from disk or rebuild from MongoDB
        index.add_document(...)          # add a single tale variant
        index.get_postings("jackal")     # → {doc_id: PostingEntry, ...}
        index.get_df("jackal")           # → document frequency count
        index.doc_count()               # → total number of documents
    """

    def __init__(self):
        # term → {doc_id → PostingEntry}
        self._postings: dict[str, dict[str, PostingEntry]] = defaultdict(dict)
        # doc_id → DocMeta
        self._docs: dict[str, DocMeta] = {}

    # ------------------------------------------------------------------
    # Index Construction
    # ------------------------------------------------------------------

    def add_document(
        self,
        doc_id: str,
        tale_id: str,
        title: str,
        body: str,
        tale_type: str,
        region: str,
        tradition: str,
        source_collection: str,
        translator: str = "",
        collection_era: str = "",
    ) -> None:
        """
        Tokenize and index a single tale variant.
        Zones: title tokens weighted separately from body tokens.
        Positions are global (title tokens come first in the linear sequence).
        """
        zones = preprocess_zones(title, body, stem=True)
        all_tokens = zones["all"]

        self._docs[doc_id] = DocMeta(
            doc_id=doc_id,
            tale_id=tale_id,
            title=title,
            tale_type=tale_type,
            region=region,
            tradition=tradition,
            source_collection=source_collection,
            translator=translator,
            collection_era=collection_era,
            token_count=len(all_tokens),
        )

        # Build postings
        for pos, token in enumerate(all_tokens):
            if doc_id not in self._postings[token]:
                self._postings[token][doc_id] = PostingEntry()
            entry = self._postings[token][doc_id]
            entry.tf += 1
            entry.positions.append(pos)

        # Zone-level positions
        title_len = len(zones["title"])
        for pos, token in enumerate(zones["title"]):
            self._postings[token][doc_id].zones["title"].append(pos)
        for pos, token in enumerate(zones["body"]):
            self._postings[token][doc_id].zones["body"].append(pos + title_len)

    # ------------------------------------------------------------------
    # Query Helpers
    # ------------------------------------------------------------------

    def get_postings(self, term: str) -> dict[str, PostingEntry]:
        """Return postings dict for a (already stemmed) term."""
        return self._postings.get(term, {})

    def get_df(self, term: str) -> int:
        """Document frequency for a term."""
        return len(self._postings.get(term, {}))

    def get_all_doc_ids(self) -> set[str]:
        return set(self._docs.keys())

    def doc_count(self) -> int:
        return len(self._docs)

    def get_doc_meta(self, doc_id: str) -> Optional[DocMeta]:
        return self._docs.get(doc_id)

    def get_variants_by_tale_type(self, tale_type_id: str) -> list[dict]:
        """Return all DocMeta records matching a tale_type_id."""
        return [
            asdict(meta)
            for meta in self._docs.values()
            if meta.tale_type.lower() == tale_type_id.lower()
        ]

    def vocabulary(self) -> set[str]:
        return set(self._postings.keys())

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Serialize index to JSON files on disk."""
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        # Postings
        serializable = {
            term: {
                doc_id: {
                    "tf": e.tf,
                    "positions": e.positions,
                    "zones": e.zones,
                }
                for doc_id, e in postings.items()
            }
            for term, postings in self._postings.items()
        }
        POSTINGS_FILE.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
        # Doc registry
        DOC_REGISTRY_FILE.write_text(
            json.dumps({k: asdict(v) for k, v in self._docs.items()}, indent=2),
            encoding="utf-8",
        )
        print(f"[InvertedIndex] Saved {len(self._docs)} docs, {len(self._postings)} terms to disk.")

    def load(self) -> bool:
        """Load index from disk. Returns True if successful."""
        if not POSTINGS_FILE.exists() or not DOC_REGISTRY_FILE.exists():
            return False
        raw_postings = json.loads(POSTINGS_FILE.read_text(encoding="utf-8"))
        self._postings = defaultdict(dict)
        for term, postings in raw_postings.items():
            for doc_id, data in postings.items():
                self._postings[term][doc_id] = PostingEntry(
                    tf=data["tf"],
                    positions=data["positions"],
                    zones=data["zones"],
                )
        raw_docs = json.loads(DOC_REGISTRY_FILE.read_text(encoding="utf-8"))
        self._docs = {k: DocMeta(**v) for k, v in raw_docs.items()}
        print(f"[InvertedIndex] Loaded {len(self._docs)} docs, {len(self._postings)} terms from disk.")
        return True

    def load_or_build(self) -> None:
        """
        Attempt to load persisted index; if absent, trigger build from MongoDB.
        TODO: Wire up MongoDB ingestion pipeline when corpus is available.
        """
        if not self.load():
            print(
                "[InvertedIndex] No persisted index found. "
                "Index will be empty until documents are ingested via /ingest endpoint. "
                "TODO: implement MongoDB corpus pull when tale variants are loaded."
            )
