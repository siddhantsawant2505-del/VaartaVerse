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
| `preprocessing.py` | Tokenization, stopword removal, NLTK WordNet Lemmatization (`pos='n'` + `pos='v'`). |
| `inverted_index.py` | Multi-zone postings lists (`title`, `tradition`, `region`, `body`), term frequencies, position offsets. |
| `boolean_engine.py` | Evaluates boolean expressions (`AND`, `OR`, `NOT`, brackets) using AST trees. |
| `vsm_engine.py` | Computes TF-IDF ($1 + \log tf$) and smooth IDF ($\log(N/df)$), field boosting, cosine scoring. |
| `relevance_feedback.py` | Implements Rocchio query vector reformulation equation for explicit feedback and PRF. |
| `nl_parser.py` | Rule-based parser mapping NL queries to structured VSM/Boolean search parameters. |
| `divergence.py` | Calculates pairwise divergence matrices, Jaccard distance, and vocabulary overlap across variants. |
| `evaluation.py` | Computes P@K, Recall, MAP, nDCG@K, and F1 metrics against ground-truth `qrels`. |
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
