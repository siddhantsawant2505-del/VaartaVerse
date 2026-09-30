# VaartaVerse — Classical Information Retrieval for Indian Folk Tale Lineage

> A hand-crafted IR system — **no LLMs, no RAG, no external vector databases, no dense neural embeddings** — that indexes, searches, evaluates, and quantifies cross-regional divergence across Indian folk tale collections (*Panchatantra*, *Jataka*, *Hitopadesha*, *Vikramaditya*, *Birbal*, *Tenali Raman*, and *Puranic* traditions).

---

## Architecture Overview

VaartaVerse is structured into three micro-services:

```
VaartaVerse/
├── client/          # Next.js 14 Web UI (Search, Lineage Browser, Divergence, Evaluation Dashboard)
├── server/          # Express + MongoDB Metadata & Proxy Service (Port 5000)
├── ir_engine/       # Python FastAPI Classical IR Engine (Port 8000)
└── README.md
```

| Service | Port | Tech Stack | Purpose |
|---|---|---|---|
| **`client`** | 3000 | Next.js 14, TypeScript, Tailwind CSS | Web UI: Search, Lineage Explorer, Divergence Matrix, Benchmark Dashboard |
| **`server`** | 5000 | Node.js, Express, Mongoose, MongoDB | Tale metadata storage, Tale-type registry, Qrel benchmark judgments, Search logging |
| **`ir_engine`** | 8000 | Python 3.12, FastAPI, NLTK, NumPy | Inverted Index, Boolean parser (NOT > AND > OR), TF-IDF VSM, BM25, Rocchio Feedback + PRF, Divergence, Evaluation |

---

## Detailed Component Documentation

### 1. IR Engine Microservice (`ir_engine/`)

The `ir_engine` is built with FastAPI and runs pure mathematical retrieval routines without external AI dependencies.

#### Core Algorithmic Modules (`ir_engine/app/core/`)

* **`preprocessing.py`**: Text normalization pipeline.
  * Lowers case, strips possessives (`"lion's"` → `"lion"`), and splits hyphenated words.
  * Filters standard English stopwords + a small list of true discourse fillers (*"said"*, *"thus"*, …) — content words like *"king"* or *"well"* are deliberately kept searchable.
  * Applies **NLTK WordNet Lemmatizer** (noun `pos='n'` and verb `pos='v'` passes) to extract canonical dictionary roots (e.g., `"jackals"` → `"jackal"`, `"running"` → `"run"`).
* **`inverted_index.py`**: Multi-zone posting list manager.
  * Stores term frequencies ($tf$), document IDs, token positions, and field zones (`title`, `body`).
  * Persists index structures on disk as JSON (`doc_registry.json`, `postings.json`) with a **corpus fingerprint** — a stale index (corpus changed since last build) is detected and rebuilt automatically.
* **`boolean_engine.py`**: Exact Boolean search parser.
  * Recursive-descent parser with standard precedence (**NOT > AND > OR**), parenthesized nested logic, implicit AND via juxtaposition (`"jackal tiger"`), and juxtaposed NOT (`"jackal NOT tiger"`).
  * Evaluates set operations over postings list document IDs, then **ranks the matching set by summed TF-IDF**.
  * Malformed queries raise a precise parse error → the API returns **HTTP 422**; there are no silent fallbacks that invent results.
* **`vsm_engine.py`**: Vector Space Model ranking engine.
  * Calculates sublinear term frequency: $w_{t,d} = 1 + \log(tf_{t,d})$ if $tf > 0$, else $0$.
  * Calculates always-positive smoothed idf: $idf_t = \log(1 + N / df_t)$.
  * Applies field zone weighting with **boost multipliers** (default title $2\times$ body $1\times$) and computes document norms over the **full document vector**, so a title match genuinely outranks a body match after cosine normalization.
  * Performs top-$K$ document retrieval using heap-based selection.
