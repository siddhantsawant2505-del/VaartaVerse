# VaartaVerse — Metadata & Proxy Server (Express & MongoDB)

The Node.js server acts as the central data management tier and search proxy service for VaartaVerse.

---

## Directory Structure

```
server/
├── config/
│   └── db.js         # Mongoose MongoDB connection configuration
├── models/
│   ├── TaleVariant.js # Mongoose schema for folk tale variant documents
│   ├── TaleType.js    # Mongoose schema for canonical ATU tale types
│   ├── Qrel.js        # Mongoose schema for benchmark evaluation ground-truth
│   └── QueryLog.js    # Mongoose schema for search session logging
├── routes/
│   ├── tales.js       # CRUD endpoints for tale metadata and raw texts
│   ├── taleTypes.js   # Endpoints for canonical tale types and variant groupings
│   ├── qrels.js       # Endpoints for reading and writing benchmark judgments
│   ├── ingest.js      # Endpoint for corpus ingestion into MongoDB
│   └── irProxy.js     # Logged proxy route connecting Next.js client to Python IR Engine
└── server.js          # Express app entry point (Port 5000)
```

---

## API Routes Overview

| Route File | Base Path | Description |
|---|---|---|
| `tales.js` | `/api/tales` | List variants, fetch raw tale text by ID, filter by region/tradition. |
| `taleTypes.js` | `/api/tale-types` | List canonical ATU tale types and retrieve variants under a type. |
| `qrels.js` | `/api/qrels` | Store and query benchmark ground-truth relevance judgments. |
| `ingest.js` | `/api/ingest` | Batch ingest new folk tales into MongoDB. |
| `irProxy.js` | `/api/ir/search/*` | Proxies search requests to Python FastAPI while logging query metrics to MongoDB. |

---

## Running the Server

```bash
cd server
npm install
# Set MONGO_URI in .env if needed (default: mongodb://localhost:27017/vaartaverse)
npm run dev
```

The Express server will start on **http://localhost:5000**.
