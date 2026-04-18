import { User, ShieldCheck, Landmark } from "lucide-react";

export function parseActors(actorsInput: string | string[]) {
  if (Array.isArray(actorsInput)) {
    return actorsInput.map(name => ({ role: "Firmante / Autor", names: name }));
  }

  const lines = actorsInput.split("\n").filter((l) => l.trim().length > 0);
  const actors: { role: string; names: string }[] = [];

  lines.forEach((line) => {
    try {
      const obj = JSON.parse(line);
      // Handle different formats in the JSON objects
      Object.keys(obj).forEach((key) => {
        if (key.startsWith("rol_")) {
          const suffix = key.split("_")[1];
          const nameKey = `names_${suffix}`;
          if (obj[nameKey]) {
            actors.push({ role: obj[key], names: obj[nameKey] });
          }
        } else if (!key.startsWith("names_")) {
          // General key-value pairs like "Autor": "Name"
          actors.push({ role: key, names: obj[key] });
        }
      });
    } catch (e) {
      // If not JSON, just treat the whole line as a name if it's simple
      if (line.length < 100 && !line.includes("{")) {
         actors.push({ role: "Participante", names: line.trim() });
      }
    }
  });

  return actors;
}

export default function AnalysisActors({ actorsStr, authorsList }: { actorsStr?: string, authorsList?: string[] }) {
  const actors = parseActors(authorsList || actorsStr || "");

  if (actors.length === 0) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {actors.map((actor, idx) => (
        <div
          key={idx}
          className="flex items-start gap-4 p-4 rounded-2xl border bg-white/5 border-white/10"
        >
          <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400">
            {actor.role.toLowerCase().includes("autor") ? (
              <User size={18} />
            ) : actor.role.toLowerCase().includes("ministro") || actor.role.toLowerCase().includes("secretario") ? (
              <Landmark size={18} />
            ) : (
              <ShieldCheck size={18} />
            )}
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-wider font-bold text-slate-500 mb-1">
              {actor.role}
            </p>
            <p className="text-sm text-slate-200 font-medium">{actor.names}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
