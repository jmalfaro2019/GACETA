import { FileText, Sparkles } from "lucide-react";

export default function Loading() {
  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-pulse">
      {/* Back button placeholder */}
      <div className="h-4 w-24 bg-white/5 rounded-full" />

      {/* Header Loading State */}
      <header className="rounded-3xl p-8 border border-white/5 bg-white/[0.02] h-64 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-5">
          <FileText size={120} />
        </div>
        <div className="space-y-4">
          <div className="h-6 w-40 bg-blue-500/10 rounded-full" />
          <div className="h-10 w-3/4 bg-white/10 rounded-xl" />
          <div className="h-4 w-full bg-white/5 rounded-full" />
          <div className="h-4 w-2/3 bg-white/5 rounded-full" />
        </div>
      </header>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <div className="rounded-3xl p-8 border border-white/5 bg-white/[0.02] h-96">
            <div className="h-6 w-32 bg-white/10 rounded-full mb-6" />
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-4 w-full bg-white/5 rounded-full" />
              ))}
            </div>
          </div>
        </div>
        <div className="space-y-8">
          <div className="rounded-3xl p-6 border border-white/5 bg-white/[0.02] h-48">
             <div className="h-4 w-24 bg-white/10 rounded-full mb-4" />
             <div className="flex flex-wrap gap-2">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className="h-8 w-20 bg-white/5 rounded-xl" />
                ))}
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
