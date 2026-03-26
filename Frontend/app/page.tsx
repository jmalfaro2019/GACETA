import laws from "@/data/laws";
import LawCard from "@/components/LawCard";
import { Scale, Users, Activity } from "lucide-react";

export default function HomePage() {
  const totals = laws.reduce(
    (acc, l) => ({
      favor: acc.favor + l.voting.favor,
      against: acc.against + l.voting.against,
      abstentions: acc.abstentions + l.voting.abstentions,
    }),
    { favor: 0, against: 0, abstentions: 0 }
  );

  return (
    <>
      {/* Hero */}
      <section className="mb-12">
        <div
          className="relative rounded-3xl overflow-hidden p-8 md:p-12"
          style={{
            background:
              "linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%)",
            border: "1px solid var(--border)",
          }}
        >
          {/* Decorative grid */}
          <div
            className="absolute inset-0 opacity-5"
            style={{
              backgroundImage:
                "repeating-linear-gradient(0deg,#fff 0,#fff 1px,transparent 1px,transparent 40px),repeating-linear-gradient(90deg,#fff 0,#fff 1px,transparent 1px,transparent 40px)",
            }}
          />
          {/* Colombian flag stripe top */}
          <div className="absolute top-0 left-0 right-0 flex h-1">
            <div className="flex-1 bg-yellow-400" />
            <div className="w-1/4 bg-blue-500" />
            <div className="w-1/4 bg-red-500" />
          </div>

          <div className="relative">
            <span className="inline-block mb-4 px-3 py-1 rounded-full text-xs font-semibold bg-blue-600/20 text-blue-400 border border-blue-500/30">
              Civic Platform
            </span>
            <h1 className="text-3xl md:text-5xl font-bold leading-tight mb-4 text-white">
              Monitor the{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">
                Colombian
              </span>{" "}
              Congress
            </h1>
            <p className="text-slate-400 max-w-xl text-base md:text-lg leading-relaxed">
              Real-time tracking of bills, debates and votes from the Senate
              and House of Representatives.
            </p>
          </div>

          {/* Stats row */}
          <div className="relative mt-8 grid grid-cols-3 gap-4 max-w-md">
            {[
              { label: "Bills Tracked", value: laws.length, icon: Scale, color: "#60a5fa" },
              { label: "Votes in Favor", value: totals.favor, icon: Activity, color: "#4ade80" },
              { label: "Votes Against", value: totals.against, icon: Users, color: "#f87171" },
            ].map(({ label, value, icon: Icon, color }) => (
              <div
                key={label}
                className="rounded-2xl p-4"
                style={{ backgroundColor: "rgba(255,255,255,0.05)" }}
              >
                <Icon size={20} style={{ color }} className="mb-2" />
                <p className="text-2xl font-bold text-white">{value}</p>
                <p className="text-xs text-slate-400 mt-0.5">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Law list */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-white">
            Active Bills
          </h2>
          <span className="text-sm text-slate-400">{laws.length} results</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4 gap-5">
          {laws.map((law) => (
            <LawCard key={law.id} law={law} />
          ))}
        </div>
      </section>
    </>
  );
}
