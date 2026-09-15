'use client';

import { useState } from 'react';
import { Search, ThumbsUp, ThumbsDown, SlidersHorizontal, Terminal, Sparkles, Filter, ChevronRight, Info, RefreshCw, CheckCircle2 } from 'lucide-react';

interface TaleSearchResult {
  id: string;
  tale_id: string;
  tale_type_id: string;
  title: string;
  source_collection: string;
  region: string;
  tradition: string;
  translator: string;
  score: number;
  snippet: string;
  zone_weights: { title: number; body: number };
  terms_matched: string[];
  user_feedback?: 'relevant' | 'non_relevant' | null;
}

export default function SearchPage() {
  const [query, setQuery] = useState('smart jackal tricked lion water well AND Panchatantra');
  const [isBooleanMode, setIsBooleanMode] = useState(false);
  const [showParserDetails, setShowParserDetails] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedRegion, setSelectedRegion] = useState<string>('all');
  const [selectedCollection, setSelectedCollection] = useState<string>('all');

  // Sample classical IR mock results matching real index data schema
  const [results, setResults] = useState<TaleSearchResult[]>([
    {
      id: '1',
      tale_id: 'PAN-014',
      tale_type_id: 'ATU-122',
      title: 'The Smart Jackal and the Proud Lion',
      source_collection: 'Panchatantra — Ryder Translation',
      region: 'North-West (Kashmir/Punjab)',
      tradition: 'Panchatantra',
      translator: 'Arthur W. Ryder',
      score: 0.8942,
      snippet: 'In a certain forest lived a lion named Durgama. A clever jackal convinced him that another fierce lion resided inside a deep well...',
      zone_weights: { title: 0.35, body: 0.5442 },
      terms_matched: ['jackal', 'lion', 'well', 'trick'],
      user_feedback: null,
    },
    {
      id: '2',
      tale_id: 'HIT-009',
      tale_type_id: 'ATU-122',
      title: 'The Jackal, Lion, and Reflection in the Well',
      source_collection: 'Hitopadesha — Edwin Arnold Translation',
      region: 'East (Bengal/Odisha)',
      tradition: 'Hitopadesha',
      translator: 'Sir Edwin Arnold',
      score: 0.8210,
      snippet: 'Subuddhi the jackal addressed king lion: Your Majesty, another ruler challenges your domain from within the stone cistern near the banyan tree...',
      zone_weights: { title: 0.25, body: 0.5710 },
      terms_matched: ['jackal', 'lion', 'reflection', 'well'],
      user_feedback: null,
    },
    {
      id: '3',
      tale_id: 'JAT-210',
      tale_type_id: 'ATU-122',
      title: 'Sighala Jataka: The Foolish Lion and the Jackal',
      source_collection: 'Jataka Tales — Cowell Vol II',
      region: 'Magadha (Central India)',
      tradition: 'Jataka',
      translator: 'E.B. Cowell',
      score: 0.7435,
      snippet: 'Bodhisatta born as a wise jackal used council to protect forest animals against an arrogant lion king by showing him his shadow...',
      zone_weights: { title: 0.20, body: 0.5435 },
      terms_matched: ['jackal', 'lion', 'shadow'],
      user_feedback: null,
    },
    {
      id: '4',
      tale_id: 'VIK-007',
      tale_type_id: 'ATU-910',
      title: 'Baital Pachisi: The Jackal’s Verdict for King Vikramaditya',
      source_collection: 'Simhasana Dvatrimsika / Baital Pachisi',
      region: 'Ujjain (Central India)',
      tradition: 'Vikramaditya Cycle',
      translator: 'Richard F. Burton',
      score: 0.6512,
      snippet: 'The vampire Baital posed a riddle to King Vikram: Who demonstrated higher wisdom, the tiger or the jackal near the deep stream?',
      zone_weights: { title: 0.15, body: 0.5012 },
      terms_matched: ['jackal', 'vikramaditya', 'riddle'],
      user_feedback: null,
    },
  ]);

  const [parsedInfo, setParsedInfo] = useState<any>({
    mode: 'vsm',
    normalized_query: 'smart jackal trick lion water well panchatantra',
    stems: ['smart', 'jackal', 'trick', 'lion', 'water', 'well', 'panchatantra'],
    entities: { traditions: ['Panchatantra'], regions: [], atu_codes: [] },
    filters: {},
  });

  const handleSearch = async (e?: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const searchQuery = customQuery ?? query;
    if (!searchQuery.trim()) return;
    setIsSearching(true);

    try {
      const endpoint = isBooleanMode
        ? 'http://localhost:8000/search/boolean'
        : 'http://localhost:8000/search/nl-query';
      
      const payload = isBooleanMode
        ? { query: searchQuery }
        : { query: searchQuery, top_k: 10 };

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        if (data.parsed) {
          const stems = data.parsed.normalized_query
            ? data.parsed.normalized_query.split(/\s+/).filter(Boolean)
            : searchQuery.toLowerCase().split(/\s+/);
          setParsedInfo({
            mode: data.parsed.mode || 'vsm',
            normalized_query: data.parsed.normalized_query || searchQuery,
            stems: stems,
            entities: data.parsed.entities || { traditions: [], regions: [], atu_codes: [] },
            filters: data.parsed.filters || {},
          });
        } else {
          setParsedInfo({
            mode: isBooleanMode ? 'boolean' : 'vsm',
            normalized_query: searchQuery,
            stems: searchQuery.toLowerCase().split(/\s+/).filter(Boolean),
            entities: { traditions: [], regions: [], atu_codes: [] },
            filters: {},
          });
        }

        const rawResults = data.results || [];
        const mappedResults: TaleSearchResult[] = rawResults.map((r: any, idx: number) => ({
          id: r.doc_id || String(idx + 1),
          tale_id: r.tale_id || r.doc_id,
          tale_type_id: r.tale_type || 'ATU-122',
          title: r.title || 'Untitled Tale',
          source_collection: r.source_collection || 'Collection',
          region: r.region || 'India',
          tradition: r.tradition || 'Folk Tradition',
          translator: r.translator || 'Unknown',
          score: typeof r.score === 'number' ? r.score : 0.5,
          snippet: r.snippet || (r.text ? r.text.slice(0, 180) + '...' : 'Tale variant content indexed in inverted index.'),
          zone_weights: r.zone_weights || { title: 0.35, body: 0.65 },
          terms_matched: r.terms_matched || r.terms || [],
          user_feedback: null,
        }));
        setResults(mappedResults);
      }
    } catch (err) {
      console.warn('Backend API offline or unreachable, using sample data:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleChipClick = (presetQuery: string, isBool: boolean = false) => {
    setQuery(presetQuery);
    setIsBooleanMode(isBool);
    handleSearch(undefined, presetQuery);
  };

  const toggleFeedback = (id: string, feedbackType: 'relevant' | 'non_relevant') => {
    setResults((prev) =>
      prev.map((item) => {
        if (item.id === id) {
          const newFeedback = item.user_feedback === feedbackType ? null : feedbackType;
          return { ...item, user_feedback: newFeedback };
        }
        return item;
      })
    );
  };

  const handleApplyRocchio = async () => {
    setIsSearching(true);
    const relevantIds = results.filter((r) => r.user_feedback === 'relevant').map((r) => r.tale_id);
    const nonRelevantIds = results.filter((r) => r.user_feedback === 'non_relevant').map((r) => r.tale_id);

    try {
      const res = await fetch('http://localhost:8000/search/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          relevant_ids: relevantIds,
          non_relevant_ids: nonRelevantIds,
          top_k: 10,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        const rawResults = data.results || [];
        const mappedResults: TaleSearchResult[] = rawResults.map((r: any, idx: number) => ({
          id: r.doc_id || String(idx + 1),
          tale_id: r.tale_id || r.doc_id,
          tale_type_id: r.tale_type || 'ATU-122',
          title: r.title || 'Untitled Tale',
          source_collection: r.source_collection || 'Collection',
          region: r.region || 'India',
          tradition: r.tradition || 'Folk Tradition',
          translator: r.translator || 'Unknown',
          score: typeof r.score === 'number' ? r.score : 0.5,
          snippet: r.snippet || (r.text ? r.text.slice(0, 180) + '...' : 'Tale variant content indexed in inverted index.'),
          zone_weights: r.zone_weights || { title: 0.35, body: 0.65 },
          terms_matched: r.terms_matched || r.terms || [],
          user_feedback: results.find((existing) => existing.tale_id === r.tale_id)?.user_feedback || null,
        }));
        if (mappedResults.length > 0) {
          setResults(mappedResults);
        }
      }
    } catch (err) {
      console.warn('Rocchio API offline, re-ranking locally:', err);
      setResults((prev) =>
        [...prev].sort((a, b) => {
          let scoreA = a.score + (a.user_feedback === 'relevant' ? 0.15 : a.user_feedback === 'non_relevant' ? -0.2 : 0);
          let scoreB = b.score + (b.user_feedback === 'relevant' ? 0.15 : b.user_feedback === 'non_relevant' ? -0.2 : 0);
          return scoreB - scoreA;
        })
      );
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-[#space] space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-3xl font-serif font-bold text-slate-100 flex items-center gap-3">
            Classical IR Search Engine
            <span className="text-xs font-mono font-normal px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
              No-LLM / Pure Math IR
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Inverted index postings, TF-IDF VSM scoring, title/body zone weighting, and Rocchio feedback.
          </p>
        </div>

        {/* Query Mode Switch */}
        <div className="flex items-center gap-3 bg-slate-900/90 p-1.5 rounded-xl border border-slate-800 self-start md:self-auto">
          <button
            onClick={() => setIsBooleanMode(false)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
              !isBooleanMode
                ? 'bg-amber-500 text-slate-950 shadow-md font-bold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Vector Space (VSM + TF-IDF)
          </button>
          <button
            onClick={() => setIsBooleanMode(true)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
              isBooleanMode
                ? 'bg-amber-500 text-slate-950 shadow-md font-bold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            Boolean AST (AND/OR/NOT)
          </button>
        </div>
      </div>

      {/* Search Input Box */}
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              isBooleanMode
                ? 'Enter boolean query e.g. (jackal OR fox) AND lion AND NOT tiger'
                : 'Enter query e.g. smart jackal tricked lion in water well Panchatantra'
            }
            className="w-full bg-slate-900/90 border-2 border-slate-800 rounded-2xl py-4 pl-14 pr-32 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500/60 shadow-2xl transition-all font-sans text-base"
          />
          <Search className="w-6 h-6 text-amber-500 absolute left-4 top-1/2 -translate-y-1/2" />
          <button
            type="submit"
            disabled={isSearching}
            className="absolute right-3 top-1/2 -translate-y-1/2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-slate-950 font-bold text-sm shadow-lg shadow-amber-500/20 transition-all flex items-center gap-2"
          >
            {isSearching ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <>
                Execute IR Search
                <ChevronRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>

        {/* Quick Query Preset Chips (Single-word, Multi-word, NL & Boolean) */}
        <div className="flex flex-wrap items-center gap-2 text-xs pt-1">
          <span className="text-slate-400 font-mono text-[11px]">Try query presets:</span>
          <button
            type="button"
            onClick={() => handleChipClick('jackal')}
            className="px-2.5 py-1 rounded-full bg-slate-900 hover:bg-slate-800 text-amber-300 border border-slate-700 transition-all font-mono text-[11px]"
          >
            single-word: <span className="underline">jackal</span>
          </button>
          <button
            type="button"
            onClick={() => handleChipClick('mongoose')}
            className="px-2.5 py-1 rounded-full bg-slate-900 hover:bg-slate-800 text-amber-300 border border-slate-700 transition-all font-mono text-[11px]"
          >
            single-word: <span className="underline">mongoose</span>
          </button>
          <button
            type="button"
            onClick={() => handleChipClick('jackal lion well')}
            className="px-2.5 py-1 rounded-full bg-slate-900 hover:bg-slate-800 text-amber-200 border border-slate-700 transition-all font-mono text-[11px]"
          >
            multi-word: <span className="underline">jackal lion well</span>
          </button>
          <button
            type="button"
            onClick={() => handleChipClick('monkey crocodile river')}
            className="px-2.5 py-1 rounded-full bg-slate-900 hover:bg-slate-800 text-amber-200 border border-slate-700 transition-all font-mono text-[11px]"
          >
            multi-word: <span className="underline">monkey crocodile river</span>
          </button>
          <button
            type="button"
            onClick={() => handleChipClick('Show Panchatantra tales from Kashmir about a clever jackal')}
            className="px-2.5 py-1 rounded-full bg-slate-900 hover:bg-slate-800 text-emerald-300 border border-slate-700 transition-all font-mono text-[11px]"
          >
            natural-language: <span className="underline">Panchatantra tales in Kashmir</span>
          </button>
          <button
            type="button"
            onClick={() => handleChipClick('(jackal OR fox) AND lion AND NOT tiger', true)}
            className="px-2.5 py-1 rounded-full bg-slate-900 hover:bg-slate-800 text-indigo-300 border border-slate-700 transition-all font-mono text-[11px]"
          >
            boolean-AST: <span className="underline">(jackal OR fox) AND lion</span>
          </button>
        </div>

        {/* Filter controls */}
        <div className="flex flex-wrap items-center justify-between gap-3 text-xs pt-1">
          <div className="flex items-center gap-4 text-slate-400">
            <span className="flex items-center gap-1.5 font-semibold text-slate-300">
              <Filter className="w-3.5 h-3.5 text-amber-400" /> Corpus Filters:
            </span>
            <select
              value={selectedCollection}
              onChange={(e) => setSelectedCollection(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-300 focus:outline-none focus:border-amber-500"
            >
              <option value="all">All Collections</option>
              <option value="panchatantra">Panchatantra (Ryder)</option>
              <option value="hitopadesha">Hitopadesha (Arnold)</option>
              <option value="jataka">Jataka Tales (Cowell)</option>
              <option value="vikramaditya">Vikramaditya Cycle</option>
            </select>
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-300 focus:outline-none focus:border-amber-500"
            >
              <option value="all">All Regions</option>
              <option value="northwest">North-West (Kashmir/Punjab)</option>
              <option value="east">East (Bengal/Odisha)</option>
              <option value="magadha">Magadha (Central India)</option>
              <option value="ujjain">Ujjain (Malwa)</option>
            </select>
          </div>

          <button
            type="button"
            onClick={() => setShowParserDetails(!showParserDetails)}
            className="text-amber-400 hover:text-amber-300 flex items-center gap-1 font-mono hover:underline"
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            {showParserDetails ? 'Hide IR Parser & Stemming Inspector' : 'Inspect IR Parser & AST'}
          </button>
        </div>
      </form>

      {/* Query Parser Live Inspection Drawer */}
      {showParserDetails && (
        <div className="glass-panel p-4 border border-amber-500/20 bg-slate-900/80 rounded-xl space-y-3 font-mono text-xs">
          <div className="flex items-center justify-between text-amber-400 border-b border-slate-800 pb-2">
            <span className="flex items-center gap-2 font-bold uppercase tracking-wider">
              <Terminal className="w-4 h-4 text-amber-400" /> Classical IR Rule-Based Query Parser Output
            </span>
            <span className="text-[10px] bg-amber-500/20 px-2 py-0.5 rounded text-amber-300">
              Pipeline: PorterStemmer + StopwordRemoval + EntityExtractor
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-slate-300">
            <div>
              <span className="text-slate-500 block text-[10px] uppercase">Extracted Terms & Stems</span>
              <div className="mt-1 flex flex-wrap gap-1">
                {(parsedInfo.stems || []).map((stem: string) => (
                  <span key={stem} className="bg-slate-800 px-2 py-0.5 rounded text-amber-300 border border-slate-700">
                    {stem}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px] uppercase">Extracted Entities & Metadata</span>
              <div className="mt-1 space-y-1 text-slate-300 text-[11px]">
                <div>
                  Traditions: <span className="text-amber-300 font-bold">{parsedInfo.entities?.traditions?.join(', ') || 'None detected'}</span>
                </div>
                <div>
                  Regions: <span className="text-amber-300 font-bold">{parsedInfo.entities?.regions?.join(', ') || 'None detected'}</span>
                </div>
              </div>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px] uppercase">Execution Mode & Normalized Query</span>
              <code className="mt-1 block text-emerald-400 bg-slate-950 p-1.5 rounded border border-slate-800 text-[11px] overflow-x-auto">
                Mode: {parsedInfo.mode?.toUpperCase()} | Query: "{parsedInfo.normalized_query}"
              </code>
            </div>
          </div>
        </div>
      )}

      {/* Relevance Feedback Banner (Rocchio Trigger) */}
      {results.some((r) => r.user_feedback) && (
        <div className="bg-gradient-to-r from-amber-500/20 via-amber-600/10 to-transparent border border-amber-500/40 rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Info className="w-5 h-5 text-amber-400 flex-shrink-0" />
            <div>
              <h4 className="text-sm font-semibold text-amber-200">Explicit Relevance Feedback Active</h4>
              <p className="text-xs text-slate-300">
                You marked {results.filter((r) => r.user_feedback === 'relevant').length} relevant and{' '}
                {results.filter((r) => r.user_feedback === 'non_relevant').length} non-relevant document(s). Ready for Rocchio query shift (q_m = α·q₀ + β·μ_r − γ·μ_nr).
              </p>
            </div>
          </div>
          <button
            onClick={handleApplyRocchio}
            className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg text-xs shadow-lg transition-all"
          >
            Apply Rocchio Re-Ranking
          </button>
        </div>
      )}

      {/* Results Header */}
      <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
        <span>Showing {results.length} ranked tale variants from Inverted Index</span>
        <span>Retrieval metric: Cosine Similarity (TF-IDF w/ Sublinear Scaling)</span>
      </div>

      {/* Results List or Empty "Not Found" State */}
      {results.length === 0 ? (
        <div className="glass-panel p-8 border border-rose-500/30 bg-slate-900/90 rounded-2xl text-center space-y-4 my-6">
          <div className="w-16 h-16 rounded-full bg-rose-500/10 border border-rose-500/30 flex items-center justify-center mx-auto text-rose-400">
            <Search className="w-8 h-8" />
          </div>
          <div className="space-y-1">
            <h3 className="text-xl font-serif font-bold text-slate-100">No Matching Folk Tales Found</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto">
              0 indexed documents in the inverted index matched your query: <code className="text-amber-300 font-mono text-xs">"{query}"</code>
            </p>
          </div>

          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 max-w-lg mx-auto text-left space-y-2 text-xs">
            <span className="text-amber-400 font-mono font-semibold block uppercase text-[11px]">Suggestions to refine your search:</span>
            <ul className="list-disc list-inside text-slate-300 space-y-1">
              <li>Try single-word queries: <code className="text-amber-300">jackal</code>, <code className="text-amber-300">lion</code>, <code className="text-amber-300">monkey</code>, <code className="text-amber-300">riddle</code></li>
              <li>Try core motif keywords: <code className="text-amber-300 font-mono">well</code>, <code className="text-amber-300 font-mono">drum</code>, <code className="text-amber-300 font-mono">river</code>, <code className="text-amber-300 font-mono">mongoose</code></li>
              <li>Include tradition names: <code className="text-amber-300 font-mono">Panchatantra</code>, <code className="text-amber-300 font-mono">Hitopadesha</code>, <code className="text-amber-300 font-mono">Jataka</code></li>
            </ul>
          </div>

          <button
            onClick={() => handleChipClick('jackal')}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-amber-300 border border-slate-700 rounded-xl text-xs font-mono transition-all inline-flex items-center gap-2"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Reset to Default Search ('jackal')
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {results.map((result) => (
          <div
            key={result.id}
            className={`glass-panel p-5 transition-all space-y-3 ${
              result.user_feedback === 'relevant'
                ? 'border-emerald-500/50 bg-emerald-950/10'
                : result.user_feedback === 'non_relevant'
                ? 'border-rose-500/30 bg-rose-950/10 opacity-75'
                : 'hover:border-amber-500/40'
            }`}
          >
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
              <div className="space-y-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-amber-400 border border-slate-700">
                    {result.tale_type_id}
                  </span>
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                    {result.tale_id}
                  </span>
                  <span className="indic-tag bg-amber-500/10 text-amber-300 border-amber-500/30">
                    {result.tradition}
                  </span>
                  <span className="indic-tag bg-slate-800 text-slate-300 border-slate-700">
                    {result.region}
                  </span>
                </div>
                <h3 className="text-lg font-serif font-bold text-slate-100 hover:text-amber-300 transition-colors">
                  {result.title}
                </h3>
              </div>

              {/* Score Badge */}
              <div className="flex items-center gap-3 self-start">
                <div className="text-right">
                  <span className="text-[10px] uppercase font-mono text-slate-500 block">TF-IDF Score</span>
                  <span className="font-mono text-base font-bold text-amber-400">
                    {result.score.toFixed(4)}
                  </span>
                </div>
              </div>
            </div>

            {/* Source details */}
            <p className="text-xs text-slate-400 font-serif italic">
              Collection: <span className="text-slate-300 not-italic font-sans">{result.source_collection}</span> • Translator: {result.translator}
            </p>

            {/* Snippet */}
            <p className="text-sm text-slate-300 leading-relaxed font-serif bg-slate-950/50 p-3 rounded-lg border border-slate-900">
              "{result.snippet}"
            </p>

            {/* Bottom Controls & Zone Weight Breakdown */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-800/80 text-xs">
              <div className="flex items-center gap-2 text-slate-400 font-mono">
                <span>Matches:</span>
                {result.terms_matched.map((term) => (
                  <span key={term} className="bg-slate-900 px-2 py-0.5 rounded text-amber-400 border border-slate-800">
                    {term}
                  </span>
                ))}
                <span className="text-slate-600">|</span>
                <span className="text-slate-500">
                  Zone (T:{result.zone_weights.title} + B:{result.zone_weights.body})
                </span>
              </div>

              {/* Feedback buttons */}
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-slate-400 font-sans">Rocchio Feedback:</span>
                <button
                  onClick={() => toggleFeedback(result.id, 'relevant')}
                  className={`p-1.5 rounded-lg border transition-all flex items-center gap-1 text-xs font-semibold ${
                    result.user_feedback === 'relevant'
                      ? 'bg-emerald-500 text-slate-950 border-emerald-400 font-bold'
                      : 'bg-slate-900 text-slate-400 hover:text-emerald-400 border-slate-800'
                  }`}
                  title="Mark as Relevant for Rocchio"
                >
                  <ThumbsUp className="w-3.5 h-3.5" />
                  Relevant
                </button>
                <button
                  onClick={() => toggleFeedback(result.id, 'non_relevant')}
                  className={`p-1.5 rounded-lg border transition-all flex items-center gap-1 text-xs font-semibold ${
                    result.user_feedback === 'non_relevant'
                      ? 'bg-rose-500 text-slate-950 border-rose-400 font-bold'
                      : 'bg-slate-900 text-slate-400 hover:text-rose-400 border-slate-800'
                  }`}
                  title="Mark as Non-Relevant"
                >
                  <ThumbsDown className="w-3.5 h-3.5" />
                  Irrelevant
                </button>
              </div>
            </div>
          </div>
        ))}
        </div>
      )}
    </div>
  );
}
