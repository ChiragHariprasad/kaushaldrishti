"use client";

import React, { useState } from "react";
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
  const [activeHexState, setActiveHexState] = useState<"KA" | "TN" | "UP">("KA");

  // National metrics using theme palette
  const kpiCards = [
    { label: t.kpiMonitoredDistricts, value: "144", sub: "3 Pilot States (KA, TN, UP)", border: "border-[#255DCE]/60", bg: "bg-[#021861]", text: "text-white" },
    { label: t.kpiAcuteShortage, value: "1,418", sub: "p_S >= 0.80, persists >= 2 refreshes", border: "border-[#DE1110]/80", bg: "bg-[#021861]", text: "text-[#DE1110]" },
    { label: t.kpiEmergingShortage, value: "2,740", sub: "0.60 <= p_S < 0.80, growth diff", border: "border-amber-500/60", bg: "bg-[#021861]", text: "text-amber-300" },
    { label: t.kpiApproachingSaturation, value: "892", sub: "0.60 <= p_O < 0.80, supply > demand", border: "border-teal-500/60", bg: "bg-[#021861]", text: "text-teal-300" },
    { label: t.kpiSaturated, value: "410", sub: "p_O >= 0.80, E[g] <= -0.20", border: "border-purple-500/60", bg: "bg-[#021861]", text: "text-purple-300" },
    { label: t.kpiRapidGrowth, value: "624", sub: ">90th percentile growth & corroboration", border: "border-[#255DCE]/60", bg: "bg-[#021861]", text: "text-blue-300" },
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

  // Hex tile-grid representation for districts (Section 11 offline map requirement)
  const hexDistrictsKA = [
    { id: 1, name: "Bengaluru Urban", code: "BLR", status: "acute", shortages: 18 },
    { id: 2, name: "Mysuru", code: "MYS", status: "emerging", shortages: 12 },
    { id: 3, name: "Dharwad", code: "DHD", status: "balanced", shortages: 9 },
    { id: 4, name: "Belagavi", code: "BEL", status: "balanced", shortages: 11 },
    { id: 5, name: "Dakshina Kannada", code: "DKN", status: "emerging", shortages: 10 },
    { id: 6, name: "Udupi", code: "UDP", status: "balanced", shortages: 6 },
    { id: 7, name: "Shivamogga", code: "SHV", status: "balanced", shortages: 7 },
    { id: 8, name: "Kalaburagi", code: "KLB", status: "saturation", shortages: 8 },
    { id: 9, name: "Ballari", code: "BAL", status: "emerging", shortages: 14 },
    { id: 10, name: "Tumakuru", code: "TUM", status: "balanced", shortages: 7 },
    { id: 11, name: "Kolar", code: "KLR", status: "emerging", shortages: 11 },
    { id: 12, name: "Mandya", code: "MDY", status: "balanced", shortages: 5 },
  ];

  const hexDistrictsTN = [
    { id: 32, name: "Chennai", code: "CHN", status: "acute", shortages: 20 },
    { id: 33, name: "Kanchipuram", code: "KNC", status: "emerging", shortages: 13 },
    { id: 34, name: "Coimbatore", code: "CBE", status: "acute", shortages: 16 },
    { id: 35, name: "Salem", code: "SLM", status: "emerging", shortages: 12 },
    { id: 36, name: "Tiruppur", code: "TPR", status: "acute", shortages: 14 },
    { id: 37, name: "Erode", code: "ERD", status: "balanced", shortages: 9 },
    { id: 40, name: "Madurai", code: "MDU", status: "saturation", shortages: 10 },
    { id: 41, name: "Tiruchirappalli", code: "TRY", status: "balanced", shortages: 8 },
  ];

  const hexDistrictsUP = [
    { id: 70, name: "Gautam Buddha Nagar", code: "GBN", status: "acute", shortages: 22 },
    { id: 71, name: "Lucknow", code: "LKO", status: "saturation", shortages: 19 },
    { id: 72, name: "Ghaziabad", code: "GZB", status: "acute", shortages: 18 },
    { id: 75, name: "Kanpur Nagar", code: "KNP", status: "emerging", shortages: 15 },
    { id: 80, name: "Varanasi", code: "VNS", status: "emerging", shortages: 13 },
    { id: 81, name: "Prayagraj", code: "PRY", status: "balanced", shortages: 10 },
    { id: 82, name: "Bareilly", code: "BLY", status: "saturation", shortages: 8 },
    { id: 85, name: "Agra", code: "AGR", status: "emerging", shortages: 14 },
  ];

  const activeHexList =
    activeHexState === "KA" ? hexDistrictsKA : activeHexState === "TN" ? hexDistrictsTN : hexDistrictsUP;

  const getStatusColor = (status: string) => {
    switch (status) {
      case "acute":
        return "bg-[#DE1110] text-white border-white/40 shadow-sm shadow-[#DE1110]/50";
      case "emerging":
        return "bg-amber-600 text-white border-amber-400/40";
      case "saturation":
        return "bg-purple-700 text-white border-purple-400/40";
      default:
        return "bg-[#05216e] text-slate-200 border-[#133896]";
    }
  };

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
      <div className="bg-[#021861] border border-[#255DCE] rounded-xl p-4 shadow-lg flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#255DCE] text-white flex items-center justify-center font-black text-xl shadow">
            ★
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider font-extrabold text-blue-200 flex items-center gap-2">
              <span>Evaluator Golden Path Demonstration</span>
              <span className="text-[10px] bg-[#DE1110] text-white px-1.5 py-0.2 rounded font-bold">
                Team PROMETHEUSS
              </span>
            </div>
            <div className="text-sm font-semibold text-white">
              National Overview &rarr; Karnataka &rarr; Bengaluru Urban &rarr; Automotive &rarr; EV Service Technician
            </div>
          </div>
        </div>
        <button
          onClick={() => {
            onSelectCell("KA", 1, 1);
            onNavigateTab("forecast");
          }}
          className="px-5 py-2.5 bg-[#255DCE] hover:bg-[#1e4eb2] text-white text-xs font-bold rounded-lg shadow-md transition-all flex items-center gap-2 border border-blue-400/40"
        >
          <span>Launch Golden Path Trade</span>
          <span>&rarr;</span>
        </button>
      </div>

      {/* National KPI Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {kpiCards.map((kpi, idx) => (
          <div key={idx} className={`p-4 rounded-xl border ${kpi.border} ${kpi.bg} shadow-md`}>
            <div className={`text-2xl font-black tracking-tight font-mono ${kpi.text}`}>{kpi.value}</div>
            <div className="text-xs font-bold mt-1 text-slate-100">{kpi.label}</div>
            <div className="text-[10px] text-slate-300 mt-1 leading-snug">{kpi.sub}</div>
          </div>
        ))}
      </div>

      {/* Hex Tile-Grid Map Fallback (Section 11 Requirement) */}
      <div className="bg-[#021861] border border-[#133896] rounded-xl p-5 shadow-lg space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#133896] pb-3">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <span>🗺️</span> District Spatial Hex-Grid Map (Offline Fallback)
            </h3>
            <p className="text-xs text-slate-300">
              Deterministic hex tile topology for pilot districts. Zero external tile dependencies (Section 11 invariant).
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-300 font-medium">State View:</span>
            <div className="flex items-center bg-[#010e3b] p-1 rounded-lg border border-[#133896]">
              {(["KA", "TN", "UP"] as const).map((st) => (
                <button
                  key={st}
                  onClick={() => setActiveHexState(st)}
                  className={`px-3 py-1 rounded text-xs font-bold transition ${
                    activeHexState === st
                      ? "bg-[#255DCE] text-white shadow"
                      : "text-slate-300 hover:text-white"
                  }`}
                >
                  {st === "KA" ? "Karnataka (31)" : st === "TN" ? "Tamil Nadu (38)" : "Uttar Pradesh (75)"}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-4 text-xs text-slate-300 bg-[#010e3b] p-2.5 rounded-lg border border-[#133896]">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-[#DE1110]" />
            <span>Acute Shortage (p_S &ge; 80%)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-amber-500" />
            <span>Emerging Shortage</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-[#05216e] border border-[#133896]" />
            <span>Balanced</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-purple-600" />
            <span>Saturation / Surplus</span>
          </div>
        </div>

        {/* Hex District Tiles */}
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2.5 pt-2">
          {activeHexList.map((dist) => (
            <button
              key={dist.id}
              onClick={() => {
                onSelectCell(activeHexState, dist.id, 1);
                onNavigateTab("explorer");
              }}
              className={`p-3 rounded-xl border transition-all text-left flex flex-col justify-between hover:scale-105 ${getStatusColor(
                dist.status
              )}`}
            >
              <div className="flex items-center justify-between w-full">
                <span className="text-[10px] font-mono font-black">{dist.code}</span>
                <span className="text-[10px] font-bold font-mono">
                  {dist.shortages} shortages
                </span>
              </div>
              <div className="font-bold text-xs mt-2 truncate w-full">{dist.name}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Pilot States Comparison */}
      <div>
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
          Pilot State Intelligence Scorecards
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {stateCards.map((st) => (
            <div
              key={st.code}
              className="bg-[#021861] border border-[#133896] rounded-xl p-5 hover:border-[#255DCE] transition-all shadow-md"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <span className="text-xs font-mono bg-[#255DCE] text-white px-2 py-0.5 rounded font-bold mr-2">
                    {st.code}
                  </span>
                  <span className="font-bold text-base text-white">{st.name}</span>
                </div>
                <div className="text-xs text-slate-300 font-mono">
                  LDI: <span className="text-white font-bold">{st.avgLdi}</span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 text-center py-2 bg-[#010e3b] rounded-lg border border-[#133896] mb-3 text-xs">
                <div>
                  <div className="text-[#DE1110] font-bold font-mono text-sm">{st.shortages}</div>
                  <div className="text-[10px] text-slate-300">Shortages</div>
                </div>
                <div>
                  <div className="text-blue-300 font-bold font-mono text-sm">{st.balanced}</div>
                  <div className="text-[10px] text-slate-300">Balanced</div>
                </div>
                <div>
                  <div className="text-purple-300 font-bold font-mono text-sm">{st.surplus}</div>
                  <div className="text-[10px] text-slate-300">Saturation</div>
                </div>
              </div>

              <div className="text-xs text-slate-300 mb-4">
                Highest Shortage Priority:{" "}
                <span className="text-white font-semibold">{st.topTrade}</span>
              </div>

              <button
                onClick={() => {
                  onSelectCell(st.code, st.repDistrictId, st.topTradeId);
                  onNavigateTab("explorer");
                }}
                className="w-full py-2 bg-[#255DCE] hover:bg-[#1e4eb2] text-white text-xs font-bold rounded-lg transition-colors border border-blue-400/40 shadow-sm"
              >
                Explore {st.districts} Districts &rarr;
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Top 5 Shortages and Top 5 Saturations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top 5 Shortages */}
        <div className="bg-[#021861] border border-[#133896] rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-bold text-sm text-white flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#DE1110] animate-pulse" />
              <span className="text-[#DE1110]">Top Critical Shortages</span>
            </h3>
            <span className="text-[11px] text-slate-300 font-mono">Ranked by Severity</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#010e3b] text-slate-300 border-b border-[#133896]">
                <tr>
                  <th className="py-2.5 px-2">#</th>
                  <th className="py-2.5 px-2">District &amp; State</th>
                  <th className="py-2.5 px-2">Priority Trade</th>
                  <th className="py-2.5 px-2 text-right">Gap</th>
                  <th className="py-2.5 px-2 text-right">P(Shortage)</th>
                  <th className="py-2.5 px-2 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#133896]/60">
                {topShortages.map((item) => (
                  <tr key={item.rank} className="hover:bg-[#05216e]/60 transition">
                    <td className="py-2.5 px-2 font-mono text-slate-400 font-bold">{item.rank}</td>
                    <td className="py-2.5 px-2 font-semibold text-white">
                      {item.district} <span className="text-slate-400 font-normal">({item.state})</span>
                    </td>
                    <td className="py-2.5 px-2 text-slate-200">{item.trade}</td>
                    <td className="py-2.5 px-2 text-right font-mono font-bold text-[#DE1110]">{item.gap}</td>
                    <td className="py-2.5 px-2 text-right font-mono text-slate-300">{(item.p * 100).toFixed(0)}%</td>
                    <td className="py-2.5 px-2 text-center">
                      <button
                        onClick={() => {
                          onSelectCell(item.state, item.distId, item.tradeId);
                          onNavigateTab("forecast");
                        }}
                        className="px-2.5 py-1 bg-[#255DCE] hover:bg-[#1e4eb2] text-white rounded text-[11px] font-bold shadow-sm"
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
        <div className="bg-[#021861] border border-[#133896] rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-bold text-sm text-purple-300 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-500" />
              <span>Top Saturation &amp; Surplus Risks</span>
            </h3>
            <span className="text-[11px] text-slate-300 font-mono">Ranked by Severity</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#010e3b] text-slate-300 border-b border-[#133896]">
                <tr>
                  <th className="py-2.5 px-2">#</th>
                  <th className="py-2.5 px-2">District &amp; State</th>
                  <th className="py-2.5 px-2">Priority Trade</th>
                  <th className="py-2.5 px-2 text-right">Oversupply</th>
                  <th className="py-2.5 px-2 text-right">P(Surplus)</th>
                  <th className="py-2.5 px-2 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#133896]/60">
                {topSaturations.map((item) => (
                  <tr key={item.rank} className="hover:bg-[#05216e]/60 transition">
                    <td className="py-2.5 px-2 font-mono text-slate-400 font-bold">{item.rank}</td>
                    <td className="py-2.5 px-2 font-semibold text-white">
                      {item.district} <span className="text-slate-400 font-normal">({item.state})</span>
                    </td>
                    <td className="py-2.5 px-2 text-slate-200">{item.trade}</td>
                    <td className="py-2.5 px-2 text-right font-mono font-bold text-purple-300">{item.gap}</td>
                    <td className="py-2.5 px-2 text-right font-mono text-slate-300">{(item.p * 100).toFixed(0)}%</td>
                    <td className="py-2.5 px-2 text-center">
                      <button
                        onClick={() => {
                          onSelectCell(item.state, item.distId, item.tradeId);
                          onNavigateTab("forecast");
                        }}
                        className="px-2.5 py-1 bg-purple-700 hover:bg-purple-600 text-white rounded text-[11px] font-bold shadow-sm"
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
