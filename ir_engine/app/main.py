"""
VaartaVerse Classical IR Engine — FastAPI Entry Point
Implements all retrieval, feedback, evaluation, and divergence endpoints.
No LLMs, no external vector databases — pure hand-crafted IR math.

Error policy: malformed boolean queries and stopword-only queries return
HTTP 422 with the parser's message — no silent fallbacks, no invented results.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Optional

from app.core.inverted_index import InvertedIndex, corpus_fingerprint
from app.core.boolean_engine import BooleanEngine, BooleanParseError
from app.core.vsm_engine import VSMEngine
from app.core.bm25_engine import BM25Engine
from app.core.relevance_feedback import RocchioFeedback
from app.core.nl_parser import NLQueryParser
from app.core.evaluation import EvaluationHarness
from app.core.divergence import DivergenceCalculator
from app.core.ingestion import IngestionPipeline
from app.core.preprocessing import preprocess
from app.core.spelling import correct_terms

app = FastAPI(
    title="VaartaVerse Classical IR Engine",
    description=(
        "Hand-crafted Information Retrieval engine for cross-regional Indian folk tale lineage. "
        "Implements inverted index, Boolean retrieval (NOT > AND > OR), TF-IDF VSM with real "
        "zone weighting, BM25, Rocchio feedback (explicit + PRF), rule-based NL query parsing, "
        "MAP/nDCG evaluation, and pairwise cosine divergence. No LLMs or external vector DBs."
    ),
    version="0.2.0",
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
_bm25_engine: Optional[BM25Engine] = None
_rocchio: Optional[RocchioFeedback] = None
_nl_parser: Optional[NLQueryParser] = None
_eval_harness: Optional[EvaluationHarness] = None
_divergence: Optional[DivergenceCalculator] = None


def _build_index_from_corpus(index: InvertedIndex) -> None:
    pipeline = IngestionPipeline(index)
    stats = pipeline.ingest_from_json()
    if stats["documents_ingested"] > 0:
        pipeline.save_index()
        print(f"[VaartaVerse] Index built: {stats['documents_ingested']} docs, "
              f"{stats['terms_indexed']} terms.")
    else:
        print("[VaartaVerse] Seed corpus empty or not found. Index will be empty.")


def get_index() -> InvertedIndex:
    global _index
    if _index is None:
        _index = InvertedIndex()
        if not _index.load():
            print("[VaartaVerse] No valid persisted index — auto-building from seed corpus...")
            _build_index_from_corpus(_index)
    return _index


def reset_engines() -> None:
    """Drop all engine singletons (after ingestion/rebuild) so they rebuild on next use."""
    global _vsm_engine, _boolean_engine, _bm25_engine, _rocchio, _divergence, _eval_harness
    _vsm_engine = _boolean_engine = _bm25_engine = _rocchio = _divergence = _eval_harness = None


def get_vsm() -> VSMEngine:
    global _vsm_engine
    if _vsm_engine is None:
        _vsm_engine = VSMEngine(get_index())
    return _vsm_engine


def get_bm25() -> BM25Engine:
    global _bm25_engine
    if _bm25_engine is None:
        _bm25_engine = BM25Engine(get_index())
    return _bm25_engine


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
            bm25_engine=get_bm25(),
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
    auto_correct: bool = False
    """Correct unknown query terms against the vocabulary (edit distance ≤ 2)."""

    @field_validator("zone_weights")
    @classmethod
    def _check_weights(cls, v: dict) -> dict:
        for key in ("title", "body"):
            w = v.get(key)
            if not isinstance(w, (int, float)) or w < 0:
                raise ValueError(f"zone weight '{key}' must be a non-negative number")
        return v


class BM25QueryRequest(BaseModel):
    query: str
    top_k: int = 10
    k1: Optional[float] = None
    b: Optional[float] = None
    title_boost: float = 1.5
    collection_filter: Optional[str] = None
    region_filter: Optional[str] = None
    auto_correct: bool = False
    """Correct unknown query terms against the vocabulary (edit distance ≤ 2)."""


class NLQueryRequest(BaseModel):
    query: str
    """Free-text natural language query"""
    top_k: int = 10
    expand_synonyms: bool = False
    """WordNet synonym expansion — synonyms weighted below original terms."""
    expansion_weight: float = 0.3
    """Weight multiplier for synonym terms (0 < w ≤ 1)."""
    max_expansions: int = 3
    """Max synonyms per query term."""
    auto_correct: bool = False
    """Correct unknown query terms against the vocabulary (edit distance ≤ 2)."""


class FeedbackRequest(BaseModel):
    query: str
    relevant_ids: list[str] = []
    non_relevant_ids: list[str] = []
    top_k: int = 10
    alpha: float = 1.0    # Rocchio α — original query weight
    beta: float = 0.75    # Rocchio β — relevant centroid weight
    gamma: float = 0.15   # Rocchio γ — non-relevant centroid weight


class PRFRequest(BaseModel):
    query: str
    top_k: int = 10
    prf_k: int = 3
    beta: float = 0.75


class EvaluateRequest(BaseModel):
    modes: list[str] = ["boolean", "vsm", "bm25", "vsm_rocchio"]
    qrel_query_ids: Optional[list[str]] = None  # None = run all qrels
    qrels_path: Optional[str] = None            # optional qrels JSON file


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    index = get_index()
    corpus_path = Path(__import__("os").getenv("CORPUS_PATH", "./data/corpus/tales.json"))
    current_fp = corpus_fingerprint(corpus_path)
    return {
        "status": "ok",
        "service": "VaartaVerse Classical IR Engine",
        "version": app.version,
        "corpus_size": index.doc_count(),
        "vocabulary_size": len(index.vocabulary()),
        "index_stale": bool(current_fp) and current_fp != (
            Path("data/index/corpus_fingerprint.json").read_text(encoding="utf-8").strip()
            if Path("data/index/corpus_fingerprint.json").exists() else None
        ),
    }


@app.post("/search/boolean")
def search_boolean(req: BooleanQueryRequest):
    """
    Boolean retrieval with standard precedence (NOT > AND > OR), implicit AND
    via juxtaposition, and tf-idf ranking of the matching set.
    Malformed queries return HTTP 422 with the parse error.
    """
    try:
        results = get_boolean().search(req.query, filters=req.filters)
    except BooleanParseError as e:
        raise HTTPException(
            status_code=422,
            detail={"error": "boolean_parse_error", "message": str(e)},
        )
    return {"mode": "boolean", "query": req.query, "results": results, "count": len(results)}


def _apply_corrections(terms: list[str], enabled: bool) -> tuple[list[str], dict[str, str], str]:
    """
    Vocabulary-based typo correction for query terms.

    Returns (corrected_terms, corrections_map, corrected_query). When disabled
    or nothing needs correcting, returns the original terms unchanged.
    """
    if not enabled or not terms:
        return terms, {}, ""
    vocab = get_index().vocabulary()
    missing = [t for t in terms if t not in vocab]
    if not missing:
        return terms, {}, ""
    corrections = correct_terms(missing, vocab)
    if not corrections:
        return terms, {}, ""
    corrected = [corrections.get(t, t) for t in terms]
    return corrected, corrections, " ".join(corrected)


@app.post("/search/vsm")
def search_vsm(req: VSMQueryRequest):
    """
    Vector Space Model retrieval: TF-IDF with always-positive smoothed idf,
    real zone weighting (full-document norms), cosine similarity top-K ranking.
    With auto_correct, unknown query terms are matched to the closest vocabulary
    term (edit distance ≤ 2) and reported in `corrections` / `corrected_query`.
    """
    engine = get_vsm()
    terms = preprocess(req.query)
    corrected_terms, corrections, corrected_query = _apply_corrections(terms, req.auto_correct)
    query_used = corrected_query or req.query

    results = engine.search(
        query=query_used,
        top_k=req.top_k,
        zone_weights=req.zone_weights,
        collection_filter=req.collection_filter,
        region_filter=req.region_filter,
    )
    return {
        "mode": "vsm",
        "query": req.query,
        "query_changed": bool(corrections),
        "corrections": corrections,
        "corrected_query": corrected_query or None,
        "results": results,
        "count": len(results),
    }


@app.post("/search/bm25")
def search_bm25(req: BM25QueryRequest):
    """
    Okapi BM25 ranking: saturating TF, document-length normalization, and a
    title-zone boost. The classical baseline against the VSM.
    """
    engine = get_bm25()
    terms = preprocess(req.query)
    corrected_terms, corrections, corrected_query = _apply_corrections(terms, req.auto_correct)
    query_used = corrected_query or req.query

    results = engine.search(
        query=query_used,
        top_k=req.top_k,
        k1=req.k1,
        b=req.b,
        title_boost=req.title_boost,
        collection_filter=req.collection_filter,
        region_filter=req.region_filter,
    )
    return {
        "mode": "bm25",
        "query": req.query,
        "query_changed": bool(corrections),
        "corrections": corrections,
        "corrected_query": corrected_query or None,
        "results": results,
        "count": len(results),
    }


def _vsm_search_with_filters(parsed: dict, req: NLQueryRequest) -> list[dict]:
    filters = parsed.get("filters", {})
    # Precompute WordNet expansions against the index vocabulary
    expansion_weights: dict[str, float] = {}
    if req.expand_synonyms and parsed.get("expansions"):
        vocab = get_index().vocabulary()
        w = min(max(req.expansion_weight, 0.0), 1.0)
        for term in parsed["expanded_terms"]:
            if term in vocab:
                expansion_weights[term] = w
    return get_vsm().search(
        query=parsed["normalized_query"] or req.query,
        top_k=req.top_k,
        collection_filter=filters.get("tradition"),
        region_filter=filters.get("region"),
        expansion_weights=expansion_weights or None,
    )


@app.post("/search/nl-query")
def search_nl_query(req: NLQueryRequest):
    """
    Rule-based natural language query parser.
    Extracts keywords and known regions/traditions/tale-types, detects boolean
    structure, then dispatches to the appropriate engine. If a parsed boolean
    query matches nothing, falls back to ranked VSM (and reports it in `mode`).
    """
    parser = get_nl_parser()
    parsed = parser.parse(
        req.query,
        expand_synonyms=req.expand_synonyms,
        vocabulary=get_index().vocabulary() if req.expand_synonyms else None,
    )
    fallback_used = False

    # Typo correction (VSM mode only — boolean semantics must stay exact)
    corrections: dict[str, str] = {}
    corrected_query = ""
    if req.auto_correct and parsed["mode"] != "boolean":
        corrected_terms, corrections, corrected_query = _apply_corrections(
            parsed["stemmed_terms"], req.auto_correct
        )
        if corrections:
            parsed["corrections"] = corrections
            parsed["normalized_query"] = corrected_query
            # Re-map expansion structures onto the corrected terms
            old2new = corrections
            parsed["expanded_terms"] = [old2new.get(t, t) for t in parsed.get("expanded_terms", [])]
            parsed["expansions"] = {
                old2new.get(k, k): v for k, v in parsed.get("expansions", {}).items()
            }
    if parsed["mode"] == "boolean":
        try:
            results = get_boolean().search(parsed["structured_query"])
        except BooleanParseError:
            results = []
        if not results:
            results = _vsm_search_with_filters(parsed, req)
            fallback_used = True
    else:
        results = _vsm_search_with_filters(parsed, req)
    return {
        "mode": "vsm_fallback" if fallback_used else "nl_query",
        "original_query": req.query,
        "query_changed": bool(corrections),
        "corrections": corrections,
        "corrected_query": corrected_query or None,
        "parsed": parsed,
        "synonyms_applied": sorted(parsed.get("expanded_terms", [])),
        "results": results,
        "count": len(results),
    }


@app.post("/search/feedback")
def search_feedback(req: FeedbackRequest):
    """
    Rocchio relevance feedback — shifts the query vector toward relevant
    document centroids and away from non-relevant ones, then re-ranks top-K.
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


