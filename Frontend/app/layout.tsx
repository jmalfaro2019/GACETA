import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Veeduría Congreso Colombia",
  description:
    "Plataforma ciudadana para vigilar las leyes y decisiones del Congreso de Colombia.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen" style={{ backgroundColor: "var(--bg-primary)" }}>
        {/* ── Nav ── */}
        <header
          className="sticky top-0 z-50 border-b"
          style={{
            backgroundColor: "var(--bg-secondary)",
            borderColor: "var(--border)",
          }}
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* Colombian flag accent bar */}
              <div className="flex flex-col gap-0.5 w-1 h-8">
                <div className="flex-1 bg-yellow-400 rounded-full" />
                <div className="flex-1 bg-blue-500 rounded-full" />
                <div className="flex-1 bg-red-500 rounded-full" />
              </div>
              <span
                className="text-xl font-bold tracking-tight"
                style={{ color: "var(--text-primary)" }}
              >
                Veeduría{" "}
                <span style={{ color: "var(--accent)" }}>Congreso</span>
              </span>
            </div>
            <nav className="hidden md:flex items-center gap-6 text-sm font-medium" style={{ color: "var(--text-secondary)" }}>
              <a href="/" className="hover:text-white transition-colors">
                Leyes
              </a>
              <a href="#" className="hover:text-white transition-colors">
                Senadores
              </a>
              <a href="#" className="hover:text-white transition-colors">
                Estadísticas
              </a>
            </nav>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          {children}
        </main>

        <footer
          className="border-t mt-20 py-8 text-center text-sm"
          style={{
            borderColor: "var(--border)",
            color: "var(--text-secondary)",
          }}
        >
          Veeduría Congreso Colombia — Datos públicos con fines ciudadanos.
        </footer>
      </body>
    </html>
  );
}
