# VaartaVerse — Next.js 14 Frontend Web Client

The `client` directory houses the Next.js 14 web interface built with React, TypeScript, and Tailwind CSS.

---

## Page Route Structure

```
client/src/app/
├── page.tsx          # Main Search & IR Workbench Page (`/`)
├── tale-types/
│   └── page.tsx      # Tale Types & Lineage Browser Page (`/tale-types`)
├── divergence/
│   └── page.tsx      # Comparative Divergence Matrix Page (`/divergence`)
└── evaluation/
    └── page.tsx      # IR Benchmark & Evaluation Dashboard Page (`/evaluation`)
```

---

## Page Features & Usages

### 1. Main Search & IR Workbench (`/`)
* **File**: [`src/app/page.tsx`](file:///e:/Projects/VaartaVerse/client/src/app/page.tsx)
* **Usage**: Provides search interfaces for VSM, Boolean, and Natural Language queries. Features field-weight boost controls, snippet previews, and interactive relevance feedback toggles for Rocchio query expansion.

### 2. Tale Types & Lineage Browser (`/tale-types`)
* **File**: [`src/app/tale-types/page.tsx`](file:///e:/Projects/VaartaVerse/client/src/app/tale-types/page.tsx)
* **Usage**: Explore ATU-classified folk tale categories, inspect narrative motifs, and view cross-regional variant variants linked across traditions (*Panchatantra*, *Jataka*, *Hitopadesha*, etc.).

### 3. Comparative Divergence Matrix (`/divergence`)
* **File**: [`src/app/divergence/page.tsx`](file:///e:/Projects/VaartaVerse/client/src/app/divergence/page.tsx)
* **Usage**: Generates interactive divergence heatmaps, Jaccard distance tables, and vocabulary overlap ratios to visualize how tale narratives evolved across geographical regions.

### 4. IR Evaluation & Benchmark Dashboard (`/evaluation`)
* **File**: [`src/app/evaluation/page.tsx`](file:///e:/Projects/VaartaVerse/client/src/app/evaluation/page.tsx)
* **Usage**: Runs automated query benchmarks against human `qrel` judgments and reports real-time search evaluation metrics (Precision@K, Recall, MAP, nDCG@K, F1 Score).

---

## Running the Web Client

```bash
cd client
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.
