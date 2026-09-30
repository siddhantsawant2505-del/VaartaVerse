'use client';

import { useState } from 'react';
import { Play, RefreshCw, BarChart3, Award, Layers, AlertTriangle } from 'lucide-react';

const IR_API = 'http://localhost:5000/api/ir';

interface ModeSummary {
  MAP: number;
  'nDCG@10'?: number;
  'nDCG@5'?: number;
  'P@5'?: number;
  'P@10'?: number;
  Recall: number;
  F1: number;
  query_count: number;
}

interface ModeRow {
  key: string;
  label: string;
  s: ModeSummary | undefined;
}

interface PerQueryEntry {
  query_id: string;
  query_text: string;
  [key: string]: string | number;
}

const MODE_LABELS: Record<string, string> = {
  boolean: 'Boolean (AND/OR/NOT, tf-idf ranked)',
  vsm: 'Vector Space Model (TF-IDF Cosine)',
  bm25: 'BM25 (Okapi)',
  vsm_rocchio: 'VSM + Rocchio PRF (pseudo-feedback)',
};

const MODE_ORDER = ['boolean', 'vsm', 'bm25', 'vsm_rocchio'];

export default function EvaluationPage() {
  const [summaryRows, setSummaryRows] = useState<ModeRow[]>([]);
  const [perQuery, setPerQuery] = useState<PerQueryEntry[]>([]);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [ranOnce, setRanOnce] = useState(false);

  const handleRunEvaluation = async () => {
    setIsEvaluating(true);
    setErrorMsg('');
    try {
      const res = await fetch(`${IR_API}/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ modes: MODE_ORDER }),
      });

      if (!res.ok) {
        setErrorMsg(`Evaluation failed: ${res.status} ${res.statusText}`);
        return;
      }

      const report = await res.json();
      const summary = report.summary || {};

      setSummaryRows(
        MODE_ORDER.map((key) => ({
          key,
          label: MODE_LABELS[key],
          s: summary[key] as ModeSummary | undefined,
        })).filter((row) => row.s)
      );

      // Reshape per-query entries: one row per query with a metric per mode
      const entries: Record<string, any> = {};
      (report.per_query || []).forEach((e: any) => {
        if (!entries[e.query_id]) {
          entries[e.query_id] = {
            query_id: e.query_id,
            query_text: e.query_text,
          };
        }
        const row = entries[e.query_id];
        row[`${e.mode}_ap`] = e.ap;
        row[`${e.mode}_p5`] = e['p@5'];
        row[`${e.mode}_ndcg`] = e['ndcg@10'];
      });

      setPerQuery(Object.values(entries) as PerQueryEntry[]);
      setRanOnce(true);
    } catch {
      setErrorMsg(
        'Cannot reach the evaluation service. Start the server (:5000) and IR engine (:8000).'
      );
    } finally {
      setIsEvaluating(false);
    }
  };

  const bestMap = summaryRows.length
    ? Math.max(...summaryRows.map((r) => r.s?.MAP ?? 0))
    : 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-3xl font-serif font-bold text-slate-100 flex items-center gap-3">
            Classical IR Evaluation Harness
            <span className="text-xs font-mono font-normal px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
              Qrels Benchmarking — Live
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            P, R, F1, P@K, MAP and nDCG across Boolean, VSM, BM25 and Rocchio-PRF retrieval modes.
            Qrels are author-judged over a small corpus — treat absolute values as illustrative.
          </p>
        </div>

        <button
          onClick={handleRunEvaluation}
          disabled={isEvaluating}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-slate-950 font-bold text-sm shadow-lg shadow-amber-500/20 transition-all flex items-center gap-2 self-start md:self-auto"
        >
          {isEvaluating ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <>
              <Play className="w-4 h-4 fill-slate-950" />
              Run Full Benchmark Suite
            </>
          )}
        </button>
      </div>

      {errorMsg && (
        <div className="bg-rose-950/40 border border-rose-500/40 rounded-xl p-4 text-sm text-rose-300 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" /> {errorMsg}
        </div>
      )}

      {!ranOnce && !errorMsg && (
        <div className="glass-panel p-10 rounded-2xl border border-slate-800 text-center space-y-3">
          <BarChart3 className="w-10 h-10 text-amber-500/40 mx-auto" />
          <h3 className="text-lg font-semibold text-slate-300">No evaluation run yet</h3>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            Click “Run Full Benchmark Suite” to execute all retrieval modes against the qrel set and
            compute MAP, nDCG@10, P@5, Recall and F1.
          </p>
        </div>
      )}

      {ranOnce && summaryRows.length > 0 && (
        <>
          {/* Top cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {summaryRows.map((row) => (
              <div
                key={row.key}
                className={`glass-panel p-5 space-y-1 ${
                  row.s?.MAP === bestMap ? 'border-amber-500/40' : 'border-slate-800'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-mono text-slate-500">{row.label}</span>
                  {row.s?.MAP === bestMap && <Award className="w-4 h-4 text-amber-400" />}
                </div>
                <div className="flex items-baseline justify-between">
                  <span className="text-3xl font-mono font-bold text-amber-400">
                    {(row.s?.MAP ?? 0).toFixed(3)}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">MAP</span>
                </div>
                <span className="text-xs text-slate-400 block font-sans">
                  nDCG@10 {(row.s?.['nDCG@10'] ?? 0).toFixed(3)} · P@5 {(row.s?.['P@5'] ?? 0).toFixed(2)} · F1{' '}
                  {(row.s?.F1 ?? 0).toFixed(2)} · {row.s?.query_count} queries
                </span>
              </div>
            ))}
          </div>

          {/* Mode comparison table */}
          <div className="glass-panel p-6 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-serif font-bold text-slate-100 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-amber-400" />
                Retrieval Method Comparison
              </h2>
              <span className="text-xs font-mono text-slate-400">
                Boolean is unranked-matched against ranked metrics — expect low MAP there by design
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse font-mono text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="p-3">Retrieval Mode</th>
                    <th className="p-3 text-right">MAP</th>
                    <th className="p-3 text-right">nDCG@10</th>
                    <th className="p-3 text-right">P@5</th>
                    <th className="p-3 text-right">P@10</th>
                    <th className="p-3 text-right">Recall</th>
                    <th className="p-3 text-right">F1</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {summaryRows.map((row) => (
                    <tr key={row.key} className={row.s?.MAP === bestMap ? 'bg-amber-500/10 font-bold' : ''}>
                      <td className="p-3 flex items-center gap-2 text-slate-200">
                        {row.s?.MAP === bestMap && <Award className="w-4 h-4 text-amber-400" />}
                        <span>{row.label}</span>
                      </td>
                      <td className="p-3 text-right text-amber-400 font-bold">
                        {(row.s?.MAP ?? 0).toFixed(4)}
                      </td>
                      <td className="p-3 text-right text-indigo-400 font-bold">
                        {(row.s?.['nDCG@10'] ?? 0).toFixed(4)}
                      </td>
                      <td className="p-3 text-right text-emerald-400">
                        {(row.s?.['P@5'] ?? 0).toFixed(4)}
                      </td>
                      <td className="p-3 text-right text-slate-300">
                        {(row.s?.['P@10'] ?? 0).toFixed(4)}
                      </td>
                      <td className="p-3 text-right text-slate-300">
                        {(row.s?.Recall ?? 0).toFixed(4)}
                      </td>
                      <td className="p-3 text-right text-amber-200">
                        {(row.s?.F1 ?? 0).toFixed(4)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Per-query breakdown */}
          <div className="glass-panel p-6 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-serif font-bold text-slate-100 flex items-center gap-2">
                <Layers className="w-5 h-5 text-amber-400" />
                Query-by-Query Metric Breakdown
              </h3>
              <span className="text-xs font-mono text-slate-400">AP / P@5 / nDCG@10 per mode</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-mono">
                    <th className="p-3">QID</th>
                    <th className="p-3">Query Text</th>
                    {summaryRows.map((row) => (
                      <th key={row.key} className="p-3 text-right font-semibold text-amber-300/80">
                        {row.key} AP
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-sans">
                  {perQuery.map((q) => (
                    <tr key={q.query_id} className="hover:bg-slate-900/50">
                      <td className="p-3 font-mono font-bold text-amber-400">{q.query_id}</td>
                      <td className="p-3 font-serif text-slate-200">“{q.query_text}”</td>
                      {summaryRows.map((row) => (
                        <td key={row.key} className="p-3 text-right font-mono text-slate-300">
                          {Number(q[`${row.key}_ap`] ?? 0).toFixed(3)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
