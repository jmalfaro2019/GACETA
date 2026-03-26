"use client";

import { Law } from "@/data/laws";
import { ArrowRight, User, Building2 } from "lucide-react";
import Link from "next/link";

const STATUS_STYLES: Record<string, { bg: string; text: string; dot: string }> =
  {
    amber: {
      bg: "rgba(251,191,36,0.1)",
      text: "#fbbf24",
      dot: "#fbbf24",
    },
    green: {
      bg: "rgba(34,197,94,0.1)",
      text: "#22c55e",
      dot: "#22c55e",
    },
    blue: {
      bg: "rgba(59,130,246,0.1)",
      text: "#60a5fa",
      dot: "#60a5fa",
    },
    gray: {
      bg: "rgba(148,163,184,0.1)",
      text: "#94a3b8",
      dot: "#94a3b8",
    },
  };

const PARTY_COLORS: Record<string, string> = {
  purple: "#a78bfa",
  red: "#f87171",
  orange: "#fb923c",
  blue: "#60a5fa",
  gray: "#94a3b8",
};

export default function LawCard({ law }: { law: Law }) {
  const status = STATUS_STYLES[law.statusColor] ?? STATUS_STYLES.gray;
  const partyColor =
    PARTY_COLORS[law.partyColor] ?? PARTY_COLORS.gray;

  const total = law.voting.favor + law.voting.against + law.voting.abstentions;
  const favorPct = Math.round((law.voting.favor / total) * 100);
  const againstPct = Math.round((law.voting.against / total) * 100);

  return (
    <article
      className="rounded-2xl p-6 flex flex-col gap-4 border transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl group"
      style={{
        backgroundColor: "var(--bg-card)",
        borderColor: "var(--border)",
      }}
    >
      {/* Status badge */}
      <div className="flex items-center justify-between">
        <span
          className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold"
          style={{ backgroundColor: status.bg, color: status.text }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{ backgroundColor: status.dot }}
          />
          {law.status}
        </span>
        <span
          className="text-xs"
          style={{ color: "var(--text-secondary)" }}
        >
          Filed {new Date(law.filingDate).toLocaleDateString("en-US")}
        </span>
      </div>

      {/* Title */}
      <h2
        className="text-base font-semibold leading-snug group-hover:text-blue-400 transition-colors"
        style={{ color: "var(--text-primary)" }}
      >
        {law.title}
      </h2>

      {/* Description */}
      <p
        className="text-sm leading-relaxed line-clamp-2"
        style={{ color: "var(--text-secondary)" }}
      >
        {law.description}
      </p>

      {/* Author & Party */}
      <div className="flex items-center gap-4 text-xs" style={{ color: "var(--text-secondary)" }}>
        <span className="flex items-center gap-1.5">
          <User size={13} />
          {law.author}
        </span>
        <span
          className="flex items-center gap-1.5 font-medium"
          style={{ color: partyColor }}
        >
          <Building2 size={13} />
          {law.party}
        </span>
      </div>

      {/* Mini voting bar */}
      <div className="space-y-1">
        <div className="flex rounded-full overflow-hidden h-2 bg-slate-800">
          <div
            className="bg-green-500 transition-all"
            style={{ width: `${favorPct}%` }}
          />
          <div
            className="bg-red-500 transition-all"
            style={{ width: `${againstPct}%` }}
          />
        </div>
        <div className="flex justify-between text-xs" style={{ color: "var(--text-secondary)" }}>
          <span className="text-green-400">{law.voting.favor} in favor</span>
          <span className="text-red-400">{law.voting.against} against</span>
        </div>
      </div>

      {/* CTA */}
      <Link
        href={`/${law.id}`}
        className="mt-auto inline-flex items-center justify-center gap-2 w-full py-2.5 rounded-xl text-sm font-semibold transition-colors"
        style={{
          backgroundColor: "rgba(59,130,246,0.12)",
          color: "var(--accent)",
        }}
      >
        View details
        <ArrowRight size={15} />
      </Link>
    </article>
  );
}