@app.post("/search/prf")
def search_prf(req: PRFRequest):
    """
    Pseudo-Relevance Feedback (blind feedback): assumes the top prf_k VSM
    results are relevant and applies Rocchio expansion. No user input needed.
    """
    results = get_rocchio().pseudo_relevance_feedback(
        query=req.query,
        top_k=req.top_k,
        prf_k=req.prf_k,
        beta=req.beta,
    )
    return {
        "mode": "vsm_prf",
        "original_query": req.query,
        "prf_params": {"prf_k": req.prf_k, "beta": req.beta},
        "results": results,
        "count": len(results),
    }


@app.post("/evaluate")
def evaluate(req: EvaluateRequest):
    """
    Runs the evaluation harness against qrels. Computes per-query and mean
    Precision, Recall, F1, P@K, MAP, nDCG for each requested retrieval mode.
    """
    try:
        harness = get_eval()
        report = harness.run(
            modes=req.modes,
            qrel_query_ids=req.qrel_query_ids,
            qrels_path=req.qrels_path,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"qrels file not found: {e}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return report


@app.get("/tale-types")
def list_tale_types():
    """Distinct tale types in the index with variant counts (the registry)."""
    return {"tale_types": get_index().all_tale_types()}


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
# Ingestion Endpoints
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
    reset_engines()

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
    global _index
    reset_engines()
    _index = InvertedIndex()

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
        "tale_types": list({m.tale_type for m in index._docs.values()}),
        "traditions": list({m.tradition for m in index._docs.values()}),
        "regions": list({m.region for m in index._docs.values()}),
    }
