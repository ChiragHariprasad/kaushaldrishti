"use client";

import React, { useState } from "react";
import { Language, translations } from "../i18n";

interface DistrictExplorerProps {
  lang: Language;
  selectedState: string;
  setSelectedState: (s: string) => void;
  selectedDistrictId: number;
  setSelectedDistrictId: (d: number) => void;
  onSelectTrade: (tId: number) => void;
  onOpenWhy: (tId: number) => void;
  onOpenScenario: (tId: number) => void;
}

export const DistrictExplorer: React.FC<DistrictExplorerProps> = ({
  lang,
  selectedState,
  setSelectedState,
  selectedDistrictId,
  setSelectedDistrictId,
  onSelectTrade,
  onOpenWhy,
  onOpenScenario,
}) => {
  const t = translations[lang];
  const [selectedSector, setSelectedSector] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const states = [
    { code: "KA", name: "Karnataka", districtsCount: 31 },
    { code: "TN", name: "Tamil Nadu", districtsCount: 38 },
    { code: "UP", name: "Uttar Pradesh", districtsCount: 75 },
  ];

  const districtsKA = [
    { id: 1, name: "Bengaluru Urban", lgd: "556", pop: "9,621,551", shortages: 18, surplus: 4 },
    { id: 2, name: "Mysuru", lgd: "577", pop: "3,001,127", shortages: 12, surplus: 6 },
    { id: 3, name: "Dharwad", lgd: "565", pop: "1,847,023", shortages: 9, surplus: 8 },
    { id: 4, name: "Belagavi", lgd: "555", pop: "4,779,661", shortages: 11, surplus: 7 },
    { id: 5, name: "Dakshina Kannada", lgd: "563", pop: "2,089,649", shortages: 10, surplus: 5 },
    { id: 8, name: "Kalaburagi", lgd: "571", pop: "2,566,326", shortages: 8, surplus: 12 },
    { id: 10, name: "Tumakuru", lgd: "587", pop: "2,678,980", shortages: 7, surplus: 9 },
  ];

  const districtsTN = [
    { id: 32, name: "Chennai", lgd: "603", pop: "7,088,403", shortages: 20, surplus: 5 },
    { id: 34, name: "Coimbatore", lgd: "605", pop: "3,458,045", shortages: 16, surplus: 6 },
    { id: 36, name: "Tiruppur", lgd: "634", pop: "2,479,052", shortages: 14, surplus: 7 },
    { id: 40, name: "Madurai", lgd: "611", pop: "3,038,252", shortages: 10, surplus: 9 },
  ];

  const districtsUP = [
    { id: 70, name: "Gautam Buddha Nagar", lgd: "154", pop: "1,648,195", shortages: 22, surplus: 3 },
    { id: 71, name: "Lucknow", lgd: "167", pop: "4,589,838", shortages: 19, surplus: 6 },
    { id: 75, name: "Kanpur Nagar", lgd: "164", pop: "4,581,268", shortages: 15, surplus: 8 },
    { id: 80, name: "Varanasi", lgd: "198", pop: "3,676,841", shortages: 13, surplus: 7 },
  ];

  const activeDistricts =
    selectedState === "KA" ? districtsKA : selectedState === "TN" ? districtsTN : districtsUP;

  const currentDist =
    activeDistricts.find((d) => d.id === selectedDistrictId) || activeDistricts[0];

  // Representative trades in selected district
  const tradesData = [
    {
      id: 1,
      name: "EV Service Technician",
      sector: "Automotive",
      nco: "7231.0101",
      nsqf: 4,
      ldi: 88.4,
      conf: "High",
      demand: 520,
      supply: 136,
      gap: 384,
      flag: "Acute Shortage",
      overlays: ["Rapid Growth"],
      badgeColor: "bg-rose-500/20 text-rose-300 border-rose-500/40",
    },
    {
      id: 2,
      name: "Motor Vehicle Mechanic",
      sector: "Automotive",
      nco: "7231.0100",
      nsqf: 4,
      ldi: 68.2,
      conf: "High",
      demand: 380,
      supply: 260,
      gap: 120,
      flag: "Emerging Shortage",
      overlays: [],
      badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/40",
    },
    {
      id: 6,
      name: "CNC Machining Technician",
      sector: "Automotive",
      nco: "7223.0100",
      nsqf: 4,
      ldi: 74.5,
      conf: "High",
      demand: 410,
      supply: 245,
      gap: 165,
      flag: "Emerging Shortage",
      overlays: ["Rapid Growth"],
      badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/40",
    },
    {
      id: 10,
      name: "General Duty Assistant",
      sector: "Healthcare",
      nco: "5321.0100",
      nsqf: 3,
      ldi: 78.1,
      conf: "High",
      demand: 490,
      supply: 280,
      gap: 210,
      flag: "Emerging Shortage",
      overlays: [],
      badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/40",
    },
    {
      id: 18,
      name: "Electronics Mechanic",
      sector: "Electronics",
      nco: "7421.0100",
      nsqf: 4,
      ldi: 52.0,
      conf: "Medium",
      demand: 260,
      supply: 250,
      gap: 10,
      flag: "Stable",
      overlays: [],
      badgeColor: "bg-slate-700/50 text-slate-300 border-slate-600",
    },
    {
      id: 21,
      name: "Solar Panel Installation Technician",
      sector: "Electronics",
      nco: "7411.0100",
      nsqf: 4,
      ldi: 82.6,
      conf: "High",
      demand: 390,
      supply: 145,
      gap: 245,
      flag: "Acute Shortage",
      overlays: ["Rapid Growth"],
      badgeColor: "bg-rose-500/20 text-rose-300 border-rose-500/40",
    },
    {
      id: 23,
      name: "Wireman",
      sector: "Electronics",
      nco: "7411.0200",
      nsqf: 3,
      ldi: 38.5,
      conf: "Medium",
      demand: 180,
      supply: 290,
      gap: -110,
      flag: "Approaching Saturation",
      overlays: [],
      badgeColor: "bg-teal-500/20 text-teal-300 border-teal-500/40",
    },
    {
      id: 8,
      name: "Vehicle Painter",
      sector: "Automotive",
      nco: "7132.0100",
      nsqf: 3,
      ldi: 32.1,
      conf: "Medium",
      demand: 110,
      supply: 220,
      gap: -110,
      flag: "Saturated",
      overlays: [],
      badgeColor: "bg-purple-500/20 text-purple-300 border-purple-500/40",
    },
  ];

  const filteredTrades = tradesData.filter((tr) => {
    const matchesSector = selectedSector === "ALL" || tr.sector === selectedSector;
    const matchesSearch =
      tr.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tr.nco.includes(searchQuery);
    return matchesSector && matchesSearch;
  });

  return (
    <div className="space-y-5">
      {/* Breadcrumb Navigation */}
      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400 bg-slate-900 px-4 py-2.5 rounded-lg border border-slate-800">
        <span className="font-semibold text-slate-200">Hierarchy:</span>
        <button
          onClick={() => setSelectedState("KA")}
          className="hover:text-blue-400 font-medium"
        >
          National (India)
        </button>
        <span>&gt;</span>
        <div className="flex items-center gap-1">
          {states.map((st) => (
            <button
              key={st.code}
              onClick={() => {
                setSelectedState(st.code);
                setSelectedDistrictId(st.code === "KA" ? 1 : st.code === "TN" ? 32 : 70);
              }}
              className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors ${
                selectedState === st.code
                  ? "bg-blue-600 text-white"
                  : "bg-slate-800 text-slate-400 hover:text-white"
              }`}
            >
              {st.name}
            </button>
          ))}
        </div>
        <span>&gt;</span>
        <span className="text-blue-400 font-semibold">{currentDist.name}</span>
      </div>

      {/* District Selector Header Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="font-mono text-xs bg-blue-950 text-blue-300 border border-blue-800 px-2 py-0.5 rounded font-bold">
                LGD: {currentDist.lgd}
              </span>
              <h2 className="text-xl font-bold text-white tracking-tight">
                {currentDist.name}, {selectedState === "KA" ? "Karnataka" : selectedState === "TN" ? "Tamil Nadu" : "Uttar Pradesh"}
              </h2>
            </div>
            <div className="text-xs text-slate-400 mt-1 flex items-center gap-4">
              <span>Working Age Population: <strong className="text-slate-200">{currentDist.pop}</strong></span>
              <span>•</span>
              <span className="text-rose-400 font-medium">{currentDist.shortages} Shortages Active</span>
              <span>•</span>
              <span className="text-purple-400 font-medium">{currentDist.surplus} Saturation Risks</span>
            </div>
          </div>

          {/* District Quick-Switch Pills */}
          <div className="flex flex-wrap gap-1.5 max-w-md">
            {activeDistricts.map((d) => (
              <button
                key={d.id}
                onClick={() => setSelectedDistrictId(d.id)}
                className={`px-2.5 py-1 rounded text-xs transition-all ${
                  selectedDistrictId === d.id
                    ? "bg-blue-600 text-white font-semibold shadow"
                    : "bg-slate-800/80 hover:bg-slate-800 text-slate-300 border border-slate-700/60"
                }`}
              >
                {d.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-medium">Filter Sector:</span>
          {["ALL", "Automotive", "Healthcare", "Electronics"].map((sec) => (
            <button
              key={sec}
              onClick={() => setSelectedSector(sec)}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                selectedSector === sec
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-800 text-slate-400 hover:text-white"
              }`}
            >
              {sec}
            </button>
          ))}
        </div>

        <div className="w-64">
          <input
            type="text"
            placeholder="Search trade or NCO code..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Trades Master Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-3">Trade Name & NCO</th>
                <th className="py-3 px-2">Sector</th>
                <th className="py-3 px-2 text-center">NSQF</th>
                <th className="py-3 px-2 text-right">LDI (0-100)</th>
                <th className="py-3 px-2 text-right">Forecast Demand</th>
                <th className="py-3 px-2 text-right">Supply (S_cert)</th>
                <th className="py-3 px-2 text-right">Net Gap</th>
                <th className="py-3 px-3 text-center">Alert Status</th>
                <th className="py-3 px-3 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredTrades.map((tr) => (
                <tr key={tr.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-3">
                    <div className="font-semibold text-slate-100 text-sm">{tr.name}</div>
                    <div className="font-mono text-[10px] text-slate-400">
                      NCO: {tr.nco} <span className="text-slate-500">(indicative)</span>
                    </div>
                  </td>
                  <td className="py-3 px-2 text-slate-300 font-medium">{tr.sector}</td>
                  <td className="py-3 px-2 text-center font-mono text-slate-300">L{tr.nsqf}</td>
                  <td className="py-3 px-2 text-right font-mono font-bold text-blue-400">
                    {tr.ldi.toFixed(1)}
                  </td>
                  <td className="py-3 px-2 text-right font-mono text-slate-200">{tr.demand}</td>
                  <td className="py-3 px-2 text-right font-mono text-slate-200">{tr.supply}</td>
                  <td className="py-3 px-2 text-right font-mono font-bold">
                    <span className={tr.gap > 0 ? "text-rose-400" : "text-purple-400"}>
                      {tr.gap > 0 ? `+${tr.gap}` : tr.gap}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-center">
                    <div className="inline-flex flex-col items-center">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${tr.badgeColor}`}>
                        {tr.flag}
                      </span>
                      {tr.overlays.length > 0 && (
                        <span className="text-[9px] font-mono text-emerald-400 mt-0.5">
                          {tr.overlays.join(", ")}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-3 text-center">
                    <div className="flex items-center justify-center gap-1.5">
                      <button
                        onClick={() => onSelectTrade(tr.id)}
                        className="px-2 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-[11px] font-medium transition-colors"
                        title="View multi-horizon probabilistic forecast"
                      >
                        {t.forecastButton}
                      </button>
                      <button
                        onClick={() => onOpenWhy(tr.id)}
                        className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded text-[11px] font-medium transition-colors"
                        title="Inspect exact source attribution and Kalman weights"
                      >
                        {t.whyButton}
                      </button>
                      <button
                        onClick={() => onOpenScenario(tr.id)}
                        className="px-2 py-1 bg-indigo-600/30 hover:bg-indigo-600/60 text-indigo-300 border border-indigo-500/40 rounded text-[11px] font-medium transition-colors"
                        title="Simulate +15% seat allocation"
                      >
                        {t.simulateButton}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
