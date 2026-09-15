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
| **`ir_engine`** | 8000 | Python 3.11, FastAPI, NLTK, NumPy | Inverted Index, Boolean AST parser, TF-IDF VSM, Rocchio Feedback, Divergence, Evaluation |

---

## Detailed Component Documentation

### 1. IR Engine Microservice (`ir_engine/`)

The `ir_engine` is built with FastAPI and runs pure mathematical retrieval routines without external AI dependencies.

#### Core Algorithmic Modules (`ir_engine/app/core/`)

* **`preprocessing.py`**: Text normalization pipeline.
  * Lowers case and splits hyphenated words.
  * Filters standard English stopwords + domain-specific terms (*"said"*, *"king"*, *"day"*, etc.).
  * Applies **NLTK WordNet Lemmatizer** (noun `pos='n'` and verb `pos='v'` passes) to extract canonical dictionary roots (e.g., `"jackals"` → `"jackal"`, `"running"` → `"run"`).
* **`inverted_index.py`**: Multi-zone posting list manager.
  * Stores term frequencies ($tf$), document IDs, token positions, and field zones (`title`, `tradition`, `region`, `body`).
  * Persists index structures on disk as JSON (`doc_registry.json`, `postings.json`).
* **`boolean_engine.py`**: Exact Boolean search parser.
  * Recursive-descent AST parser supporting `AND`, `OR`, `NOT`, and parenthesized nested logic.
  * Evaluates set operations over postings list document IDs.
* **`vsm_engine.py`**: Vector Space Model ranking engine.
  * Calculates sublinear term frequency: $w_{t,d} = 1 + \log(tf_{t,d})$ if $tf > 0$, else $0$.
  * Calculates smoothed inverse document frequency: $idf_t = \log(N / df_t)$.
  * Applies field zone weighting (e.g., title boost factor) and cosine similarity vector normalization.
  * Performs top-$K$ document retrieval using min-heap priority queues.
* **`relevance_feedback.py`**: Query expansion and re-ranking via Rocchio algorithm.
  * Refines search query vectors based on user-provided relevance judgments ($D_r$ vs $D_{nr}$):
    $$\vec{q}_{new} = \alpha \vec{q}_0 + \frac{\beta}{|D_r|} \sum_{\vec{d} \in D_r} \vec{d} - \frac{\gamma}{|D_{nr}|} \sum_{\vec{d} \in D_{nr}} \vec{d}$$
  * Supports both explicit feedback and Pseudo-Relevance Feedback (PRF).
* **`nl_parser.py`**: Rule-based natural language parser.
  * Extracts named entities, traditions (*Panchatantra*, *Jataka*, *Hitopadesha*), and geographic regions from free-text inputs to automatically build structured search parameters.
* **`divergence.py`**: Cross-regional textual evolution metrics.
  * Computes pairwise cosine similarity matrices across variants of the same ATU tale type.
  * Measures Jaccard coefficients and vocabulary overlap ratios to quantify narrative divergence.
* **`evaluation.py`**: Benchmark quality evaluator.
  * Benchmarks search queries against curated relevance judgment benchmark sets (`qrels`).
  * Computes **Precision@K**, **Recall**, **Mean Average Precision (MAP)**, **nDCG@K**, and **F1 Score**.
* **`ingestion.py`**: Corpus ingestion pipeline.
  * Ingests JSON document collections, executes preprocessing, and builds the inverted index.

#### API Endpoints (`ir_engine/app/main.py`)
* `GET /health`: Service health and index statistics.
* `POST /search/vsm`: TF-IDF VSM vector ranking.
* `POST /search/boolean`: Recursive Boolean search.
* `POST /search/nl-query`: NL query parsing + search routing.
* `POST /search/feedback`: Rocchio relevance feedback re-ranking.
* `POST /evaluate`: Full dataset benchmark evaluation.
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
  * Interactive search interface supporting VSM, Boolean, and NL search tabs.
  * Allows tuning field weight boosts and executing Rocchio relevance feedback re-ranking by toggling document relevance.
* **`/tale-types` (Tale Types & Lineage Browser)** (`client/src/app/tale-types/page.tsx`):
  * Browse canonical ATU tale classifications, view core motifs, and list regional variants across traditions (*Panchatantra*, *Jataka*, etc.).
* **`/divergence` (Comparative Divergence Matrix)** (`client/src/app/divergence/page.tsx`):
  * Renders pairwise cosine similarity heatmaps, Jaccard distance, and vocabulary overlap matrices to visualize story evolution across regions.
* **`/evaluation` (IR Benchmark & Evaluation Dashboard)** (`client/src/app/evaluation/page.tsx`):
  * Evaluation runner that executes benchmark queries against `qrels` and displays Precision@K, Recall, MAP, and nDCG@K metrics in real time.

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
