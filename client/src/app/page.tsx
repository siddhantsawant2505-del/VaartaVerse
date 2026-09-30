'use client';

import { useState } from 'react';
import {
  Search,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  BookOpen,
  MapPin,
  User,
  Layers,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Terminal,
  Zap,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface TaleResult {
  id: string;
  tale_id: string;
  tale_type: string;
  title: string;
  source_collection: string;
  region: string;
  tradition: string;
  translator: string;
  score: number;
  snippet: string;
  terms_matched: string[];
  user_feedback?: 'relevant' | 'non_relevant' | null;
}

interface ParsedInfo {
  mode: string;
  normalized_query: string;
  stems: string[];
  entities: { traditions: string[]; regions: string[]; atu_codes: string[] };
  expansions: Record<string, string[]>;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const EXAMPLE_QUERIES = [
  { label: 'Akbar & Birbal', query: 'Birbal cooking khichdi cold lake', bool: false },
  { label: 'Tenali Rama', query: 'Tenali Raman and Persian horse trader', bool: false },
  { label: 'Ramayana', query: 'Hanuman brings Sanjeevani mountain for Lakshmana', bool: false },
  { label: 'Mahabharata', query: 'Yaksha Prashna riddles of the pool Yudhishthira', bool: false },
  { label: 'Ekalavya', query: 'Ekalavya archery thumb guru dakshina', bool: false },
  { label: 'Blue Jackal', query: 'blue jackal indigo vat forest king', bool: false },
  { label: 'Brahmin & Mongoose', query: 'brahmin mongoose snake baby', bool: false },
  { label: 'Boolean: Fox or Jackal', query: '(jackal OR hare) AND lion AND NOT tiger', bool: true },
];

const IR_APIS = ['http://localhost:8000', 'http://localhost:5000/api/ir'];

async function fetchWithFallback(path: string, options: RequestInit) {
  let lastError: any = null;
  for (const base of IR_APIS) {
    try {
      const res = await fetch(`${base}${path}`, options);
      return res;
    } catch (err) {
      lastError = err;
    }
  }
  throw lastError;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [isBooleanMode, setIsBooleanMode] = useState(false);
  const [isBm25Mode, setIsBm25Mode] = useState(false);
  const [expandSynonyms, setExpandSynonyms] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<TaleResult[]>([]);
  const [parsedInfo, setParsedInfo] = useState<ParsedInfo | null>(null);
  const [showParsed, setShowParsed] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [hasSearched, setHasSearched] = useState(false);

  // -------------------------------------------------------------------------
  // Search
  // -------------------------------------------------------------------------

  const runSearch = async (q: string, bool: boolean, bm25: boolean) => {
    if (!q.trim()) return;
    setIsSearching(true);
    setErrorMsg('');
    setHasSearched(true);

    try {
      const path = bool
        ? '/search/boolean'
        : bm25
        ? '/search/bm25'
        : '/search/nl-query';
      const payload = bool
        ? { query: q }
        : { query: q, top_k: 10, expand_synonyms: expandSynonyms };

      const res = await fetchWithFallback(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        // Surface the engine's real error (e.g. boolean parse errors → 422)
        let detail = `${res.status} ${res.statusText}`;
        try {
          const body = await res.json();
          const d = body?.detail;
          if (typeof d === 'string') detail = d;
          else if (d?.message) detail = d.message;
          else if (Array.isArray(d) && d[0]?.msg) detail = d[0].msg;
        } catch {
          /* keep status text */
        }
        setErrorMsg(`Engine error: ${detail}`);
        return;
      }

      const data = await res.json();

      // Update parsed info
      if (data.parsed) {
        const p = data.parsed;
        setParsedInfo({
          mode: p.mode || 'vsm',
          normalized_query: p.normalized_query || q,
          stems: p.stemmed_terms || (p.normalized_query ? p.normalized_query.split(/\s+/).filter(Boolean) : []),
          entities: p.entities || { traditions: [], regions: [], atu_codes: [] },
          expansions: p.expansions || {},
        });
      } else {
        setParsedInfo({
          mode: bool ? 'boolean' : bm25 ? 'bm25' : 'vsm',
          normalized_query: q,
          stems: q.toLowerCase().split(/\s+/).filter(Boolean),
          entities: { traditions: [], regions: [], atu_codes: [] },
          expansions: {},
        });
      }

      const rawResults: any[] = (data.results || []).filter((r: any) => r && !r.error && (r.title || r.tale_id));
      const mapped: TaleResult[] = rawResults.map((r, idx) => ({
        id: r.doc_id || r.tale_id || String(idx + 1),
        tale_id: r.tale_id || r.doc_id || `TALE-${idx + 1}`,
        tale_type: r.tale_type && r.tale_type !== 'UNKNOWN' ? r.tale_type : '',
        title: r.title || 'Folk Tale Variant',
        source_collection: r.source_collection || '',
        region: r.region && !r.region.toLowerCase().includes('unknown') ? r.region : '',
        tradition: r.tradition && !r.tradition.toLowerCase().includes('unknown') ? r.tradition : '',
        translator: r.translator && !r.translator.toLowerCase().includes('unknown') ? r.translator : '',
        score: typeof r.score === 'number' ? r.score : 0,
        snippet: r.snippet || (r.raw_text ? r.raw_text.slice(0, 200) + '…' : ''),
        terms_matched: r.terms_matched || [],
        user_feedback: null,
      }));

      setResults(mapped);
    } catch (err) {
      setErrorMsg('Cannot reach the search service. Make sure the server (:5000) and IR engine (:8000) are running.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    runSearch(query, isBooleanMode, isBm25Mode);
  };

  const handleExample = (q: string, bool: boolean) => {
    setQuery(q);
    setIsBooleanMode(bool);
    setIsBm25Mode(false);
    runSearch(q, bool, false);
  };

  // -------------------------------------------------------------------------
  // Feedback
  // -------------------------------------------------------------------------

  const toggleFeedback = (id: string, type: 'relevant' | 'non_relevant') => {
    setResults((prev) =>
      prev.map((r) =>
        r.id === id ? { ...r, user_feedback: r.user_feedback === type ? null : type } : r
      )
    );
  };

  const relevantIds = results.filter((r) => r.user_feedback === 'relevant').map((r) => r.tale_id);
  const nonRelevantIds = results.filter((r) => r.user_feedback === 'non_relevant').map((r) => r.tale_id);
  const hasFeedback = relevantIds.length > 0 || nonRelevantIds.length > 0;

  const applyRocchio = async () => {
    setIsSearching(true);
    try {
      const res = await fetchWithFallback('/search/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, relevant_ids: relevantIds, non_relevant_ids: nonRelevantIds, top_k: 10 }),
      });
      if (res.ok) {
        const data = await res.json();
        const rawResults: any[] = (data.results || []).filter((r: any) => r && !r.error && (r.title || r.tale_id));
        const mapped: TaleResult[] = rawResults.map((r, idx) => ({
          id: r.doc_id || r.tale_id || String(idx + 1),
          tale_id: r.tale_id || r.doc_id || `TALE-${idx + 1}`,
          tale_type: r.tale_type && r.tale_type !== 'UNKNOWN' ? r.tale_type : '',
          title: r.title || 'Folk Tale Variant',
          source_collection: r.source_collection || '',
          region: r.region && !r.region.toLowerCase().includes('unknown') ? r.region : '',
          tradition: r.tradition && !r.tradition.toLowerCase().includes('unknown') ? r.tradition : '',
          translator: r.translator && !r.translator.toLowerCase().includes('unknown') ? r.translator : '',
          score: typeof r.score === 'number' ? r.score : 0,
          snippet: r.snippet || '',
          terms_matched: r.terms_matched || [],
          user_feedback: results.find((e) => e.tale_id === r.tale_id)?.user_feedback ?? null,
        }));
        if (mapped.length > 0) setResults(mapped);
      }
    } catch {
      // fallback local re-rank
      setResults((prev) =>
        [...prev].sort((a, b) => {
          const sa = a.score + (a.user_feedback === 'relevant' ? 0.15 : a.user_feedback === 'non_relevant' ? -0.2 : 0);
          const sb = b.score + (b.user_feedback === 'relevant' ? 0.15 : b.user_feedback === 'non_relevant' ? -0.2 : 0);
          return sb - sa;
        })
      );
    } finally {
      setIsSearching(false);
    }
  };

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  return (
    <div className="space-y-6 max-w-4xl mx-auto">

      {/* ---- Header ---- */}
      <div className="text-center space-y-1 pt-2">
        <h1 className="text-3xl font-serif font-bold text-slate-100">
          VaartaVerse Search
        </h1>
        <p className="text-sm text-slate-400">
          Search Indian folk tale variants — Panchatantra, Jataka, Hitopadesha and more
        </p>
      </div>

      {/* ---- Mode Toggle ---- */}
      <div className="flex justify-center">
        <div className="inline-flex items-center bg-slate-900 border border-slate-800 rounded-xl p-1 gap-1">
          <button
            onClick={() => { setIsBooleanMode(false); setIsBm25Mode(false); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all ${
              !isBooleanMode && !isBm25Mode
                ? 'bg-amber-500 text-slate-950 shadow font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            Smart Search
          </button>
          <button
            onClick={() => { setIsBooleanMode(false); setIsBm25Mode(true); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all ${
              isBm25Mode
                ? 'bg-amber-500 text-slate-950 shadow font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Zap className="w-4 h-4" />
            BM25
          </button>
          <button
            onClick={() => { setIsBooleanMode(true); setIsBm25Mode(false); }}
            className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all ${
              isBooleanMode
                ? 'bg-amber-500 text-slate-950 shadow font-semibold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Terminal className="w-4 h-4" />
            Boolean (AND/OR/NOT)
          </button>
        </div>
      </div>

      {/* Mode hint */}
      <p className="text-center text-xs text-slate-500">
        {isBooleanMode
          ? 'Use AND, OR, NOT and parentheses — e.g. (jackal OR fox) AND lion AND NOT tiger'
          : isBm25Mode
          ? 'BM25 ranking: saturating term frequency, length normalization, title boost'
          : 'Type anything naturally — a keyword, a character, a place, or a full sentence'}
      </p>

      {/* ---- Search Box ---- */}
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="relative flex items-center gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-amber-500 pointer-events-none" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={
                isBooleanMode
                  ? '(jackal OR hare) AND lion AND NOT tiger'
                  : 'Try: jackal well, monkey crocodile, Panchatantra…'
              }
              className="w-full bg-slate-900 border-2 border-slate-700 rounded-2xl py-3.5 pl-12 pr-4 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 transition-colors text-base"
            />
          </div>
          <button
            type="submit"
            disabled={isSearching || !query.trim()}
            className="px-6 py-3.5 rounded-2xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 disabled:cursor-not-allowed text-slate-950 font-bold text-sm transition-all flex items-center gap-2 whitespace-nowrap"
          >
            {isSearching ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            Search
          </button>
        </div>

        {/* Example chips + synonym toggle */}
        <div className="flex flex-wrap gap-2 justify-center items-center">
          <span className="text-xs text-slate-500 self-center mr-1">Examples:</span>
          {EXAMPLE_QUERIES.map((ex) => (
            <button
              key={ex.label}
              type="button"
              onClick={() => handleExample(ex.query, ex.bool)}
              className={`px-3 py-1 text-xs rounded-full border transition-all ${
                ex.bool
                  ? 'bg-slate-900 border-indigo-700/60 text-indigo-300 hover:bg-indigo-900/30'
                  : 'bg-slate-900 border-slate-700 text-amber-300 hover:bg-slate-800'
              }`}
            >
              {ex.bool && <span className="mr-1 opacity-60">bool:</span>}
              {ex.label}
            </button>
          ))}
          {!isBooleanMode && (
            <label
              className="flex items-center gap-1.5 text-xs text-slate-400 cursor-pointer select-none ml-2 px-3 py-1 rounded-full border border-slate-800 bg-slate-900 hover:border-emerald-700/50 transition-all"
              title="Expand query terms with WordNet synonyms (weighted below your original words)"
            >
              <input
                type="checkbox"
                checked={expandSynonyms}
                onChange={(e) => setExpandSynonyms(e.target.checked)}
                className="accent-emerald-500 w-3.5 h-3.5"
              />
              <Sparkles className="w-3 h-3 text-emerald-400" />
              Synonym expansion
            </label>
          )}
        </div>
      </form>

      {/* ---- Error ---- */}
      {errorMsg && (
        <div className="bg-rose-950/40 border border-rose-500/40 rounded-xl p-4 text-sm text-rose-300">
          ⚠ {errorMsg}
        </div>
      )}

      {/* ---- Feedback Banner ---- */}
      {hasFeedback && (
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 flex items-center justify-between gap-4">
          <div className="text-sm text-amber-200">
            <span className="font-semibold">Relevance feedback:</span>{' '}
            {relevantIds.length} relevant · {nonRelevantIds.length} irrelevant marked.
            Apply to get better-tuned results.
          </div>
          <button
            onClick={applyRocchio}
            disabled={isSearching}
            className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg text-xs transition-all flex items-center gap-2 whitespace-nowrap"
          >
            <Zap className="w-3.5 h-3.5" />
            Re-rank Results
          </button>
        </div>
      )}

      {/* ---- Results count + parser toggle ---- */}
      {hasSearched && !isSearching && (
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>
            {results.length === 0 ? 'No results' : `${results.length} tale${results.length !== 1 ? 's' : ''} found`}
            {parsedInfo && ` · Mode: ${parsedInfo.mode.toUpperCase()}`}
          </span>
          {parsedInfo && (
            <button
              onClick={() => setShowParsed(!showParsed)}
              className="flex items-center gap-1 text-amber-400/70 hover:text-amber-400 transition-colors"
            >
              Query details {showParsed ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>
      )}

      {/* ---- Parsed info (collapsible) ---- */}
      {showParsed && parsedInfo && (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-xs space-y-2">
          <div className="text-slate-400">
            <span className="text-slate-500">Normalized:</span>{' '}
            <span className="text-emerald-400">{parsedInfo.normalized_query}</span>
          </div>
          {parsedInfo.stems.length > 0 && (
            <div className="flex flex-wrap gap-1">
              <span className="text-slate-500 self-center">Stems:</span>
              {parsedInfo.stems.map((s) => (
                <span key={s} className="bg-slate-800 px-2 py-0.5 rounded text-amber-300">{s}</span>
              ))}
            </div>
          )}
          {Object.keys(parsedInfo.expansions).length > 0 && (
            <div className="flex flex-wrap gap-1">
              <span className="text-slate-500 self-center">Synonyms (0.3×):</span>
              {Object.entries(parsedInfo.expansions).map(([term, syns]) => (
                <span key={term} className="flex items-center gap-0.5">
                  <span className="bg-slate-800 px-2 py-0.5 rounded text-amber-300">{term}</span>
                  <span className="text-slate-600">→</span>
                  {syns.map((syn) => (
                    <span key={syn} className="bg-emerald-900/40 border border-emerald-700/40 px-2 py-0.5 rounded text-emerald-300">{syn}</span>
                  ))}
                </span>
              ))}
            </div>
          )}
          {parsedInfo.entities.traditions.length > 0 && (
            <div className="text-slate-400">
              Detected tradition: <span className="text-amber-300">{parsedInfo.entities.traditions.join(', ')}</span>
            </div>
          )}
          {parsedInfo.entities.regions.length > 0 && (
            <div className="text-slate-400">
              Detected region: <span className="text-amber-300">{parsedInfo.entities.regions.join(', ')}</span>
            </div>
          )}
        </div>
      )}

      {/* ---- Results ---- */}
      {hasSearched && !isSearching && results.length === 0 && !errorMsg && (
        <div className="glass-panel p-10 rounded-2xl text-center space-y-3 border border-slate-800">
          <Search className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="text-lg font-semibold text-slate-300">No matching tales found</h3>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            Try a different keyword, a character name, or click one of the example queries above.
          </p>
        </div>
      )}

      {!hasSearched && (
        <div className="glass-panel p-10 rounded-2xl text-center space-y-3 border border-slate-800/50">
          <BookOpen className="w-10 h-10 text-amber-500/40 mx-auto" />
          <p className="text-slate-500 text-sm">Enter a query or click an example to begin searching</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-3">
          {results.map((result) => (
            <ResultCard
              key={result.id}
              result={result}
              onFeedback={toggleFeedback}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Result Card
// ---------------------------------------------------------------------------

function ResultCard({
  result,
  onFeedback,
}: {
  result: TaleResult;
  onFeedback: (id: string, type: 'relevant' | 'non_relevant') => void;
}) {
  const feedbackBorder =
    result.user_feedback === 'relevant'
      ? 'border-emerald-500/50 bg-emerald-950/10'
      : result.user_feedback === 'non_relevant'
      ? 'border-rose-500/30 bg-rose-950/10 opacity-70'
      : 'hover:border-amber-500/30';

  return (
    <div className={`glass-panel p-5 space-y-3 transition-all ${feedbackBorder}`}>
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1.5 flex-1 min-w-0">
          {/* Badges */}
          <div className="flex flex-wrap gap-1.5 text-xs">
            {result.tale_type && (
              <span className="px-2 py-0.5 rounded bg-slate-800 text-amber-400 font-mono border border-slate-700">
                {result.tale_type}
              </span>
            )}
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono border border-slate-700">
              {result.tale_id}
            </span>
            {result.tradition && (
              <span className="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20">
                {result.tradition}
              </span>
            )}
          </div>
          {/* Title */}
          <h3 className="text-base font-serif font-bold text-slate-100 leading-snug">
            {result.title}
          </h3>
        </div>

        {/* Score */}
        <div className="text-right shrink-0">
          <div className="text-[10px] text-slate-500 uppercase font-mono">Score</div>
          <div className="font-mono font-bold text-amber-400 text-sm">{result.score.toFixed(4)}</div>
        </div>
      </div>

      {/* Meta row */}
      <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-400">
        {result.region && (
          <span className="flex items-center gap-1">
            <MapPin className="w-3 h-3 text-slate-500" /> {result.region}
          </span>
        )}
        {result.source_collection && (
          <span className="flex items-center gap-1">
            <BookOpen className="w-3 h-3 text-slate-500" /> {result.source_collection}
          </span>
        )}
        {result.translator && (
          <span className="flex items-center gap-1">
            <User className="w-3 h-3 text-slate-500" /> {result.translator}
          </span>
        )}
      </div>

      {/* Snippet */}
      {result.snippet && (
        <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/50 rounded-lg p-3 border border-slate-800/60 font-serif">
          "{result.snippet}"
        </p>
      )}

      {/* Footer: matched terms + feedback */}
      <div className="flex items-center justify-between gap-2 pt-1 flex-wrap">
        {result.terms_matched.length > 0 && (
          <div className="flex items-center gap-1.5 text-xs text-slate-500 flex-wrap">
            <Layers className="w-3.5 h-3.5" />
            {result.terms_matched.map((t) => (
              <span key={t} className="px-1.5 py-0.5 rounded bg-slate-900 text-amber-400/80 border border-slate-800 font-mono">
                {t}
              </span>
            ))}
          </div>
        )}

        {/* Feedback */}
        <div className="flex items-center gap-2 text-xs ml-auto">
          <span className="text-slate-600">Was this relevant?</span>
          <button
            onClick={() => onFeedback(result.id, 'relevant')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-lg border transition-all ${
              result.user_feedback === 'relevant'
                ? 'bg-emerald-500 border-emerald-400 text-slate-950 font-bold'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-emerald-400 hover:border-emerald-700'
            }`}
          >
            <ThumbsUp className="w-3.5 h-3.5" /> Yes
          </button>
          <button
            onClick={() => onFeedback(result.id, 'non_relevant')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-lg border transition-all ${
              result.user_feedback === 'non_relevant'
                ? 'bg-rose-500 border-rose-400 text-slate-950 font-bold'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-rose-400 hover:border-rose-700'
            }`}
          >
            <ThumbsDown className="w-3.5 h-3.5" /> No
          </button>
        </div>
      </div>
    </div>
  );
}