* **`bm25_engine.py`**: Okapi BM25 ranking — saturating TF ($k_1$), document-length normalization ($b$), always-positive BM25 idf, and a configurable title-zone boost. The classical baseline against the VSM.
* **`relevance_feedback.py`**: Query expansion and re-ranking via Rocchio algorithm.
  * Refines search query vectors based on user-provided relevance judgments ($D_r$ vs $D_{nr}$):
    $$\vec{q}_{new} = \alpha \vec{q}_0 + \frac{\beta}{|D_r|} \sum_{\vec{d} \in D_r} \vec{d} - \frac{\gamma}{|D_{nr}|} \sum_{\vec{d} \in D_{nr}} \vec{d}$$
  * Uses the same always-positive idf scheme as the VSM, clips negative weights, and re-ranks via a single postings traversal.
  * Supports both explicit feedback and **Pseudo-Relevance Feedback (PRF)** — exposed at `POST /search/prf`.
* **`nl_parser.py`**: Rule-based natural language parser.
  * Extracts named entities, traditions (*Panchatantra*, *Jataka*, *Hitopadesha*), and geographic regions from free-text inputs to automatically build structured search parameters.
* **`divergence.py`**: Cross-regional textual evolution metrics.
  * Computes pairwise cosine similarity matrices across variants of the same ATU tale type.
  * Measures Jaccard coefficients and vocabulary overlap ratios to quantify narrative divergence.
* **`evaluation.py`**: Benchmark quality evaluator.
  * Benchmarks **boolean / vsm / bm25 / vsm_rocchio** retrieval modes against relevance judgments (`qrels`), injectable via constructor or a JSON file.
  * Computes **Precision@K**, **Recall**, **per-query F1**, **Mean Average Precision (MAP)**, and **nDCG@K**; judgments referencing tale IDs missing from the corpus are filtered and counted.
  * **Honesty notes:** the bundled stub qrels are author-judged over a small corpus (illustrative, not a benchmark), and boolean results are ranked post-hoc by TF-IDF — unranked boolean matching against ranked metrics will (correctly) look poor.
  * The test suite (`tests/`, pytest) covers tokenization, boolean precedence, VSM/BM25 behavior, metric formulas, and the API surface.
* **`ingestion.py`**: Corpus ingestion pipeline.
  * Ingests JSON document collections, executes preprocessing, and builds the inverted index.

#### API Endpoints (`ir_engine/app/main.py`)
* `GET /health`: Service health, index statistics, and index-staleness flag.
* `POST /search/vsm`: TF-IDF VSM vector ranking with zone weighting.
* `POST /search/bm25`: Okapi BM25 ranking (k1 / b / title_boost configurable).
* `POST /search/boolean`: Boolean search (NOT > AND > OR); malformed queries → HTTP 422 with the parse error.
* `POST /search/nl-query`: NL query parsing + search routing (falls back to ranked VSM when a parsed boolean query matches nothing, and reports it). Accepts `expand_synonyms` (bool, default false), `expansion_weight` (default 0.3), and `max_expansions` (default 3); applied synonyms are reported in `synonyms_applied` and per-result `expansions_matched`.
* `POST /search/feedback`: Rocchio explicit relevance feedback re-ranking.
* `POST /search/prf`: Pseudo-Relevance Feedback (blind feedback) via Rocchio.
* `POST /evaluate`: Benchmark evaluation across retrieval modes with injectable qrels.
* `GET /tale-types`: Tale-type registry with variant counts.
* `GET /tale-type/{id}/divergence`: Pairwise divergence matrix computation.

---

### 2. Express Metadata & Proxy Server (`server/`)

The Node.js server acts as the data repository and API proxy.

