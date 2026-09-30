'use client';

import { useEffect, useMemo, useState } from 'react';
import { GitFork, ArrowLeftRight, BarChart2, RefreshCw, AlertTriangle } from 'lucide-react';

const IR_API = 'http://localhost:5000/api/ir';

interface VariantMeta {
  doc_id: string;
  tale_id: string;
  title: string;
  region: string;
  tradition: string;
  source_collection: string;
  snippet: string;
}

interface MatrixPair {
  source_a: string;
  source_b: string;
  doc_id_a: string;
  doc_id_b: string;
  cosine_similarity: number;
  vocab_overlap_pct: number;
  jaccard_similarity: number;
}

interface DivergenceData {
  tale_type_id: string;
  variant_count: number;
  variants: VariantMeta[];
  matrix: MatrixPair[];
  centroid_top_terms: string[];
  summary: {
    avg_cosine_similarity: number;
    min_cosine_similarity: number;
    max_cosine_similarity: number;
    most_similar_pair: MatrixPair | Record<string, never>;
    most_divergent_pair: MatrixPair | Record<string, never>;
  };
}

interface TaleTypeEntry {
  tale_type: string;
  variant_count: number;
}

export default function DivergencePage() {
  const [taleTypes, setTaleTypes] = useState<TaleTypeEntry[]>([]);
  const [selectedTaleType, setSelectedTaleType] = useState<string>('');
  const [variantA, setVariantA] = useState<string>('');
  const [variantB, setVariantB] = useState<string>('');
  const [data, setData] = useState<DivergenceData | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Load the tale-type registry
  useEffect(() => {
    fetch(`${IR_API}/tale-types`)
      .then((r) => r.json())
      .then((body) => {
        const types: TaleTypeEntry[] = body.tale_types || [];
        setTaleTypes(types);
        const best = [...types].sort((a, b) => b.variant_count - a.variant_count)[0];
        if (best) setSelectedTaleType(best.tale_type);
      })
      .catch(() => setErrorMsg('Cannot reach the IR engine at localhost:5000/api/ir.'));
  }, []);

  // Load the divergence matrix whenever the selected tale type changes
  useEffect(() => {
    if (!selectedTaleType) return;
    setLoading(true);
    setErrorMsg('');
    fetch(`${IR_API}/tale-type/${encodeURIComponent(selectedTaleType)}/divergence`)
      .then(async (r) => {
        if (!r.ok) throw new Error(`Engine returned ${r.status}`);
        return r.json();
      })
      .then((body: DivergenceData) => {
        setData(body);
        setVariantA(body.variants[0]?.doc_id ?? '');
        setVariantB(body.variants[1]?.doc_id ?? '');
      })
      .catch((e) => {
        setData(null);
        setErrorMsg(e instanceof Error ? e.message : 'Divergence request failed');
      })
      .finally(() => setLoading(false));
  }, [selectedTaleType]);

  const pairLookup = useMemo(() => {
    const map = new Map<string, MatrixPair>();
    data?.matrix.forEach((m) => {
      map.set(`${m.doc_id_a}|${m.doc_id_b}`, m);
      map.set(`${m.doc_id_b}|${m.doc_id_a}`, m);
    });
    return map;
  }, [data]);

  const metaById = useMemo(() => {
    const map = new Map<string, VariantMeta>();
    data?.variants.forEach((v) => map.set(v.doc_id, v));
    return map;
  }, [data]);

  const activePair =
    (variantA && variantB && pairLookup.get(`${variantA}|${variantB}`)) || null;

  const cellColor = (sim: number) =>
    sim > 0.5
      ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30'
      : sim > 0.25
      ? 'bg-amber-500/15 text-amber-300 border border-amber-500/20'
      : 'bg-slate-900 text-slate-400 border border-slate-800';

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-3xl font-serif font-bold text-slate-100 flex items-center gap-3">
            Pairwise Variant Divergence &amp; Lineage
            <span className="text-xs font-mono font-normal px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
              Real TF-IDF Cosine — Live from Engine
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Pairwise cosine similarity, Jaccard and vocabulary overlap between variants of the same
            tale type, computed live from the inverted index.
          </p>
        </div>

        {/* Tale Type Selector — populated from the engine registry */}
        <div className="flex items-center gap-3 bg-slate-900 p-2 rounded-xl border border-slate-800 self-start md:self-auto">
          <span className="text-xs text-slate-400 font-mono">Tale Type:</span>
          <select
            value={selectedTaleType}
            onChange={(e) => setSelectedTaleType(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-amber-400 font-bold focus:outline-none focus:border-amber-500 max-w-[220px]"
          >
            {taleTypes.map((t) => (
              <option key={t.tale_type} value={t.tale_type}>
                {t.tale_type} ({t.variant_count})
              </option>
            ))}
          </select>
        </div>
      </div>

      {errorMsg && (
        <div className="bg-rose-950/40 border border-rose-500/40 rounded-xl p-4 text-sm text-rose-300 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" /> {errorMsg}
        </div>
      )}

      {loading && (
        <div className="glass-panel p-10 rounded-2xl border border-slate-800 flex items-center justify-center gap-3 text-slate-400">
          <RefreshCw className="w-5 h-5 animate-spin" /> Computing pairwise matrix…
        </div>
      )}

      {!loading && data && data.variants.length < 2 && (
        <div className="glass-panel p-10 rounded-2xl border border-slate-800 text-center text-slate-400">
          This tale type has fewer than 2 variants — nothing to compare.
        </div>
      )}

      {!loading && data && data.variants.length >= 2 && (
        <>
          {/* Summary strip */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="glass-panel p-5 border-slate-800 space-y-1">
              <span className="text-[10px] uppercase font-mono text-slate-500">Avg Cosine</span>
              <div className="text-2xl font-mono font-bold text-amber-400">
                {data.summary.avg_cosine_similarity.toFixed(3)}
              </div>
            </div>
            <div className="glass-panel p-5 border-slate-800 space-y-1">
              <span className="text-[10px] uppercase font-mono text-slate-500">Most Similar</span>
              <div className="text-2xl font-mono font-bold text-emerald-400">
                {data.summary.max_cosine_similarity.toFixed(3)}
              </div>
            </div>
            <div className="glass-panel p-5 border-slate-800 space-y-1">
              <span className="text-[10px] uppercase font-mono text-slate-500">Most Divergent</span>
              <div className="text-2xl font-mono font-bold text-indigo-400">
                {data.summary.min_cosine_similarity.toFixed(3)}
              </div>
            </div>
            <div className="glass-panel p-5 border-slate-800 space-y-1">
              <span className="text-[10px] uppercase font-mono text-slate-500">Variants</span>
              <div className="text-2xl font-mono font-bold text-slate-200">
                {data.variant_count}
              </div>
            </div>
          </div>

          {/* Heatmap */}
          <div className="glass-panel p-6 border border-slate-800 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-serif font-bold text-slate-100 flex items-center gap-2">
                <BarChart2 className="w-5 h-5 text-amber-400" />
                Pairwise Cosine Similarity Matrix ({selectedTaleType})
              </h2>
              <span className="text-xs font-mono text-slate-400">
                Click a cell to inspect the pair below
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-center border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-xs font-mono text-slate-400">
                    <th className="p-3 text-left">Variant</th>
                    {data.variants.map((v) => (
                      <th key={v.doc_id} className="p-3 font-semibold text-slate-300">
                        {v.tale_id}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
                  {data.variants.map((row) => (
                    <tr key={row.doc_id}>
                      <td className="p-3 text-left font-bold text-amber-300">
                        <span>{row.tale_id}</span>
                        <span className="text-[10px] text-slate-500 font-normal ml-2 hidden sm:inline">
                          {row.tradition}
                        </span>
                      </td>
                      {data.variants.map((col) => {
                        if (row.doc_id === col.doc_id) {
                          return (
                            <td
                              key={col.doc_id}
                              className="p-3 bg-amber-500/20 text-amber-300 font-bold"
                            >
                              1.000
                            </td>
                          );
                        }
                        const pair = pairLookup.get(`${row.doc_id}|${col.doc_id}`);
                        const sim = pair ? pair.cosine_similarity : 0;
                        return (
                          <td
                            key={col.doc_id}
                            onClick={() => {
                              setVariantA(row.doc_id);
                              setVariantB(col.doc_id);
                            }}
                            className={`p-3 cursor-pointer transition-all hover:scale-105 ${cellColor(sim)}`}
                          >
                            {sim.toFixed(3)}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Shared vocabulary of the cluster */}
            <div className="pt-2 font-sans text-xs text-slate-400 flex flex-wrap gap-1">
              <span className="text-slate-500">Centroid top terms:</span>
              {data.centroid_top_terms.slice(0, 12).map((t) => (
                <span key={t} className="bg-amber-500/10 text-amber-300 px-2 py-0.5 rounded font-mono">
                  {t}
                </span>
              ))}
            </div>
          </div>

          {/* Side-by-side inspector backed by real variant metadata */}
          <div className="glass-panel p-6 border border-slate-800 space-y-6">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-slate-800 pb-4">
              <h3 className="text-xl font-serif font-bold text-slate-100 flex items-center gap-2">
                <ArrowLeftRight className="w-5 h-5 text-amber-400" />
                Variant Comparison
              </h3>
              <div className="flex items-center gap-4 bg-slate-900 px-4 py-2 rounded-xl border border-slate-800 text-xs font-mono">
                <div>
                  <span className="text-slate-500 block text-[10px]">Cosine</span>
                  <span className="text-base font-bold text-amber-400">
                    {activePair ? activePair.cosine_similarity.toFixed(3) : '—'}
                  </span>
                </div>
                <div className="h-6 w-px bg-slate-800" />
                <div>
                  <span className="text-slate-500 block text-[10px]">Vocab Overlap</span>
                  <span className="text-base font-bold text-emerald-400">
                    {activePair ? `${activePair.vocab_overlap_pct}%` : '—'}
                  </span>
                </div>
                <div className="h-6 w-px bg-slate-800" />
                <div>
                  <span className="text-slate-500 block text-[10px]">Jaccard</span>
                  <span className="text-base font-bold text-indigo-400">
                    {activePair ? activePair.jaccard_similarity.toFixed(2) : '—'}
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[variantA, variantB].map((id, i) => {
                const meta = metaById.get(id);
                return (
                  <div
                    key={`${id}-${i}`}
                    className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-3 font-serif"
                  >
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <span className="font-mono text-xs font-bold text-amber-400">
                        {meta?.tale_id ?? id}
                      </span>
                      <span className="text-xs text-slate-400 font-sans">
                        {meta?.source_collection || meta?.tradition || '—'}
                      </span>
                    </div>
                    <h4 className="text-sm font-bold text-slate-200">{meta?.title || 'Untitled'}</h4>
                    <p className="text-sm text-slate-300 leading-relaxed italic">
                      {meta?.snippet ? `"${meta.snippet}"` : 'No text available.'}
                    </p>
                    <div className="pt-1 font-sans text-xs text-slate-400">
                      {meta?.region && <span>Region: {meta.region}</span>}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
