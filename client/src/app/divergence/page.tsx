'use client';

import { useState } from 'react';
import { GitFork, ArrowLeftRight, BarChart2, FileText, CheckCircle, RefreshCw, Zap } from 'lucide-react';

interface VariantPair {
  source_a: string;
  source_b: string;
  cosine_sim: number;
  vocab_overlap_pct: number;
  jaccard_sim: number;
}

export default function DivergencePage() {
  const [selectedTaleType, setSelectedTaleType] = useState('ATU-122');
  const [variantA, setVariantA] = useState('PAN-014');
  const [variantB, setVariantB] = useState('HIT-009');

  const variants = [
    { id: 'PAN-014', title: 'Panchatantra — Ryder Translation (Kashmir)', collection: 'Panchatantra' },
    { id: 'HIT-009', title: 'Hitopadesha — Edwin Arnold (Bengal)', collection: 'Hitopadesha' },
    { id: 'JAT-210', title: 'Jataka Tales — Cowell Vol II (Magadha)', collection: 'Jataka' },
    { id: 'VIK-007', title: 'Baital Pachisi — Burton (Ujjain)', collection: 'Vikramaditya' },
  ];

  // Pairwise matrix mock data calculated via classical TF-IDF cosine distance
  const matrixData: VariantPair[] = [
    { source_a: 'PAN-014', source_b: 'HIT-009', cosine_sim: 0.864, vocab_overlap_pct: 68.2, jaccard_sim: 0.54 },
    { source_a: 'PAN-014', source_b: 'JAT-210', cosine_sim: 0.712, vocab_overlap_pct: 52.1, jaccard_sim: 0.41 },
    { source_a: 'PAN-014', source_b: 'VIK-007', cosine_sim: 0.435, vocab_overlap_pct: 31.4, jaccard_sim: 0.22 },
    { source_a: 'HIT-009', source_b: 'JAT-210', cosine_sim: 0.785, vocab_overlap_pct: 59.8, jaccard_sim: 0.47 },
    { source_a: 'HIT-009', source_b: 'VIK-007', cosine_sim: 0.481, vocab_overlap_pct: 34.0, jaccard_sim: 0.26 },
    { source_a: 'JAT-210', source_b: 'VIK-007', cosine_sim: 0.510, vocab_overlap_pct: 38.5, jaccard_sim: 0.29 },
  ];

  const activePair = matrixData.find(
    (m) =>
      (m.source_a === variantA && m.source_b === variantB) ||
      (m.source_a === variantB && m.source_b === variantA)
  ) || { source_a: variantA, source_b: variantB, cosine_sim: 0.75, vocab_overlap_pct: 55, jaccard_sim: 0.42 };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-3xl font-serif font-bold text-slate-100 flex items-center gap-3">
            Pairwise Variant Divergence & Lineage
            <span className="text-xs font-mono font-normal px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
              Cosine Matrix Math
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Quantify how the same tale archetype (ATU code) diverges across different geographical regions and collections.
          </p>
        </div>

        {/* Tale Type Selector */}
        <div className="flex items-center gap-3 bg-slate-900 p-2 rounded-xl border border-slate-800 self-start md:self-auto">
          <span className="text-xs text-slate-400 font-mono">Tale Type:</span>
          <select
            value={selectedTaleType}
            onChange={(e) => setSelectedTaleType(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-amber-400 font-bold focus:outline-none focus:border-amber-500"
          >
            <option value="ATU-122">ATU 122 — Jackal/Lion in the Well</option>
            <option value="ATU-1430">ATU 1430 — Jackal and War Drum</option>
            <option value="ATU-910">ATU 910 — Baital Pachisi Riddles</option>
          </select>
        </div>
      </div>

      {/* Cosine Matrix Visualization */}
      <div className="glass-panel p-6 border border-slate-800 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h2 className="text-lg font-serif font-bold text-slate-100 flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-amber-400" />
            Pairwise Cosine Similarity Heatmap Matrix ({selectedTaleType})
          </h2>
          <span className="text-xs font-mono text-slate-400">Range: 0.0 (Distinct) to 1.0 (Identical)</span>
        </div>

        {/* Matrix Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-center border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-xs font-mono text-slate-400">
                <th className="p-3 text-left">Variant</th>
                {variants.map((v) => (
                  <th key={v.id} className="p-3 font-semibold text-slate-300">
                    {v.id}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
              {variants.map((row) => (
                <tr key={row.id}>
                  <td className="p-3 text-left font-bold text-amber-300 flex items-center gap-2">
                    <span>{row.id}</span>
                    <span className="text-[10px] text-slate-500 font-normal hidden sm:inline">({row.collection})</span>
                  </td>
                  {variants.map((col) => {
                    if (row.id === col.id) {
                      return (
                        <td key={col.id} className="p-3 bg-amber-500/20 text-amber-300 font-bold">
                          1.000
                        </td>
                      );
                    }
                    const pair = matrixData.find(
                      (m) =>
                        (m.source_a === row.id && m.source_b === col.id) ||
                        (m.source_a === col.id && m.source_b === row.id)
                    );
                    const sim = pair ? pair.cosine_sim : 0.5;
                    const bgClass =
                      sim > 0.8
                        ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30'
                        : sim > 0.6
                        ? 'bg-amber-500/15 text-amber-300 border border-amber-500/20'
                        : 'bg-slate-900 text-slate-400 border border-slate-800';

                    return (
                      <td
                        key={col.id}
                        onClick={() => {
                          setVariantA(row.id);
                          setVariantB(col.id);
                        }}
                        className={`p-3 cursor-pointer transition-all hover:scale-105 ${bgClass}`}
                        title="Click to load side-by-side text comparison"
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
      </div>

      {/* Side by Side Text Comparison Inspector */}
      <div className="glass-panel p-6 border border-slate-800 space-y-6">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <h3 className="text-xl font-serif font-bold text-slate-100 flex items-center gap-2">
              <ArrowLeftRight className="w-5 h-5 text-amber-400" />
              Side-by-Side Variant Text & Vocabulary Inspector
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Comparing <strong className="text-amber-300">{variantA}</strong> against <strong className="text-amber-300">{variantB}</strong>
            </p>
          </div>

          <div className="flex items-center gap-4 bg-slate-900 px-4 py-2 rounded-xl border border-slate-800 text-xs font-mono">
            <div>
              <span className="text-slate-500 block text-[10px]">Cosine Similarity</span>
              <span className="text-base font-bold text-amber-400">{activePair.cosine_sim.toFixed(3)}</span>
            </div>
            <div className="h-6 w-px bg-slate-800" />
            <div>
              <span className="text-slate-500 block text-[10px]">Vocab Overlap</span>
              <span className="text-base font-bold text-emerald-400">{activePair.vocab_overlap_pct}%</span>
            </div>
            <div className="h-6 w-px bg-slate-800" />
            <div>
              <span className="text-slate-500 block text-[10px]">Jaccard Sim</span>
              <span className="text-base font-bold text-indigo-400">{activePair.jaccard_sim.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Text Columns */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Column A */}
          <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-3 font-serif">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="font-mono text-xs font-bold text-amber-400">{variantA}</span>
              <span className="text-xs text-slate-400 font-sans">Panchatantra — Ryder Translation</span>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed italic">
              "In a certain forest lived a lion named Durgama. A clever jackal named Subuddhi approached him and declared: 'Lord, as I brought your dinner, another lion intercepted me near the marble well and claimed sovereignty.' The proud Durgama marched to the well, saw his reflection, roared in anger, and leaped to his demise."
            </p>
            <div className="pt-2 font-sans text-xs text-slate-400 flex flex-wrap gap-1">
              <span className="text-slate-500">Key TF-IDF Terms:</span>
              <span className="bg-amber-500/10 text-amber-300 px-2 py-0.5 rounded">Durgama</span>
              <span className="bg-amber-500/10 text-amber-300 px-2 py-0.5 rounded">Subuddhi</span>
              <span className="bg-amber-500/10 text-amber-300 px-2 py-0.5 rounded">marble well</span>
            </div>
          </div>

          {/* Column B */}
          <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-3 font-serif">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="font-mono text-xs font-bold text-amber-400">{variantB}</span>
              <span className="text-xs text-slate-400 font-sans">Hitopadesha — Edwin Arnold</span>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed italic">
              "Subuddhi the jackal addressed king lion: 'Your Majesty, another ruler challenges your domain from within the stone cistern near the banyan tree.' The monarch peered into the deep waters, mistook his echo for a hostile challenge, and jumped into the abyss."
            </p>
            <div className="pt-2 font-sans text-xs text-slate-400 flex flex-wrap gap-1">
              <span className="text-slate-500">Key TF-IDF Terms:</span>
              <span className="bg-amber-500/10 text-amber-300 px-2 py-0.5 rounded">Subuddhi</span>
              <span className="bg-amber-500/10 text-amber-300 px-2 py-0.5 rounded">stone cistern</span>
              <span className="bg-amber-500/10 text-amber-300 px-2 py-0.5 rounded">echo</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
