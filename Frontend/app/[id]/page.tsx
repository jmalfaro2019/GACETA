import laws from "@/data/laws";
import ChatWidget from "@/components/ChatWidget";
import AnalysisActors from "@/components/AnalysisActors";
import prisma from "@/lib/prisma";
import { ArrowLeft, User, Building2, Calendar, ThumbsUp, ThumbsDown, Minus, Sparkles, FileText, Info, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Prisma } from "@prisma/client";

const STATUS_STYLES: Record<string, { bg: string; text: string }> = {
  amber: { bg: "rgba(251,191,36,0.1)", text: "#fbbf24" },
  green: { bg: "rgba(34,197,94,0.1)", text: "#22c55e" },
  blue: { bg: "rgba(59,130,246,0.1)", text: "#60a5fa" },
  gray: { bg: "rgba(148,163,184,0.1)", text: "#94a3b8" },
};

const PARTY_COLORS: Record<string, string> = {
  purple: "#a78bfa",
  red: "#f87171",
  orange: "#fb923c",
  blue: "#60a5fa",
  gray: "#94a3b8",
};

// Force dynamic rendering to avoid static generation issues in dev
export const dynamic = "force-dynamic";


export default async function LawDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  // Try to find in database first if id is numeric
  let dbDoc = null;
  if (!isNaN(Number(id))) {
    dbDoc = await prisma.document.findUnique({
      where: { id: parseInt(id) },
    });
  }

  const law = laws.find((l) => l.id === id);

  if (!dbDoc && !law) notFound();

  // If it's a real document from DB
  if (dbDoc) {
    const data = dbDoc.contenu_json as any;
    const meta = data.metadatos_generales;
    const details = data.detalles_especificos;

    const dateStr = new Date(dbDoc.date_creation).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });

    const uniqueConcepts = Array.from(new Set(meta?.palabras_clave as string[] || [])).slice(0, 5);

    return (
      <div className="max-w-4xl mx-auto space-y-8 pb-20">
        {/* Back */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm transition-colors hover:text-white text-slate-400"
        >
          <ArrowLeft size={15} />
          Back to list
        </Link>

        {/* ── Header ── */}
        <header
          className="rounded-3xl p-8 border relative overflow-hidden"
          style={{
            backgroundColor: "rgba(15, 23, 42, 0.6)",
            borderColor: "rgba(255, 255, 255, 0.08)",
            backdropFilter: "blur(12px)",
          }}
        >
          <div className="absolute top-0 right-0 p-8 opacity-10">
            <FileText size={120} />
          </div>

          <div className="relative">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold mb-6 bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Sparkles size={12} />
              {meta?.tipo_documento || "AI Analyzed Document"}
            </span>
            <h1 className="text-3xl md:text-4xl font-bold text-white leading-tight mb-4">
              {meta?.titulo_principal || dbDoc.titre}
            </h1>
            <p className="text-lg text-slate-400 leading-relaxed mb-6 italic">
              {meta?.resumen_ia}
            </p>
            <div className="flex flex-wrap gap-4 text-xs text-slate-500">
              <span className="flex items-center gap-1.5">
                <Calendar size={14} />
                Analyzed on {dateStr}
              </span>
              <span className="flex items-center gap-1.5 font-medium text-emerald-400">
                <ShieldCheck size={14} />
                High Precision Verified
              </span>
              {meta?.numero_gaceta && (
                <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10">
                   Gaceta No. {meta.numero_gaceta}
                </span>
              )}
            </div>
          </div>
        </header>

        {/* ── Content Sections ── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Dynamic Specialized Details Section */}
            {details && Object.keys(details).length > 0 && (
              <section className="rounded-3xl p-8 border border-blue-500/20 bg-blue-500/5">
                <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                   Specialized Details
                </h2>
                <div className="grid grid-cols-1 gap-6">
                  {/* Voting Records for Actas */}
                  {meta?.tipo_documento?.includes("Acta") && details.votaciones ? (
                    <div className="space-y-6">
                       {details.votaciones.map((v: any, i: number) => (
                         <div key={i} className="rounded-2xl p-6 bg-white/5 border border-white/10 space-y-4">
                            <h4 className="font-bold text-blue-300 text-sm italic">Voting on: {v.asunto_votado}</h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                               <div className="space-y-2">
                                  <p className="text-emerald-400 font-bold flex items-center gap-1"><ThumbsUp size={12}/> Votos a Favor:</p>
                                  <p className="text-slate-400">{v.votos_a_favor?.join(", ") || "None recorded"}</p>
                               </div>
                               <div className="space-y-2">
                                  <p className="text-red-400 font-bold flex items-center gap-1"><ThumbsDown size={12}/> Votos en Contra:</p>
                                  <p className="text-slate-400">{v.votos_en_contra?.join(", ") || "None recorded"}</p>
                               </div>
                               {v.ausencias_o_abstenciones && (
                                 <div className="md:col-span-2 space-y-2 pt-2 border-t border-white/5">
                                    <p className="text-slate-500 font-bold flex items-center gap-1"><Minus size={12}/> Ausencias / Abstenciones:</p>
                                    <p className="text-slate-400 text-[11px]">{v.ausencias_o_abstenciones?.join(", ")}</p>
                                 </div>
                               )}
                            </div>
                         </div>
                       ))}
                    </div>
                  ) : (
                    // Generic rendering for other types
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                       {Object.entries(details).map(([key, value]: [string, any]) => (
                         <div key={key}>
                            <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-1">{key.replace(/_/g, " ")}</p>
                            <p className="text-sm text-slate-300">
                               {Array.isArray(value) ? value.join(", ") : String(value)}
                            </p>
                         </div>
                       ))}
                    </div>
                  )}
                </div>
              </section>
            )}

            <section className="rounded-3xl p-8 border border-white/5 bg-white/[0.02]">
              <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                Document Body Analysis
              </h2>
              <div className="prose prose-invert max-w-none text-slate-300 leading-loose space-y-4">
                {(meta?.contenido_limpio || "").split("\n\n").map((para: string, i: number) => (
                  <p key={i}>{para}</p>
                ))}
              </div>
            </section>

            <section className="space-y-6">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                Actors & Signatories
              </h2>
              <AnalysisActors authorsList={meta?.autores_o_firmantes} />
            </section>
          </div>

          {/* Sidebar */}
          <aside className="space-y-8">
            <div className="rounded-3xl p-6 border border-white/5 bg-blue-500/5">
              <h3 className="text-sm font-bold text-white mb-4 uppercase tracking-widest">
                Key Concepts
              </h3>
              <div className="flex flex-wrap gap-2">
                {uniqueConcepts.map(
                  (concept, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-xs text-slate-300"
                    >
                      {concept}
                    </span>
                  )
                )}
              </div>
            </div>

            {/* AI Chat Widget */}
            <div className="sticky top-8 space-y-4">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-white uppercase tracking-widest">
                  Assistant
                </h3>
                <span className="px-1.5 py-0.5 rounded text-[10px] bg-indigo-500/20 text-indigo-300">
                  LIVE
                </span>
              </div>
              <ChatWidget
                initialHistory={[]}
                lawTitle={meta?.titulo_principal || dbDoc.titre}
              />
            </div>
          </aside>
        </div>
      </div>
    );
  }

  // Fallback to original mock data logic (if not in DB)
  if (!law) notFound();

  const status = STATUS_STYLES[law.statusColor] ?? STATUS_STYLES.gray;
  const partyColor = PARTY_COLORS[law.partyColor] ?? PARTY_COLORS.gray;

  const total = law.voting.favor + law.voting.against + law.voting.abstentions;
  const favorPct = Math.round((law.voting.favor / total) * 100);
  const againstPct = Math.round((law.voting.against / total) * 100);
  const abstPct = 100 - favorPct - againstPct;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Back */}
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-sm transition-colors hover:text-white"
        style={{ color: "var(--text-secondary)" }}
      >
        <ArrowLeft size={15} />
        Back to list
      </Link>

      {/* ── Header card ── */}
      <header
        className="rounded-2xl p-7 border"
        style={{
          backgroundColor: "var(--bg-card)",
          borderColor: "var(--border)",
          background: "linear-gradient(135deg, #131c30 0%, #1e1b4b 100%)",
        }}
      >
        <span
          className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold mb-4"
          style={{ backgroundColor: status.bg, color: status.text }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{ backgroundColor: status.text }}
          />
          {law.status}
        </span>
        <h1 className="text-2xl md:text-3xl font-bold text-white leading-snug">
          {law.title}
        </h1>
        <p className="mt-3 text-slate-400 leading-relaxed">{law.description}</p>
        <p className="mt-3 text-xs text-slate-500 flex items-center gap-1.5">
          <Calendar size={12} />
          Filed on {new Date(law.filingDate).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}
        </p>
      </header>

      {/* ── Author card ── */}
      <section
        className="rounded-2xl p-6 border flex items-start gap-5"
        style={{ backgroundColor: "var(--bg-card)", borderColor: "var(--border)" }}
      >
        {/* Avatar placeholder */}
        <div
          className="w-14 h-14 rounded-full flex-shrink-0 flex items-center justify-center text-2xl font-bold"
          style={{ backgroundColor: "rgba(99,102,241,0.2)", color: "#818cf8" }}
        >
          {law.author.split(" ").slice(-1)[0][0]}
        </div>
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-widest mb-1">
            Bill Author
          </p>
          <p
            className="text-lg font-semibold"
            style={{ color: "var(--text-primary)" }}
          >
            {law.author}
          </p>
          <span
            className="inline-flex items-center gap-1.5 mt-1 text-sm font-medium"
            style={{ color: partyColor }}
          >
            <Building2 size={13} />
            {law.party}
          </span>
        </div>
      </section>

      {/* ── Voting stats ── */}
      <section
        className="rounded-2xl p-6 border space-y-5"
        style={{ backgroundColor: "var(--bg-card)", borderColor: "var(--border)" }}
      >
        <h2 className="text-base font-semibold text-white">
          Voting Statistics
        </h2>

        {/* Segmented bar */}
        <div className="flex rounded-full overflow-hidden h-4 bg-slate-800 gap-0.5">
          <div
            className="bg-green-500 rounded-full transition-all"
            style={{ width: `${favorPct}%` }}
            title={`In favor: ${law.voting.favor}`}
          />
          <div
            className="bg-red-500 rounded-full transition-all"
            style={{ width: `${againstPct}%` }}
            title={`Against: ${law.voting.against}`}
          />
          <div
            className="bg-slate-500 rounded-full transition-all"
            style={{ width: `${abstPct}%` }}
            title={`Abstentions: ${law.voting.abstentions}`}
          />
        </div>

        {/* Legend */}
        <div className="grid grid-cols-3 gap-4">
          {[
            {
              label: "In Favor",
              value: law.voting.favor,
              pct: favorPct,
              color: "#4ade80",
              icon: ThumbsUp,
              bg: "rgba(74,222,128,0.08)",
            },
            {
              label: "Against",
              value: law.voting.against,
              pct: againstPct,
              color: "#f87171",
              icon: ThumbsDown,
              bg: "rgba(248,113,113,0.08)",
            },
            {
              label: "Abstentions",
              value: law.voting.abstentions,
              pct: abstPct,
              color: "#94a3b8",
              icon: Minus,
              bg: "rgba(148,163,184,0.08)",
            },
          ].map(({ label, value, pct, color, icon: Icon, bg }) => (
            <div
              key={label}
              className="rounded-xl p-4 text-center"
              style={{ backgroundColor: bg }}
            >
              <Icon size={18} style={{ color }} className="mx-auto mb-2" />
              <p className="text-2xl font-bold" style={{ color }}>
                {value}
              </p>
              <p className="text-xs text-slate-400 mt-0.5">{label}</p>
              <p className="text-xs font-semibold mt-1" style={{ color }}>
                {pct}%
              </p>
            </div>
          ))}
        </div>

        <p className="text-xs text-center text-slate-500">
          Total votes recorded: {total}
        </p>
      </section>

      {/* ── AI Chat ── */}
      <section className="space-y-3">
        <div className="flex items-center gap-2">
          <h2 className="text-base font-semibold text-white">AI Assistant</h2>
          <span className="px-2 py-0.5 rounded-full text-xs bg-blue-600/20 text-blue-400 border border-blue-500/30">
            Beta
          </span>
        </div>
        <ChatWidget initialHistory={law.chatHistory} lawTitle={law.title} />
      </section>
    </div>
  );
}
