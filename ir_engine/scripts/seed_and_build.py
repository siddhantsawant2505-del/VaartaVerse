#!/usr/bin/env python3
"""
seed_and_build.py — VaartaVerse Corpus Seed & Index Build CLI
==============================================================
One-shot script that:
  1. Reads the seed corpus JSON (data/corpus/tales.json)
  2. (Optionally) pushes tale records into MongoDB via pymongo
  3. Builds the inverted index
  4. Persists the index to disk (data/index/)
  5. Prints a summary report

Usage (from ir_engine/ directory, with venv active):
    python scripts/seed_and_build.py
    python scripts/seed_and_build.py --source mongodb
    python scripts/seed_and_build.py --mongo-only    # skip index build, just seed Mongo
    python scripts/seed_and_build.py --report        # only print index stats
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Allow imports from the ir_engine root
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.core.inverted_index import InvertedIndex
from app.core.ingestion import IngestionPipeline

CORPUS_PATH = Path(os.getenv("CORPUS_PATH", "./data/corpus/tales.json"))
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/vaartaverse")


def seed_mongodb(tales: list[dict]) -> int:
    """Push tale records into MongoDB. Returns count inserted."""
    try:
        import pymongo
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        db = client.get_database()
        collection = db["talevariants"]

        inserted = 0
        for tale in tales:
            # Upsert by tale_id
            result = collection.update_one(
                {"tale_id": tale["tale_id"]},
                {"$set": tale},
                upsert=True,
            )
            if result.upserted_id or result.modified_count:
                inserted += 1

        print(f"[MongoDB] Seeded {inserted}/{len(tales)} tale variants into 'vaartaverse.talevariants'")
        return inserted
    except Exception as e:
        print(f"[MongoDB] Connection failed: {e} — skipping MongoDB seed.")
        return 0


def print_index_report(index: InvertedIndex) -> None:
    """Print a structured summary of the built index."""
    docs = index._docs
    traditions = {}
    tale_types = {}

    for meta in docs.values():
        traditions[meta.tradition] = traditions.get(meta.tradition, 0) + 1
        tale_types[meta.tale_type] = tale_types.get(meta.tale_type, 0) + 1

    print("\n" + "=" * 60)
    print("  VaartaVerse Inverted Index — Build Report")
    print("=" * 60)
    print(f"  Total documents indexed  : {index.doc_count()}")
    print(f"  Unique stemmed terms     : {len(index.vocabulary())}")
    print(f"  Postings lists           : {sum(len(p) for p in index._postings.values())}")
    print()

    print("  Documents by Tradition:")
    for trad, count in sorted(traditions.items()):
        bar = "#" * count
        print(f"    {trad:<35} {bar} ({count})")

    print()
    print("  Documents by Tale Type (ATU/Custom):")
    for ttype, count in sorted(tale_types.items()):
        bar = "#" * count
        print(f"    {ttype:<20} {bar} ({count})")

    print()
    top_terms = sorted(
        ((term, sum(e.tf for e in postings.values()))
         for term, postings in index._postings.items()),
        key=lambda x: x[1], reverse=True
    )[:20]
    print("  Top 20 Terms by Collection Frequency:")
    for term, cf in top_terms:
        print(f"    {term:<20} cf={cf}")

    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="VaartaVerse Corpus Seed & Index Build")
    parser.add_argument("--source", choices=["json", "mongodb", "both"], default="json",
                        help="Index build source (default: json)")
    parser.add_argument("--mongo-only", action="store_true",
                        help="Only seed MongoDB; do not build the IR index")
    parser.add_argument("--report", action="store_true",
                        help="Load existing index from disk and print report only")
    parser.add_argument("--corpus", type=str, default=None,
                        help="Path to corpus JSON file (overrides CORPUS_PATH env)")
    args = parser.parse_args()

    corpus_path = Path(args.corpus) if args.corpus else CORPUS_PATH

    # --- Report only mode ---
    if args.report:
        index = InvertedIndex()
        if index.load():
            print_index_report(index)
        else:
            print("[Error] No persisted index found. Run without --report to build first.")
        return

    # --- Load corpus ---
    if not corpus_path.exists():
        print(f"[Error] Corpus file not found: {corpus_path}")
        sys.exit(1)

    tales = json.loads(corpus_path.read_text(encoding="utf-8"))
    print(f"[Corpus] Loaded {len(tales)} tale records from {corpus_path}")

    # --- Optionally seed MongoDB ---
    seed_mongodb(tales)

    if args.mongo_only:
        print("[Done] MongoDB seeded. Index build skipped (--mongo-only).")
        return

    # --- Build inverted index ---
    print(f"\n[Index] Building inverted index from source='{args.source}'...")
    index = InvertedIndex()
    pipeline = IngestionPipeline(index)

    if args.source == "mongodb":
        stats = pipeline.ingest_from_mongodb()
    elif args.source == "both":
        stats = pipeline.ingest_from_json(corpus_path)
        stats2 = pipeline.ingest_from_mongodb()
        stats["documents_ingested"] += stats2.get("documents_ingested", 0)
    else:
        stats = pipeline.ingest_from_json(corpus_path)

    if stats["documents_ingested"] == 0:
        print("[Warning] No documents were ingested. Check corpus file and errors below.")
        for err in stats["errors"]:
            print(f"  ERROR: {err}")
        sys.exit(1)

    pipeline.save_index()

    if stats["errors"]:
        print(f"\n[Warnings] {len(stats['errors'])} issues during ingestion:")
        for err in stats["errors"][:5]:
            print(f"  - {err}")

    print_index_report(index)
    print(f"[Done] Index persisted to disk. {stats['documents_ingested']} docs ready for retrieval.\n")


if __name__ == "__main__":
    main()
