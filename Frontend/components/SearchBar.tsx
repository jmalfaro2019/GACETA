"use client";

import { useState, useEffect, useRef } from "react";
import { Search, Loader2, FileText, ChevronRight, X } from "lucide-react";
import { apiClient, SearchResult } from "@/lib/api-client";
import Link from "next/link";

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close results when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setShowResults(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Handle Search Execution
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (query.length >= 2) {
        setIsSearching(true);
        const data = await apiClient.searchDocuments(query);
        setResults(data);
        setIsSearching(false);
        setShowResults(true);
      } else {
        setResults([]);
        setShowResults(false);
      }
    }, 400); // Debounce

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div className="relative w-full max-w-2xl mx-auto z-50" ref={containerRef}>
      <div className="relative group">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <Search size={18} className="text-slate-500 group-focus-within:text-blue-400 transition-colors" />
        </div>
        <input
          type="text"
          className="block w-full pl-11 pr-12 py-4 bg-slate-900/50 border border-white/10 rounded-2xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50 transition-all backdrop-blur-xl"
          placeholder="Search laws, keywords or authors (e.g. 'reforma', 'salud')..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.length >= 2 && setShowResults(true)}
        />
        {query && (
          <button
            onClick={() => setQuery("")}
            className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-500 hover:text-white transition-colors"
          >
            <X size={18} />
          </button>
        )}
      </div>

      {/* Results Dropdown */}
      {showResults && (
        <div className="absolute top-full mt-2 w-full bg-slate-900/95 border border-white/10 rounded-2xl shadow-2xl backdrop-blur-2xl overflow-hidden max-h-[400px] flex flex-col">
          <div className="p-3 border-b border-white/5 flex items-center justify-between">
            <span className="text-[10px] uppercase tracking-widest font-bold text-slate-500">
              {isSearching ? "Searching ParadeDB..." : `${results.length} results found`}
            </span>
            {isSearching && <Loader2 size={14} className="animate-spin text-blue-400" />}
          </div>

          <div className="overflow-y-auto custom-scrollbar">
            {results.length > 0 ? (
              results.map((res) => (
                <Link
                  key={res.id}
                  href={`/${res.id}`}
                  className="flex items-start gap-4 p-4 hover:bg-white/5 transition-colors border-b border-white/5 last:border-0 group"
                  onClick={() => setShowResults(false)}
                >
                  <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 group-hover:bg-blue-500/20 transition-colors shrink-0">
                    <FileText size={16} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-300 font-bold uppercase tracking-wider">
                        {res.tipo_documento || "Document"}
                      </span>
                    </div>
                    <h4 className="text-sm font-semibold text-white truncate group-hover:text-blue-400 transition-colors">
                      {res.titre}
                    </h4>
                    <p className="text-xs text-slate-500 line-clamp-1 mt-0.5 font-light italic">
                      {res.resumen_ia}
                    </p>
                  </div>
                  <ChevronRight size={14} className="text-slate-600 group-hover:translate-x-0.5 transition-transform" />
                </Link>
              ))
            ) : !isSearching && (
              <div className="p-8 text-center">
                <p className="text-sm text-slate-500">No results found for "{query}"</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
