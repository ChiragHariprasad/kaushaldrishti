"use client";

import { useEffect, useState } from "react";

interface HealthData {
  status: string;
  version: string;
  environment: string;
  uptime_seconds: number;
  timestamp: string;
}

interface MetadataData {
  app_name: string;
  version: string;
  pilot_states: string[];
  pilot_sectors: string[];
  languages: string[];
  data_mode_counts: Record<string, number>;
}

export default function Home() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [metadata, setMetadata] = useState<MetadataData | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    async function checkApi() {
      try {
        const [healthRes, metaRes] = await Promise.all([
          fetch(`${apiUrl}/api/v1/health`),
          fetch(`${apiUrl}/api/v1/metadata`),
        ]);
        if (healthRes.ok && metaRes.ok) {
          setHealth(await healthRes.json());
          setMetadata(await metaRes.json());
          setApiError(null);
        } else {
          setApiError("Backend responded with non-200 code");
        }
      } catch (err: unknown) {
        setApiError(err instanceof Error ? err.message : "Backend connection error");
      } finally {
        setLoading(false);
      }
    }
    checkApi();
  }, [apiUrl]);

  return (
    <div className="flex flex-col min-h-screen">
      {/* Top Banner (Government of India / MSDE style) */}
      <header className="bg-slate-900 text-white border-b-4 border-amber-600">
        <div className="max-w-7xl mx-auto px-4 py-3 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 bg-amber-500 rounded-md flex items-center justify-center font-bold text-slate-950 text-xl shadow">
              क
            </div>
            <div>
              <div className="text-xs uppercase tracking-wider text-amber-400 font-semibold">
                Ministry of Skill Development &amp; Entrepreneurship (MSDE)
              </div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                KaushalDrishti
                <span className="text-xs font-normal text-slate-300 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                  SIH26246
                </span>
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 bg-slate-800 px-3 py-1 rounded text-xs border border-slate-700">
              <span className="text-slate-400">API Status:</span>
              {loading ? (
                <span className="text-amber-400">Connecting...</span>
              ) : health?.status === "healthy" ? (
                <span className="inline-flex items-center gap-1 text-emerald-400 font-medium">
                  <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  Online (v{health.version})
                </span>
              ) : (
                <span
                  className="inline-flex items-center gap-1 text-rose-400 font-medium cursor-help"
                  title={apiError || "Disconnected"}
                >
                  <span className="h-2 w-2 rounded-full bg-rose-500"></span>
                  Standby
                </span>
              )}
            </div>
            {metadata && (
              <span className="hidden sm:inline-block text-xs text-slate-400">
                {metadata.languages.join(" • ")}
              </span>
            )}
            <a
              href={`${apiUrl}/api/v1/docs`}
              target="_blank"
              rel="noreferrer"
              className="text-xs font-medium bg-amber-600 hover:bg-amber-500 text-white px-3 py-1 rounded transition"
            >
              API Docs
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8 sm:px-6 lg:px-8 space-y-8">
        {/* Hero Section */}
        <section className="bg-white rounded-xl p-6 sm:p-8 shadow-sm border border-slate-200">
          <div className="max-w-3xl space-y-3">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
              <span>M0: Scaffold Phase Complete</span>
              <span>•</span>
              <span>All 9 Architecture Layers Initialised</span>
            </div>
            <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              Labour Market Intelligence System (LMIS)
            </h2>
            <p className="text-slate-600 text-base leading-relaxed">
              District-level dynamic demand forecasting, supply pipeline modelling, and early warning intelligence for targeted skill planning across India.
            </p>
          </div>

          {/* Quick Metrics / Scope */}
          <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Pilot States
              </div>
              <div className="mt-1 text-2xl font-bold text-slate-900">3 States</div>
              <div className="mt-1 text-xs text-slate-600">
                Karnataka (31), Tamil Nadu (38), Uttar Pradesh (75)
              </div>
            </div>

            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Priority Sectors
              </div>
              <div className="mt-1 text-2xl font-bold text-slate-900">5 Sectors</div>
              <div className="mt-1 text-xs text-slate-600">
                Auto, Healthcare, Electronics, Construction, Logistics
              </div>
            </div>

            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Coverage Scale
              </div>
              <div className="mt-1 text-2xl font-bold text-slate-900">144 Districts</div>
              <div className="mt-1 text-xs text-slate-600">
                40 Trades • 48-Month Historical Horizon
              </div>
            </div>

            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Multilingual Support
              </div>
              <div className="mt-1 text-2xl font-bold text-slate-900">4 Languages</div>
              <div className="mt-1 text-xs text-slate-600">
                English (en), हिन्दी (hi), ಕನ್ನಡ (kn), தமிழ் (ta)
              </div>
            </div>
          </div>
        </section>

        {/* Working Rules & Data Mode Badges */}
        <section className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-900">
              Data Integrity &amp; Labelling Standard
            </h3>
            <span className="text-xs font-medium text-slate-500">
              Mandatory Rule #1: Honesty over polish
            </span>
          </div>
          <p className="text-sm text-slate-600">
            Every record and metric in KaushalDrishti carries an immutable <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-800 font-mono text-xs">data_mode</code> badge to prevent misrepresenting synthetic or aggregate data as live feeds:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
            <div className="p-3 rounded-lg border border-emerald-200 bg-emerald-50">
              <div className="flex items-center gap-1.5">
                <span className="px-2 py-0.5 text-xs font-bold rounded bg-emerald-600 text-white">
                  live
                </span>
                <span className="text-xs font-semibold text-emerald-900">Live API</span>
              </div>
              <p className="text-xs text-emerald-800 mt-1.5">
                Real-time portal feeds with certified update frequency.
              </p>
            </div>

            <div className="p-3 rounded-lg border border-blue-200 bg-blue-50">
              <div className="flex items-center gap-1.5">
                <span className="px-2 py-0.5 text-xs font-bold rounded bg-blue-600 text-white">
                  public_aggregate
                </span>
                <span className="text-xs font-semibold text-blue-900">Official Reports</span>
              </div>
              <p className="text-xs text-blue-800 mt-1.5">
                PLFS, e-Shram, and official statistics publications.
              </p>
            </div>

            <div className="p-3 rounded-lg border border-purple-200 bg-purple-50">
              <div className="flex items-center gap-1.5">
                <span className="px-2 py-0.5 text-xs font-bold rounded bg-purple-600 text-white">
                  partner
                </span>
                <span className="text-xs font-semibold text-purple-900">Partner Portals</span>
              </div>
              <p className="text-xs text-purple-800 mt-1.5">
                Private job portals with de-duplication and bias correction.
              </p>
            </div>

            <div className="p-3 rounded-lg border border-amber-200 bg-amber-50">
              <div className="flex items-center gap-1.5">
                <span className="px-2 py-0.5 text-xs font-bold rounded bg-amber-600 text-white">
                  synthetic
                </span>
                <span className="text-xs font-semibold text-amber-900">Pipeline Validation</span>
              </div>
              <p className="text-xs text-amber-800 mt-1.5">
                Calibrated generator for gap-filling &amp; planted-signal validation.
              </p>
            </div>
          </div>
        </section>

        {/* Golden Path Pipeline Flow */}
        <section className="bg-white rounded-xl p-6 shadow-sm border border-slate-200 space-y-4">
          <h3 className="text-lg font-bold text-slate-900">
            Golden Path Navigation Workflow
          </h3>
          <p className="text-sm text-slate-600">
            End-to-end evaluation flow (≤ 3 clicks per level):
          </p>
          <div className="grid grid-cols-1 md:grid-cols-6 gap-2 text-center text-xs font-semibold pt-2">
            <div className="p-3 rounded bg-slate-100 border border-slate-200 text-slate-800">
              1. National Overview
            </div>
            <div className="p-3 rounded bg-slate-100 border border-slate-200 text-slate-800">
              2. Karnataka State
            </div>
            <div className="p-3 rounded bg-slate-100 border border-slate-200 text-slate-800">
              3. District Selection
            </div>
            <div className="p-3 rounded bg-slate-100 border border-slate-200 text-slate-800">
              4. Automotive / EV Tech
            </div>
            <div className="p-3 rounded bg-slate-100 border border-slate-200 text-slate-800">
              5. &ldquo;Why&rdquo; Panel Attribution
            </div>
            <div className="p-3 rounded bg-amber-100 border border-amber-300 text-amber-900">
              6. Scenario Lab (+15% seats)
            </div>
          </div>
        </section>

        {/* Milestone Tracker */}
        <section className="bg-slate-900 text-white rounded-xl p-6 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white">Milestone Status</h3>
            <span className="text-xs text-slate-400">Smart India Hackathon 2026</span>
          </div>
          <div className="text-xs grid grid-cols-2 sm:grid-cols-5 gap-2 text-slate-300">
            <div className="p-2 rounded bg-emerald-950 border border-emerald-700 text-emerald-300">
              ✓ M0: Scaffold
            </div>
            <div className="p-2 rounded bg-slate-800 border border-slate-700">
              ⏳ M1: Data &amp; Taxonomy
            </div>
            <div className="p-2 rounded bg-slate-800 border border-slate-700">
              ⏳ M2: Demand Intelligence
            </div>
            <div className="p-2 rounded bg-slate-800 border border-slate-700">
              ⏳ M3: Supply Intelligence
            </div>
            <div className="p-2 rounded bg-slate-800 border border-slate-700">
              ⏳ M4: Forecasting
            </div>
            <div className="p-2 rounded bg-slate-800 border border-slate-700">
              ⏳ M5: Gap &amp; Alerts
            </div>
            <div className="p-2 rounded bg-slate-800 border border-slate-700">
              ⏳ M6: API &amp; Exports
            </div>
            <div className="p-2 rounded bg-slate-800 border border-slate-700">
              ⏳ M7: Dashboard
            </div>
            <div className="p-2 rounded bg-slate-800 border border-slate-700">
              ⏳ M8: Scenario Lab
            </div>
            <div className="p-2 rounded bg-slate-800 border border-slate-700">
              ⏳ M9: Hardening &amp; Demo
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-slate-100 border-t border-slate-200 mt-auto py-4 text-center text-xs text-slate-600">
        KaushalDrishti • Ministry of Skill Development &amp; Entrepreneurship (MSDE) • SIH 2026
      </footer>
    </div>
  );
}
