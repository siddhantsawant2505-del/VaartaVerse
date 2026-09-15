"""
VaartaVerse Classical IR Engine — FastAPI Entry Point
Implements all retrieval, feedback, evaluation, and divergence endpoints.
No LLMs, no external vector databases — pure hand-crafted IR math.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from app.core.inverted_index import InvertedIndex
from app.core.boolean_engine import BooleanEngine
from app.core.vsm_engine import VSMEngine
from app.core.relevance_feedback import RocchioFeedback
from app.core.nl_parser import NLQueryParser
from app.core.evaluation import EvaluationHarness
from app.core.divergence import DivergenceCalculator
from app.core.ingestion import IngestionPipeline

app = FastAPI(
    title="VaartaVerse Classical IR Engine",
    description=(
        "Hand-crafted Information Retrieval engine for cross-regional Indian folk tale lineage. "
        "Implements inverted index, Boolean retrieval, TF-IDF VSM, Rocchio feedback, "
        "rule-based NL query parsing, MAP/nDCG evaluation, and pairwise cosine divergence. "
        "No LLMs or external vector DBs."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Singletons — lazy-loaded on first request
# ---------------------------------------------------------------------------
_index: Optional[InvertedIndex] = None
_boolean_engine: Optional[BooleanEngine] = None
_vsm_engine: Optional[VSMEngine] = None
_rocchio: Optional[RocchioFeedback] = None
_nl_parser: Optional[NLQueryParser] = None
_eval_harness: Optional[EvaluationHarness] = None
_divergence: Optional[DivergenceCalculator] = None


def get_index() -> InvertedIndex:
    global _index
    if _index is None:
        _index = InvertedIndex()
        if not _index.load():
            # Auto-build from seed JSON corpus on first startup
            print("[VaartaVerse] No persisted index found — auto-building from seed corpus...")
            pipeline = IngestionPipeline(_index)
            stats = pipeline.ingest_from_json()
            if stats["documents_ingested"] > 0:
                pipeline.save_index()
                print(f"[VaartaVerse] Index built: {stats['documents_ingested']} docs, "
                      f"{stats['terms_indexed']} terms.")
            else:
                print("[VaartaVerse] Seed corpus empty or not found. Index will be empty.")
    return _index


def get_vsm() -> VSMEngine:
    global _vsm_engine
    if _vsm_engine is None:
        _vsm_engine = VSMEngine(get_index())
    return _vsm_engine


def get_boolean() -> BooleanEngine:
    global _boolean_engine
    if _boolean_engine is None:
        _boolean_engine = BooleanEngine(get_index())
    return _boolean_engine


def get_rocchio() -> RocchioFeedback:
    global _rocchio
    if _rocchio is None:
        _rocchio = RocchioFeedback(get_vsm())
    return _rocchio


def get_nl_parser() -> NLQueryParser:
    global _nl_parser
    if _nl_parser is None:
        _nl_parser = NLQueryParser()
    return _nl_parser


def get_eval() -> EvaluationHarness:
    global _eval_harness
    if _eval_harness is None:
        _eval_harness = EvaluationHarness(
            boolean_engine=get_boolean(),
            vsm_engine=get_vsm(),
            rocchio=get_rocchio(),
        )
    return _eval_harness


def get_divergence() -> DivergenceCalculator:
    global _divergence
    if _divergence is None:
        _divergence = DivergenceCalculator(get_vsm())
    return _divergence


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class BooleanQueryRequest(BaseModel):
    query: str
    """Boolean expression e.g. '(jackal OR fox) AND lion AND NOT tiger'"""
    filters: dict = {}


class VSMQueryRequest(BaseModel):
    query: str
    top_k: int = 10
    collection_filter: Optional[str] = None
    region_filter: Optional[str] = None
    zone_weights: dict = {"title": 0.35, "body": 0.65}


class NLQueryRequest(BaseModel):
    query: str
    """Free-text natural language query"""
    top_k: int = 10


class FeedbackRequest(BaseModel):
    query: str
    relevant_ids: list[str] = []
    non_relevant_ids: list[str] = []
    top_k: int = 10
    alpha: float = 1.0    # Rocchio α — original query weight
    beta: float = 0.75    # Rocchio β — relevant centroid weight
    gamma: float = 0.15   # Rocchio γ — non-relevant centroid weight


class EvaluateRequest(BaseModel):
    modes: list[str] = ["boolean", "vsm", "vsm_rocchio"]
    qrel_query_ids: Optional[list[str]] = None  # None = run all qrels


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "VaartaVerse Classical IR Engine",
        "corpus_size": get_index().doc_count(),
    }


@app.post("/search/boolean")
def search_boolean(req: BooleanQueryRequest):
    """
    Boolean retrieval using AND / OR / NOT with parenthesized expressions.
    Returns matching doc IDs and metadata (unranked set).
    """
    engine = get_boolean()
    results = engine.search(req.query, filters=req.filters)
    return {"mode": "boolean", "query": req.query, "results": results, "count": len(results)}


@app.post("/search/vsm")
def search_vsm(req: VSMQueryRequest):
    """
    Vector Space Model retrieval with TF-IDF weighting, sublinear TF scaling,
    zone/field weighting (title vs body), and cosine similarity top-K ranking.
    """
    engine = get_vsm()
    results = engine.search(
        query=req.query,
        top_k=req.top_k,
        zone_weights=req.zone_weights,
        collection_filter=req.collection_filter,
        region_filter=req.region_filter,
    )
    return {"mode": "vsm", "query": req.query, "results": results, "count": len(results)}


@app.post("/search/nl-query")
def search_nl_query(req: NLQueryRequest):
    """
    Rule-based natural language query parser.
    Extracts keywords, identifies known regions/traditions/tale-types,
    detects implicit boolean operators from phrase patterns,
    then dispatches to VSM or Boolean engine appropriately.
    """
    parser = get_nl_parser()
    parsed = parser.parse(req.query)
    if parsed["mode"] == "boolean":
        results = get_boolean().search(parsed["structured_query"])
    else:
        results = get_vsm().search(
            query=parsed["normalized_query"],
            top_k=req.top_k,
        )
    return {
        "mode": "nl_query",
        "original_query": req.query,
        "parsed": parsed,
        "results": results,
        "count": len(results),
    }


@app.post("/search/feedback")
def search_feedback(req: FeedbackRequest):
    """
    Rocchio relevance feedback — shifts query vector toward relevant document
    centroids and away from non-relevant ones, then re-retrieves top-K.

    Modified query: q_m = α·q₀ + β·(1/|Dr|)·Σd∈Dr - γ·(1/|Dnr|)·Σd∈Dnr
    """
    rocchio = get_rocchio()
    results = rocchio.rerank(
        query=req.query,
        relevant_ids=req.relevant_ids,
        non_relevant_ids=req.non_relevant_ids,
        top_k=req.top_k,
        alpha=req.alpha,
        beta=req.beta,
        gamma=req.gamma,
    )
    return {
        "mode": "vsm_rocchio",
        "original_query": req.query,
        "rocchio_params": {"alpha": req.alpha, "beta": req.beta, "gamma": req.gamma},
        "results": results,
        "count": len(results),
    }


@app.post("/evaluate")
def evaluate(req: EvaluateRequest):
    """
    Runs the evaluation harness against human-curated qrels.
    Computes Precision, Recall, F1 (unranked) and P@K, MAP, nDCG (ranked)
    for each requested retrieval mode.
    """
    harness = get_eval()
    report = harness.run(modes=req.modes, qrel_query_ids=req.qrel_query_ids)
    return report


@app.get("/tale-type/{tale_type_id}/variants")
def get_variants(tale_type_id: str):
    """
    Returns all indexed variants for a given tale_type_id from the inverted index metadata.
    """
    index = get_index()
    variants = index.get_variants_by_tale_type(tale_type_id)
    if not variants:
        raise HTTPException(status_code=404, detail=f"No variants found for tale type '{tale_type_id}'")
    return {"tale_type_id": tale_type_id, "variants": variants, "count": len(variants)}


@app.get("/tale-type/{tale_type_id}/divergence")
def get_divergence_route(tale_type_id: str):
    """
    Computes pairwise cosine similarity between all variants of a tale type
    using their TF-IDF document vectors. Returns the full similarity matrix
    plus per-pair vocabulary overlap and Jaccard similarity statistics.
    """
    calc = get_divergence()
    matrix = calc.compute_pairwise_matrix(tale_type_id)
    if matrix is None:
        raise HTTPException(status_code=404, detail=f"Cannot compute divergence — no variants for '{tale_type_id}'")
    return matrix


# ---------------------------------------------------------------------------
# Ingestion Endpoints — Phase 2
# ---------------------------------------------------------------------------

class IngestDocumentRequest(BaseModel):
    tale_id: str
    tale_type: str
    title: str
    region: str
    tradition: str
    source_collection: str
    translator: str = ""
    collection_era: str = ""
    raw_text: str


class IngestRebuildRequest(BaseModel):
    source: str = "json"  # "json" | "mongodb" | "both"
    corpus_path: Optional[str] = None


@app.post("/ingest/document")
def ingest_document(req: IngestDocumentRequest):
    """
    Add a single tale variant to the live inverted index.
    The index is updated in memory and persisted to disk immediately.
    """
    index = get_index()
    # Reset downstream singletons so they pick up the new doc
    global _vsm_engine, _boolean_engine, _rocchio, _divergence, _eval_harness
    _vsm_engine = _boolean_engine = _rocchio = _divergence = _eval_harness = None

    pipeline = IngestionPipeline(index)
    success = pipeline.ingest_document(req.model_dump())
    if not success:
        raise HTTPException(status_code=422, detail=f"Ingestion failed: {pipeline.stats['errors']}")

    pipeline.save_index()
    return {
        "status": "ingested",
        "tale_id": req.tale_id,
        "corpus_size": index.doc_count(),
        "vocabulary_size": len(index.vocabulary()),
    }


@app.post("/ingest/rebuild")
def ingest_rebuild(req: IngestRebuildRequest):
    """
    Rebuild the entire inverted index from scratch.
    Sources: 'json' (seed file), 'mongodb', or 'both'.
    Resets all engine singletons after rebuild.
    """
    global _index, _vsm_engine, _boolean_engine, _rocchio, _divergence, _eval_harness, _nl_parser
    # Clear all singletons
    _index = InvertedIndex()
    _vsm_engine = _boolean_engine = _rocchio = _divergence = _eval_harness = None

    pipeline = IngestionPipeline(_index)

    if req.source == "mongodb":
        stats = pipeline.ingest_from_mongodb()
    elif req.source == "both":
        stats = pipeline.ingest_from_json(req.corpus_path)
        stats2 = pipeline.ingest_from_mongodb()
        stats["documents_ingested"] += stats2["documents_ingested"]
        stats["errors"].extend(stats2["errors"])
    else:  # default: json
        stats = pipeline.ingest_from_json(req.corpus_path)

    if stats["documents_ingested"] > 0:
        pipeline.save_index()

    return {
        "status": "rebuilt",
        "source": req.source,
        "documents_ingested": stats["documents_ingested"],
        "terms_indexed": stats["terms_indexed"],
        "skipped": stats["skipped"],
        "errors": stats["errors"][:10],  # cap error list
    }


@app.get("/ingest/status")
def ingest_status():
    """
    Returns current index statistics without triggering a build.
    """
    index = get_index()
    return {
        "corpus_size": index.doc_count(),
        "vocabulary_size": len(index.vocabulary()),
        "tale_types": list({
            m.tale_type for m in index._docs.values()
        }),
        "traditions": list({
            m.tradition for m in index._docs.values()
        }),
        "regions": list({
            m.region for m in index._docs.values()
        }),
    }
