'use client';

import { useState } from 'react';
import Link from 'next/link';
import { BookOpen, GitBranch, Compass, Search, ChevronRight, Layers, MapPin } from 'lucide-react';

interface TaleTypeItem {
  id: string;
  atu_code: string;
  title: string;
  tradition_primary: string;
  summary: string;
  motifs: string[];
  variant_count: number;
  collections: string[];
  regions: string[];
}

export default function TaleTypesPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTradition, setSelectedTradition] = useState('all');

  const taleTypes: TaleTypeItem[] = [
    {
      id: 'atu-122',
      atu_code: 'ATU 122',
      title: 'The Trickster and the Arrogant Predator in the Well',
      tradition_primary: 'Panchatantra / Hitopadesha',
      summary: 'A small animal (jackal, hare, or deer) tricks an oppressive lion into seeing his own reflection in a water well and leaping to his death.',
      motifs: ['K521.1 Lion tricked by reflection', 'J2131.5 Animal leaps into well'],
      variant_count: 5,
      collections: ['Panchatantra (Ryder)', 'Hitopadesha (Arnold)', 'Jataka Tales (Cowell)', 'Kathasaritsagara'],
      regions: ['Kashmir', 'Bengal', 'Magadha', 'Ujjain'],
    },
    {
      id: 'atu-1430',
      atu_code: 'ATU 1430',
      title: 'The Jackal and the War Drum',
      tradition_primary: 'Panchatantra',
      summary: 'A hungry jackal discovers a hollow war drum beating against branches. Expecting meat inside, he bites into it only to find air and parchment.',
      motifs: ['J260.1 False expectation of food', 'K2310 Deceptive hollow sound'],
      variant_count: 4,
      collections: ['Panchatantra', 'Hitopadesha', 'Tales of the Sun (South India)'],
      regions: ['Punjab', 'Tamil Nadu', 'Odisha'],
    },
    {
      id: 'atu-910',
      atu_code: 'ATU 910 / VIK-01',
      title: 'King Vikramaditya and the Baital Riddles',
      tradition_primary: 'Vikramaditya Cycle',
      summary: 'King Vikram carries a corpses containing a vampire spirit (Baital), who narrates complex ethical paradoxes requiring fair judgment.',
      motifs: ['H510 Riddles of justice', 'F900 Celestial trial of kingship'],
      variant_count: 6,
      collections: ['Baital Pachisi (Burton)', 'Simhasana Dvatrimsika', 'Bhattacharyya Retellings'],
      regions: ['Ujjain', 'Maharashtra', 'Gujarat'],
    },
    {
      id: 'atu-1525',
      atu_code: 'ATU 1525 / BIR-04',
      title: 'Birbal’s Khichdi (Patience and Subtle Proof)',
      tradition_primary: 'Birbal–Akbar Tales',
      summary: 'Birbal cooks khichdi on a high branch far above a small flame to demonstrate to Emperor Akbar how minimal warmth inspired a freezing man.',
      motifs: ['J1171 Clever judicial proof', 'H500 Wit over authority'],
      variant_count: 3,
      collections: ['Birbal Folklore (North India)', 'Akbar-Nama Episodes'],
      regions: ['Agra/Delhi', 'Rajasthan'],
    },
    {
      id: 'atu-545',
      atu_code: 'ATU 545 / TEN-02',
      title: 'Tenali Raman and the Thieves in the Garden',
      tradition_primary: 'Tenali Raman Tales',
      summary: 'Tenali tricks thieves into watering his entire agricultural garden overnight by dropping heavy stones into a dry well.',
      motifs: ['K400 Trickster uses thieves for labor', 'J1115 Clever court jester'],
      variant_count: 3,
      collections: ['Tenali Raman Stories', 'Vijayanagara Court Chronicles'],
      regions: ['Andhra Pradesh', 'Karnataka'],
    }
  ];

  const filteredTypes = taleTypes.filter((t) => {
    const matchesSearch =
      t.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.atu_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.summary.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTradition =
      selectedTradition === 'all' || t.tradition_primary.toLowerCase().includes(selectedTradition.toLowerCase());
    return matchesSearch && matchesTradition;
  });

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-3xl font-serif font-bold text-slate-100 flex items-center gap-3">
            Tale-Type Registry & Lineage Browser
            <span className="text-xs font-mono font-normal px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
              ATU Motif Classification
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Explore how canonical Indian story archetypes branch across Panchatantra, Jataka, Hitopadesha, and regional traditions.
          </p>
        </div>
      </div>

      {/* Filter bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900/80 p-4 rounded-xl border border-slate-800">
        <div className="relative w-full sm:w-96">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search ATU code, title, motif, or summary..."
            className="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 pl-9 pr-4 text-sm text-slate-200 focus:outline-none focus:border-amber-500"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <span className="text-xs text-slate-400 whitespace-nowrap">Tradition:</span>
          <select
            value={selectedTradition}
            onChange={(e) => setSelectedTradition(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-amber-500 w-full sm:w-auto"
          >
            <option value="all">All Traditions</option>
            <option value="panchatantra">Panchatantra</option>
            <option value="hitopadesha">Hitopadesha</option>
            <option value="vikramaditya">Vikramaditya Cycle</option>
            <option value="birbal">Birbal-Akbar</option>
            <option value="tenali">Tenali Raman</option>
          </select>
        </div>
      </div>

      {/* Tale Types Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredTypes.map((item) => (
          <div
            key={item.id}
            className="glass-panel-hover p-6 flex flex-col justify-between space-y-4 border border-slate-800"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold px-2.5 py-1 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
                  {item.atu_code}
                </span>
                <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                  <GitBranch className="w-3.5 h-3.5 text-amber-500" />
                  {item.variant_count} Cross-Regional Variants
                </span>
              </div>

              <h2 className="text-xl font-serif font-bold text-slate-100 hover:text-amber-300 transition-colors">
                {item.title}
              </h2>

              <p className="text-sm text-slate-300 leading-relaxed font-serif">
                {item.summary}
              </p>

              {/* Motifs */}
              <div className="space-y-1">
                <span className="text-[10px] uppercase font-mono text-slate-500 block">Stith Thompson Motifs</span>
                <div className="flex flex-wrap gap-1.5">
                  {item.motifs.map((motif) => (
                    <span key={motif} className="text-xs font-mono px-2 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800">
                      {motif}
                    </span>
                  ))}
                </div>
              </div>

              {/* Regional Spread */}
              <div className="pt-2 flex items-center gap-2 flex-wrap text-xs text-slate-400">
                <MapPin className="w-3.5 h-3.5 text-amber-500" />
                <span>Regions:</span>
                {item.regions.map((reg) => (
                  <span key={reg} className="bg-slate-900 px-2 py-0.5 rounded text-slate-300 border border-slate-800">
                    {reg}
                  </span>
                ))}
              </div>
            </div>

            {/* Action Footer */}
            <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between">
              <span className="text-xs font-sans text-slate-400">
                Primary: <strong className="text-slate-200 font-semibold">{item.tradition_primary}</strong>
              </span>
              <Link
                href={`/divergence?taleType=${item.id}`}
                className="px-4 py-2 rounded-lg bg-amber-500/15 hover:bg-amber-500 text-amber-300 hover:text-slate-950 border border-amber-500/30 text-xs font-bold transition-all flex items-center gap-1.5"
              >
                Inspect Lineage & Divergence
                <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
