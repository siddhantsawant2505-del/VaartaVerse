# VaartaVerse — Classical IR Engine (FastAPI Microservice)

The `ir_engine` is a pure mathematical retrieval, query processing, feedback, evaluation, and divergence engine built with FastAPI and Python.

---

## Directory Structure

```
ir_engine/
├── app/
│   ├── main.py                   # FastAPI app entry point & endpoint routes
│   └── core/
│       ├── preprocessing.py      # Tokenizer, stopword filter, WordNet Lemmatizer
│       ├── inverted_index.py     # Multi-zone postings list manager & disk persistence
│       ├── boolean_engine.py     # Recursive-descent AST parser for Boolean logic
│       ├── vsm_engine.py         # Sublinear TF-IDF VSM scoring & cosine similarity
│       ├── relevance_feedback.py # Rocchio feedback & PRF query expansion
│       ├── nl_parser.py          # Rule-based natural language entity/tradition extractor
│       ├── divergence.py         # Pairwise cosine divergence matrix & Jaccard overlap
│       ├── evaluation.py         # Precision@K, MAP, nDCG@K evaluation harness
│       └── ingestion.py          # Seed JSON corpus loader & index builder
├── data/
│   ├── corpus/                   # Raw & seed folk tale JSON datasets
│   └── index/                    # Persisted inverted index (doc_registry.json, postings.json)
└── requirements.txt
```

---

## Key Modules & Responsibilities

| Module | Core Functionality |
|---|---|
| `preprocessing.py` | Tokenization (possessive-stripping), stopword removal, NLTK WordNet Lemmatization (`pos='n'` + `pos='v'`). |
| `inverted_index.py` | Multi-zone postings lists (`title`, `body`), term frequencies, position offsets, corpus fingerprint staleness detection. |
| `boolean_engine.py` | Recursive-descent boolean evaluation with **NOT > AND > OR precedence**, implicit AND, juxtaposed NOT, tf-idf ranking, precise parse errors. |
| `vsm_engine.py` | TF-IDF ($1 + \log tf$) with always-positive IDF ($\log(1 + N/df)$), title/body boost multipliers, full-vector-norm cosine scoring. |
| `bm25_engine.py` | Okapi BM25 with saturating TF ($k_1$), length normalization ($b$), and title-zone boost. |
| `relevance_feedback.py` | Rocchio query reformulation for explicit feedback and PRF, single-pass postings re-ranking. |
| `nl_parser.py` | Rule-based parser mapping NL queries to structured VSM/Boolean search parameters. |
| `divergence.py` | Calculates pairwise divergence matrices, Jaccard similarity, and vocabulary overlap across variants. |
| `evaluation.py` | P@K, Recall, per-query F1, MAP, nDCG@K against injectable `qrels` across boolean/vsm/bm25/vsm_rocchio modes. |
| `ingestion.py` | Processes text documents and constructs the inverted index on disk. |

---

## Running the IR Engine

```bash
cd ir_engine
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

FastAPI interactive documentation will be available at **http://localhost:8000/docs**.

## Tests

```bash
python -m pytest tests/ -v
```

The suite covers tokenization/possessives, boolean precedence and error handling, VSM zone weighting and idf edge cases, BM25 behavior, metric formulas (hand-computed expectations), index persistence/fingerprints, and the FastAPI surface (including HTTP 422 parse errors).