#### Mongoose Schemas (`server/models/`)
* **`TaleVariant.js`**: Per-tale record storing `tale_id`, `tale_type`, `title`, `region`, `tradition`, `source_collection`, `translator`, and `raw_text`.
* **`TaleType.js`**: Canonical tale registry storing `atu_code`, `canonical_title`, key motifs, and lineage metadata.
* **`Qrel.js`**: Ground-truth benchmark evaluation dataset storing `query_id`, `query_text`, and document relevance scores (0 to 3).
* **`QueryLog.js`**: Search history log storing `query_text`, `mode`, execution time in ms, and user interaction feedback.

#### Express Routes (`server/routes/`)
* **`tales.js`**: REST CRUD endpoints (`/api/tales`) for viewing and searching metadata.
* **`taleTypes.js`**: Endpoints (`/api/tale-types`) to query canonical tale groupings.
* **`qrels.js`**: Endpoints (`/api/qrels`) to manage ground-truth benchmark judgments.
* **`ingest.js`**: Handles text corpus ingestion into MongoDB and index triggers.
* **`irProxy.js`**: Proxies search calls from Next.js UI to FastAPI engine while logging session metrics to MongoDB.

---

### 3. Client UI Pages (`client/src/app/`)

Next.js 14 frontend pages designed for research and comparative analysis:

* **`/` (Search & IR Workbench)** (`client/src/app/page.tsx`):
  * Interactive search interface supporting Smart (NL/VSM), **BM25**, and Boolean search modes.
  * Boolean parse errors (HTTP 422) are surfaced with the engine's exact message.
  * Executes Rocchio relevance feedback re-ranking by toggling document relevance.
  * All requests flow through the Express proxy (`:5000/api/ir`), which logs query metrics to MongoDB.
* **`/tale-types` (Tale Types & Lineage Browser)** (`client/src/app/tale-types/page.tsx`):
  * Browse canonical ATU tale classifications, view core motifs, and list regional variants across traditions (*Panchatantra*, *Jataka*, etc.).
* **`/divergence` (Comparative Divergence Matrix)** (`client/src/app/divergence/page.tsx`):
  * Renders **live** pairwise cosine similarity heatmaps, Jaccard similarity, and vocabulary overlap matrices fetched from the engine's `/tale-type/{id}/divergence` endpoint, with the tale-type registry loaded from `/tale-types`.
* **`/evaluation` (IR Benchmark & Evaluation Dashboard)** (`client/src/app/evaluation/page.tsx`):
  * Evaluation runner that executes the benchmark against `qrels` and displays MAP, nDCG@10, P@5/P@10, Recall, and per-query F1 for Boolean, VSM, BM25, and Rocchio-PRF modes.

---

## Setup & Quick Start

### Prerequisites
- **Node.js**: $\ge 18$
- **Python**: $\ge 3.11$
- **MongoDB**: Running locally on port `27017`

### 1. Launch Python IR Engine (Port 8000)
```bash
cd ir_engine
python -m venv .venv
# Activate environment (Windows PowerShell):
.\.venv\Scripts\Activate.ps1
# Install dependencies:
pip install -r requirements.txt
# Run FastAPI server:
uvicorn app.main:app --reload --port 8000
```

### 2. Launch Express Metadata Server (Port 5000)
```bash
cd server
npm install
npm run dev
```

### 3. Launch Next.js UI Client (Port 3000)
```bash
cd client
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.

---

## Scope Constraints (By Design)

* ❌ **No LLMs** (No GPT, Gemini, Claude, or local generative models in retrieval)
* ❌ **No RAG** (No retrieval-augmented text generation)
* ❌ **No External Vector DBs** (No Pinecone, Qdrant, Chroma, Weaviate)
* ❌ **No Neural Embeddings** (No sentence-transformers, no OpenAI embeddings)
* ✅ **Pure Classical IR Math**: Multi-zone postings lists, WordNet Lemmatization, TF-IDF VSM, Rocchio Feedback, AST Boolean logic, Pairwise Cosine Divergence, MAP & nDCG evaluation.

---

*VaartaVerse — where stories diverge, and the math measures how far.*
