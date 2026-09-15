"""
ingestion.py — VaartaVerse Classical IR Engine
================================================
Corpus Ingestion Pipeline.

Handles the full pipeline from raw JSON corpus → preprocessing → inverted index build.
Also connects to MongoDB to read TaleVariant records from the metadata server.

Usage:
    from app.core.ingestion import IngestionPipeline
    pipeline = IngestionPipeline(index)
    pipeline.ingest_from_json("data/corpus/tales.json")
    pipeline.save_index()
"""

import json
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from app.core.inverted_index import InvertedIndex
from app.core.preprocessing import preprocess

load_dotenv()

CORPUS_PATH = Path(os.getenv("CORPUS_PATH", "./data/corpus/tales.json"))
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/vaartaverse")


class IngestionPipeline:
    """
    Manages building the inverted index from corpus sources:
      1. JSON seed file (data/corpus/tales.json)
      2. MongoDB TaleVariant collection (when populated)

    After ingestion, calls index.save() to persist to disk.
    """

    def __init__(self, index: InvertedIndex):
        self._index = index
        self._stats: dict = {
            "documents_ingested": 0,
            "terms_indexed": 0,
            "skipped": 0,
            "errors": [],
        }

    def ingest_document(self, doc: dict) -> bool:
        """
        Preprocess and add a single tale document to the inverted index.

        Args:
            doc: Dict with keys matching TaleVariant schema.

        Returns:
            True if ingested successfully, False otherwise.
        """
        required_fields = {"tale_id", "raw_text", "title"}
        if not required_fields.issubset(doc.keys()):
            missing = required_fields - doc.keys()
            self._stats["errors"].append(
                f"Skipping doc — missing fields: {missing}. doc keys: {list(doc.keys())}"
            )
            self._stats["skipped"] += 1
            return False

        tale_id = doc["tale_id"]
        # Use tale_id as doc_id for the index (stable, human-readable)
        doc_id = tale_id

        try:
            self._index.add_document(
                doc_id=doc_id,
                tale_id=tale_id,
                title=doc.get("title", ""),
                body=doc.get("raw_text", ""),
                tale_type=doc.get("tale_type", "UNKNOWN"),
                region=doc.get("region", "Unknown Region"),
                tradition=doc.get("tradition", "Unknown"),
                source_collection=doc.get("source_collection", ""),
                translator=doc.get("translator", ""),
                collection_era=doc.get("collection_era", ""),
            )
            self._stats["documents_ingested"] += 1
            return True
        except Exception as e:
            self._stats["errors"].append(f"Error ingesting {tale_id}: {e}")
            self._stats["skipped"] += 1
            return False

    def ingest_from_json(self, path: Optional[Path] = None) -> dict:
        """
        Load tales from a JSON file and ingest them into the index.

        Args:
            path: Path to JSON file. Defaults to CORPUS_PATH env variable.

        Returns:
            Ingestion statistics dict.
        """
        corpus_path = Path(path) if path else CORPUS_PATH

        if not corpus_path.exists():
            msg = f"Corpus file not found: {corpus_path}"
            self._stats["errors"].append(msg)
            print(f"[IngestionPipeline] {msg}")
            return self._stats

        print(f"[IngestionPipeline] Loading corpus from {corpus_path}")
        raw = json.loads(corpus_path.read_text(encoding="utf-8"))
        docs = raw if isinstance(raw, list) else [raw]

        for doc in docs:
            self.ingest_document(doc)

        self._stats["terms_indexed"] = len(self._index.vocabulary())
        print(
            f"[IngestionPipeline] Ingested {self._stats['documents_ingested']} docs, "
            f"{self._stats['terms_indexed']} unique stems, "
            f"{self._stats['skipped']} skipped."
        )
        return self._stats

    def ingest_from_mongodb(self) -> dict:
        """
        Load all TaleVariant documents from MongoDB and ingest into index.
        Requires pymongo and a running MongoDB instance.

        Returns:
            Ingestion statistics dict.
        """
        try:
            import pymongo
            client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            # Ping to verify connection
            client.admin.command("ping")
            db = client.get_database()
            collection = db["talevariants"]
            docs = list(collection.find({}, {"_id": 0}))

            if not docs:
                print("[IngestionPipeline] MongoDB collection 'talevariants' is empty.")
                return self._stats

            print(f"[IngestionPipeline] Found {len(docs)} docs in MongoDB.")
            for doc in docs:
                self.ingest_document(doc)

            self._stats["terms_indexed"] = len(self._index.vocabulary())
            return self._stats

        except Exception as e:
            msg = f"MongoDB connection failed: {e}. Falling back to JSON corpus."
            self._stats["errors"].append(msg)
            print(f"[IngestionPipeline] {msg}")
            return self.ingest_from_json()

    def save_index(self) -> None:
        """Persist the built index to disk."""
        self._index.save()

    @property
    def stats(self) -> dict:
        return self._stats
