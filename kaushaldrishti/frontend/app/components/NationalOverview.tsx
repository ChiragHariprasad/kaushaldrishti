"use client";

import React from "react";
import { Language, translations } from "../i18n";

interface NationalOverviewProps {
  lang: Language;
  onSelectCell: (stateCode: string, districtId: number, tradeId: number) => void;
  onNavigateTab: (tab: string) => void;
}

export const NationalOverview: React.FC<NationalOverviewProps> = ({
  lang,
  onSelectCell,
  onNavigateTab,
}) => {
  const t = translations[lang];

  // National metrics
  const kpiCards = [
    { label: t.kpiMonitoredDistricts, value: "144", sub: "3 Pilot States (KA, TN, UP)", color: "border-blue-500/40 bg-blue-950/20 text-blue-400" },
    { label: t.kpiAcuteShortage, value: "1,418", sub: "p_S >= 0.80, persists >= 2 refreshes", color: "border-rose-500/40 bg-rose-950/20 text-rose-400" },
    { label: t.kpiEmergingShortage, value: "2,740", sub: "0.60 <= p_S < 0.80, growth diff", color: "border-amber-500/40 bg-amber-950/20 text-amber-400" },
    { label: t.kpiApproachingSaturation, value: "892", sub: "0.60 <= p_O < 0.80, supply > demand", color: "border-teal-500/40 bg-teal-950/20 text-teal-400" },
    { label: t.kpiSaturated, value: "410", sub: "p_O >= 0.80, E[g] <= -0.20", color: "border-purple-500/40 bg-purple-950/20 text-purple-400" },
    { label: t.kpiRapidGrowth, value: "624", sub: ">90th percentile growth & corroboration", color: "border-emerald-500/40 bg-emerald-950/20 text-emerald-400" },
  ];

  // State comparison summaries
  const stateCards = [
    {
      code: "KA",
      name: "Karnataka",
      districts: 31,
      trades: 40,
      shortages: 412,
      balanced: 620,
      surplus: 208,
      avgLdi: 54.6,
      topTrade: "EV Service Technician",
      topTradeId: 1,
      repDistrictId: 1, // Bengaluru Urban
    },
    {
      code: "TN",
      name: "Tamil Nadu",
      districts: 38,
      trades: 40,
      shortages: 495,
      balanced: 780,
      surplus: 245,
      avgLdi: 53.2,
      topTrade: "CNC Machining Technician",
      topTradeId: 6,
      repDistrictId: 32, // Chennai
    },
    {
      code: "UP",
      name: "Uttar Pradesh",
      districts: 75,
      trades: 40,
      shortages: 890,
      balanced: 1540,
      surplus: 570,
      avgLdi: 49.8,
      topTrade: "Solar Panel Installation Technician",
      topTradeId: 21,
      repDistrictId: 70, // Gautam Buddha Nagar
    },
  ];

  // Top 5 Shortages
  const topShortages = [
    { rank: 1, state: "KA", district: "Bengaluru Urban", trade: "EV Service Technician", gap: "+384", p: 0.98, severity: 98.2, distId: 1, tradeId: 1 },
    { rank: 2, state: "TN", district: "Chennai", trade: "CNC Machining Technician", gap: "+312", p: 0.95, severity: 95.0, distId: 32, tradeId: 6 },
    { rank: 3, state: "UP", district: "Gautam Buddha Nagar", trade: "Solar Panel Installation Technician", gap: "+275", p: 0.92, severity: 92.4, distId: 70, tradeId: 21 },
    { rank: 4, state: "KA", district: "Mysuru", trade: "EV Service Technician", gap: "+210", p: 0.89, severity: 89.1, distId: 2, tradeId: 1 },
    { rank: 5, state: "TN", district: "Coimbatore", trade: "Two Wheeler Service Technician", gap: "+195", p: 0.87, severity: 87.5, distId: 34, tradeId: 5 },
  ];

  // Top 5 Saturations
  const topSaturations = [
    { rank: 1, state: "KA", district: "Kalaburagi", trade: "Wireman", gap: "-185", p: 0.94, severity: 93.6, distId: 8, tradeId: 23 },
    { rank: 2, state: "UP", district: "Bareilly", trade: "Scaffolder", gap: "-160", p: 0.91, severity: 90.8, distId: 82, tradeId: 31 },
    { rank: 3, state: "TN", district: "Madurai", trade: "Mason (General)", gap: "-145", p: 0.88, severity: 87.2, distId: 40, tradeId: 29 },
    { rank: 4, state: "UP", district: "Aligarh", trade: "Electronics Mechanic", gap: "-132", p: 0.85, severity: 84.5, distId: 88, tradeId: 17 },
    { rank: 5, state: "KA", district: "Belagavi", trade: "Two Wheeler Service Technician", gap: "-118", p: 0.82, severity: 81.9, distId: 4, tradeId: 5 },
  ];

  return (
    <div className="space-y-6">
      {/* Golden Path Alert Callout */}
      <div className="bg-gradient-to-r from-blue-900/40 via-indigo-900/30 to-purple-900/40 border border-blue-500/30 rounded-xl p-4 shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-lg">
            ★
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider font-semibold text-blue-400">
              Evaluator Golden Path Demonstration
            </div>
            <div className="text-sm font-medium text-slate-100">
              National Overview → Karnataka → Bengaluru Urban → Automotive → EV Service Technician
            </div>
          </div>
        </div>
        <button
          onClick={() => {
            onSelectCell("KA", 1, 1);
            onNavigateTab("forecast");
          }}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow transition-all flex items-center gap-1.5"
        >
          <span>Launch Golden Path Trade</span>
          <span>→</span>
        </button>
      </div>

      {/* National KPI Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {kpiCards.map((kpi, idx) => (
          <div key={idx} className={`p-4 rounded-xl border ${kpi.color} shadow-sm`}>
            <div className="text-2xl font-extrabold tracking-tight">{kpi.value}</div>
            <div className="text-xs font-semibold mt-1 text-slate-200">{kpi.label}</div>
            <div className="text-[10px] text-slate-400 mt-1 leading-snug">{kpi.sub}</div>
          </div>
        ))}
      </div>

      {/* Pilot States Comparison */}
      <div>
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3">
          Pilot State Intelligence Scorecards
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {stateCards.map((st) => (
            <div
              key={st.code}
              className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all shadow-sm"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <span className="text-xs font-mono bg-slate-800 text-blue-400 px-2 py-0.5 rounded font-semibold mr-2">
                    {st.code}
                  </span>
                  <span className="font-bold text-base text-slate-100">{st.name}</span>
                </div>
                <div className="text-xs text-slate-400 font-mono">
                  LDI: <span className="text-slate-200 font-bold">{st.avgLdi}</span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 text-center py-2 bg-slate-950/60 rounded-lg border border-slate-800/80 mb-3 text-xs">
                <div>
                  <div className="text-rose-400 font-bold">{st.shortages}</div>
                  <div className="text-[10px] text-slate-500">Shortages</div>
                </div>
                <div>
                  <div className="text-slate-300 font-bold">{st.balanced}</div>
                  <div className="text-[10px] text-slate-500">Balanced</div>
                </div>
                <div>
                  <div className="text-purple-400 font-bold">{st.surplus}</div>
                  <div className="text-[10px] text-slate-500">Saturation</div>
                </div>
              </div>

              <div className="text-xs text-slate-400 mb-4">
                Highest Shortage Priority:{" "}
                <span className="text-slate-200 font-medium">{st.topTrade}</span>
              </div>

              <button
                onClick={() => {
                  onSelectCell(st.code, st.repDistrictId, st.topTradeId);
                  onNavigateTab("explorer");
                }}
                className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg transition-colors border border-slate-700"
              >
                Explore {st.districts} Districts →
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Top 5 Shortages and Top 5 Saturations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top 5 Shortages */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-bold text-sm text-rose-400 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
              Top Emerging & Acute Shortages
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">Ranked by Severity</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-2 px-2">#</th>
                  <th className="py-2 px-2">District & State</th>
                  <th className="py-2 px-2">Priority Trade</th>
                  <th className="py-2 px-2 text-right">Gap</th>
                  <th className="py-2 px-2 text-right">P(Shortage)</th>
                  <th className="py-2 px-2 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {topShortages.map((item) => (
                  <tr key={item.rank} className="hover:bg-slate-800/40">
                    <td className="py-2.5 px-2 font-mono text-slate-500">{item.rank}</td>
                    <td className="py-2.5 px-2 font-medium text-slate-200">
                      {item.district} <span className="text-slate-500 font-normal">({item.state})</span>
                    </td>
                    <td className="py-2.5 px-2 text-slate-300">{item.trade}</td>
                    <td className="py-2.5 px-2 text-right font-mono font-bold text-rose-400">{item.gap}</td>
                    <td className="py-2.5 px-2 text-right font-mono text-slate-300">{(item.p * 100).toFixed(0)}%</td>
                    <td className="py-2.5 px-2 text-center">
                      <button
                        onClick={() => {
                          onSelectCell(item.state, item.distId, item.tradeId);
                          onNavigateTab("forecast");
                        }}
                        className="px-2 py-1 bg-blue-600/30 hover:bg-blue-600/50 text-blue-300 rounded text-[11px] font-medium"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Top 5 Saturations */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-bold text-sm text-purple-400 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-500" />
              Top Saturation & Surplus Risks
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">Ranked by Severity</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-2 px-2">#</th>
                  <th className="py-2 px-2">District & State</th>
                  <th className="py-2 px-2">Priority Trade</th>
                  <th className="py-2 px-2 text-right">Oversupply</th>
                  <th className="py-2 px-2 text-right">P(Surplus)</th>
                  <th className="py-2 px-2 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {topSaturations.map((item) => (
                  <tr key={item.rank} className="hover:bg-slate-800/40">
                    <td className="py-2.5 px-2 font-mono text-slate-500">{item.rank}</td>
                    <td className="py-2.5 px-2 font-medium text-slate-200">
                      {item.district} <span className="text-slate-500 font-normal">({item.state})</span>
                    </td>
                    <td className="py-2.5 px-2 text-slate-300">{item.trade}</td>
                    <td className="py-2.5 px-2 text-right font-mono font-bold text-purple-400">{item.gap}</td>
                    <td className="py-2.5 px-2 text-right font-mono text-slate-300">{(item.p * 100).toFixed(0)}%</td>
                    <td className="py-2.5 px-2 text-center">
                      <button
                        onClick={() => {
                          onSelectCell(item.state, item.distId, item.tradeId);
                          onNavigateTab("forecast");
                        }}
                        className="px-2 py-1 bg-purple-600/30 hover:bg-purple-600/50 text-purple-300 rounded text-[11px] font-medium"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
