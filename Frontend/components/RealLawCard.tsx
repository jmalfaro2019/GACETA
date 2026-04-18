"use client";

import { FileText, Tag, Calendar, ChevronRight, Info } from "lucide-react";
import Link from "next/link";

interface RealLawJson {
  metadatos_generales: {
    numero_gaceta: string | null;
    fecha_publicacion: string | null;
    tipo_documento: string | null;
    titulo_principal: string;
    autores_o_firmantes: string[];
    palabras_clave: string[];
    resumen_ia: string;
    contenido_limpio: string;
  };
  detalles_especificos: any;
}

interface DocumentProps {
  document: {
    id: number;
    titre: string;
    contenu_json: any;
    date_creation: Date;
  };
}

export default function RealLawCard({ document }: DocumentProps) {
  const data = document.contenu_json as RealLawJson;
  const meta = data.metadatos_generales;
  
  const dateStr = new Date(document.date_creation).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  // Extract first 5 unique key concepts as requested
  const uniqueConcepts = Array.from(new Set(meta?.palabras_clave || [])).slice(0, 5);

  return (
    <article
      className="relative group rounded-3xl overflow-hidden border transition-all duration-500 hover:shadow-[0_20px_50px_rgba(30,27,75,0.4)]"
      style={{
        backgroundColor: "rgba(15, 23, 42, 0.6)",
        borderColor: "rgba(255, 255, 255, 0.08)",
        backdropFilter: "blur(12px)",
      }}
    >
      {/* Top gradient highlight */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/50 to-transparent" />
      
      <div className="p-6 flex flex-col h-full gap-5">
        {/* Header with Icon and Date */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400 group-hover:bg-blue-500/20 transition-colors">
              <FileText size={18} />
            </div>
            <span className="text-[10px] uppercase tracking-widest font-bold text-slate-500">
              {meta?.tipo_documento || "Analyzed Document"}
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
            <Calendar size={12} />
            {dateStr}
          </div>
        </div>

        {/* Title */}
        <div>
          <h2 className="text-lg font-bold text-white line-clamp-2 leading-tight group-hover:text-blue-400 transition-colors duration-300">
            {meta?.titulo_principal || document.titre}
          </h2>
        </div>

        {/* Description snippet (Resumen IA) */}
        <p className="text-sm text-slate-400 leading-relaxed line-clamp-3">
          {meta?.resumen_ia}
        </p>

        {/* Concepts / Tags (Limit to 5) */}
        <div className="flex flex-wrap gap-2">
          {uniqueConcepts.map((concept, index) => (
            <span
              key={index}
              className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-[10px] font-medium bg-indigo-500/5 text-indigo-300 border border-indigo-500/10 group-hover:border-indigo-500/30 transition-all"
            >
              <Tag size={10} />
              {concept}
            </span>
          ))}
        </div>

        {/* Action button */}
        <div className="mt-auto pt-4 flex items-center justify-between border-t border-white/5">
          <Link
            href={`/${document.id}`}
            className="flex items-center gap-1.5 text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors group/btn"
          >
            Explore Full Analysis
            <ChevronRight size={14} className="group-hover/btn:translate-x-0.5 transition-transform" />
          </Link>
          <div className="flex items-center gap-1 opacity-40 hover:opacity-100 transition-opacity cursor-help" title="High precision AI analysis">
             <Info size={12} className="text-slate-400" />
             <span className="text-[10px] text-slate-400">AI Verified {meta?.numero_gaceta ? `(Gaceta No. ${meta.numero_gaceta})` : ""}</span>
          </div>
        </div>
      </div>

      {/* Background glow effect on hover */}
      <div className="absolute -bottom-20 -right-20 w-40 h-40 bg-blue-600/10 blur-[80px] rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
    </article>
  );
}
