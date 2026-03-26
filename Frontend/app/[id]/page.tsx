import laws from "@/data/laws";
import ChatWidget from "@/components/ChatWidget";
import { ArrowLeft, User, Building2, Calendar, ThumbsUp, ThumbsDown, Minus } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";

const STATUS_STYLES: Record<string, { bg: string; text: string }> = {
  amber: { bg: "rgba(251,191,36,0.1)", text: "#fbbf24" },
  green: { bg: "rgba(34,197,94,0.1)", text: "#22c55e" },
  blue: { bg: "rgba(59,130,246,0.1)", text: "#60a5fa" },
  gray: { bg: "rgba(148,163,184,0.1)", text: "#94a3b8" },
};

const PARTIDO_COLORS: Record<string, string> = {
  purple: "#a78bfa",
  red: "#f87171",
  orange: "#fb923c",
  blue: "#60a5fa",
  gray: "#94a3b8",
};

export function generateStaticParams() {
  return laws.map((l) => ({ id: l.id }));
}

export default async function LawDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const law = laws.find((l) => l.id === id);
  if (!law) notFound();

  const status = STATUS_STYLES[law.estadoColor] ?? STATUS_STYLES.gray;
  const partidoColor = PARTIDO_COLORS[law.partidoColor] ?? PARTIDO_COLORS.gray;

  const total = law.votacion.favor + law.votacion.contra + law.votacion.abstenciones;
  const favorPct = Math.round((law.votacion.favor / total) * 100);
  const contraPct = Math.round((law.votacion.contra / total) * 100);
  const abstPct = 100 - favorPct - contraPct;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Back */}
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-sm transition-colors hover:text-white"
        style={{ color: "var(--text-secondary)" }}
      >
        <ArrowLeft size={15} />
        Volver al listado
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
          {law.estado}
        </span>
        <h1 className="text-2xl md:text-3xl font-bold text-white leading-snug">
          {law.titulo}
        </h1>
        <p className="mt-3 text-slate-400 leading-relaxed">{law.descripcion}</p>
        <p className="mt-3 text-xs text-slate-500 flex items-center gap-1.5">
          <Calendar size={12} />
          Radicado el {new Date(law.fechaRadicacion).toLocaleDateString("es-CO", { year: "numeric", month: "long", day: "numeric" })}
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
          {law.autor.split(" ").slice(-1)[0][0]}
        </div>
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-widest mb-1">
            Autor del proyecto
          </p>
          <p
            className="text-lg font-semibold"
            style={{ color: "var(--text-primary)" }}
          >
            {law.autor}
          </p>
          <span
            className="inline-flex items-center gap-1.5 mt-1 text-sm font-medium"
            style={{ color: partidoColor }}
          >
            <Building2 size={13} />
            {law.partido}
          </span>
        </div>
      </section>

      {/* ── Voting stats ── */}
      <section
        className="rounded-2xl p-6 border space-y-5"
        style={{ backgroundColor: "var(--bg-card)", borderColor: "var(--border)" }}
      >
        <h2 className="text-base font-semibold text-white">
          Estadísticas de Votación
        </h2>

        {/* Segmented bar */}
        <div className="flex rounded-full overflow-hidden h-4 bg-slate-800 gap-0.5">
          <div
            className="bg-green-500 rounded-full transition-all"
            style={{ width: `${favorPct}%` }}
            title={`A favor: ${law.votacion.favor}`}
          />
          <div
            className="bg-red-500 rounded-full transition-all"
            style={{ width: `${contraPct}%` }}
            title={`En contra: ${law.votacion.contra}`}
          />
          <div
            className="bg-slate-500 rounded-full transition-all"
            style={{ width: `${abstPct}%` }}
            title={`Abstenciones: ${law.votacion.abstenciones}`}
          />
        </div>

        {/* Legend */}
        <div className="grid grid-cols-3 gap-4">
          {[
            {
              label: "A favor",
              value: law.votacion.favor,
              pct: favorPct,
              color: "#4ade80",
              icon: ThumbsUp,
              bg: "rgba(74,222,128,0.08)",
            },
            {
              label: "En contra",
              value: law.votacion.contra,
              pct: contraPct,
              color: "#f87171",
              icon: ThumbsDown,
              bg: "rgba(248,113,113,0.08)",
            },
            {
              label: "Abstenciones",
              value: law.votacion.abstenciones,
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
          Total de votos registrados: {total}
        </p>
      </section>

      {/* ── AI Chat ── */}
      <section className="space-y-3">
        <div className="flex items-center gap-2">
          <h2 className="text-base font-semibold text-white">Asistente IA</h2>
          <span className="px-2 py-0.5 rounded-full text-xs bg-blue-600/20 text-blue-400 border border-blue-500/30">
            Beta
          </span>
        </div>
        <ChatWidget initialHistory={law.chatHistory} lawTitle={law.titulo} />
      </section>
    </div>
  );
}
