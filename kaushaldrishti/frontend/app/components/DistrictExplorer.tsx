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
      badgeColor: "bg-[#DE1110]/20 text-[#DE1110] border-[#DE1110]/40 font-bold",
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
      sector: "Capital Goods",
      nco: "7223.0101",
      nsqf: 4,
      ldi: 74.5,
      conf: "High",
      demand: 410,
      supply: 190,
      gap: 220,
      flag: "Acute Shortage",
      overlays: [],
      badgeColor: "bg-[#DE1110]/20 text-[#DE1110] border-[#DE1110]/40 font-bold",
    },
    {
      id: 10,
      name: "Solar PV Installation Technician",
      sector: "Electronics",
      nco: "7421.0300",
      nsqf: 4,
      ldi: 82.1,
      conf: "High",
      demand: 310,
      supply: 110,
      gap: 200,
      flag: "Acute Shortage",
      overlays: ["Rapid Growth"],
      badgeColor: "bg-[#DE1110]/20 text-[#DE1110] border-[#DE1110]/40 font-bold",
    },
    {
      id: 15,
      name: "General Duty Assistant (GDA)",
      sector: "Healthcare",
      nco: "5321.0100",
      nsqf: 4,
      ldi: 62.8,
      conf: "Medium",
      demand: 290,
      supply: 220,
      gap: 70,
      flag: "Emerging Shortage",
      overlays: [],
      badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/40",
    },
    {
      id: 23,
      name: "Wireman",
      sector: "Construction",
      nco: "7411.0100",
      nsqf: 3,
      ldi: 44.2,
      conf: "High",
      demand: 180,
      supply: 210,
      gap: -30,
      flag: "Balanced",
      overlays: [],
      badgeColor: "bg-[#05216e] text-slate-300 border-[#133896]",
    },
    {
      id: 35,
      name: "Data Entry Operator",
      sector: "IT-ITeS",
      nco: "4132.0401",
      nsqf: 3,
      ldi: 31.4,
      conf: "High",
      demand: 140,
      supply: 320,
      gap: -180,
      flag: "Saturated",
      overlays: [],
      badgeColor: "bg-purple-500/20 text-purple-300 border-purple-500/40",
    },
  ];

  const sectors = ["ALL", "Automotive", "Capital Goods", "Electronics", "Healthcare", "Construction", "IT-ITeS"];

  const filteredTrades = tradesData.filter((tr) => {
    if (selectedSector !== "ALL" && tr.sector !== selectedSector) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return tr.name.toLowerCase().includes(q) || tr.nco.includes(q);
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* State & District Breadcrumb Selector */}
      <div className="bg-[#021861] border border-[#133896] rounded-xl p-5 shadow-lg flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-wider text-blue-200 font-bold mb-1 flex items-center gap-2">
            <span>District Intelligence Drill-down</span>
            <span className="text-[10px] bg-[#DE1110] text-white px-1.5 py-0.2 rounded font-bold">
              Team PROMETHEUSS
            </span>
          </div>
          <div className="flex items-center gap-2 text-xl font-black text-white">
            <span>{selectedState === "KA" ? "Karnataka" : selectedState === "TN" ? "Tamil Nadu" : "Uttar Pradesh"}</span>
            <span className="text-[#255DCE]">&rarr;</span>
            <span className="text-blue-200">{currentDist.name}</span>
          </div>
          <div className="text-xs text-slate-300 mt-1 flex items-center gap-3 font-mono">
            <span>LGD: {currentDist.lgd}</span>
            <span>&bull;</span>
            <span>Pop: {currentDist.pop}</span>
            <span>&bull;</span>
            <span className="text-[#DE1110] font-bold">{currentDist.shortages} Shortages</span>
          </div>
        </div>

        {/* State Toggle Buttons */}
        <div className="flex items-center gap-2 bg-[#010e3b] p-1.5 rounded-lg border border-[#133896]">
          {states.map((st) => (
            <button
              key={st.code}
              onClick={() => {
                setSelectedState(st.code);
                const newDist = st.code === "KA" ? districtsKA[0] : st.code === "TN" ? districtsTN[0] : districtsUP[0];
                setSelectedDistrictId(newDist.id);
              }}
              className={`px-3 py-1.5 rounded text-xs font-bold transition-all ${
                selectedState === st.code
                  ? "bg-[#255DCE] text-white shadow-md"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              {st.name} ({st.districtsCount})
            </button>
          ))}
        </div>
      </div>

      {/* District Cards Slider/Grid */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Select District in {selectedState === "KA" ? "Karnataka" : selectedState === "TN" ? "Tamil Nadu" : "Uttar Pradesh"}
          </span>
          <span className="text-xs text-blue-300 font-mono">
            Showing {activeDistricts.length} Pilot Districts
          </span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2.5">
          {activeDistricts.map((d) => {
            const isSelected = d.id === selectedDistrictId;
            return (
              <button
                key={d.id}
                onClick={() => setSelectedDistrictId(d.id)}
                className={`p-3 rounded-xl border text-left transition-all ${
                  isSelected
                    ? "bg-[#05216e] border-[#255DCE] ring-2 ring-[#255DCE] text-white shadow-lg"
                    : "bg-[#021861] border-[#133896] text-slate-200 hover:border-[#255DCE] hover:bg-[#05216e]"
                }`}
              >
                <div className="font-bold text-xs truncate">{d.name}</div>
                <div className="text-[10px] text-slate-300 font-mono mt-1">LGD: {d.lgd}</div>
                <div className="mt-2 flex items-center justify-between text-[10px] font-mono">
                  <span className="text-[#DE1110] font-black">{d.shortages} short</span>
                  <span className="text-purple-300">{d.surplus} sat</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Sector Filters & Search Bar */}
      <div className="bg-[#021861] border border-[#133896] rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 shadow-md">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-xs font-bold text-slate-300 mr-1">Sector:</span>
          {sectors.map((sec) => (
            <button
              key={sec}
              onClick={() => setSelectedSector(sec)}
              className={`px-3 py-1 rounded text-xs font-bold transition-colors ${
                selectedSector === sec
                  ? "bg-[#255DCE] text-white shadow"
                  : "bg-[#010e3b] text-slate-300 border border-[#133896] hover:text-white hover:bg-[#05216e]"
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
            className="w-full bg-[#010e3b] border border-[#133896] rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-[#255DCE]"
          />
        </div>
      </div>

      {/* Trades Master Table */}
      <div className="bg-[#021861] border border-[#133896] rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#010e3b] text-slate-300 font-bold border-b border-[#133896]">
              <tr>
                <th className="py-3 px-3">Trade Name &amp; NCO</th>
                <th className="py-3 px-2">Sector</th>
                <th className="py-3 px-2 text-center">NSQF</th>
                <th className="py-3 px-2 text-right">LDI (0-100)</th>
                <th className="py-3 px-2 text-right">Demand (E[D])</th>
                <th className="py-3 px-2 text-right">Supply (S_cert)</th>
                <th className="py-3 px-2 text-right">Net Gap</th>
                <th className="py-3 px-3 text-center">Alert Status</th>
                <th className="py-3 px-3 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#133896]/60">
              {filteredTrades.map((tr) => (
                <tr key={tr.id} className="hover:bg-[#05216e]/60 transition-colors">
                  <td className="py-3 px-3">
                    <div className="font-bold text-white text-sm">{tr.name}</div>
                    <div className="font-mono text-[10px] text-blue-200">
                      NCO: {tr.nco} <span className="text-slate-400 font-normal">(indicative)</span>
                    </div>
                  </td>
                  <td className="py-3 px-2 text-slate-200 font-medium">{tr.sector}</td>
                  <td className="py-3 px-2 text-center font-mono text-slate-300">L{tr.nsqf}</td>
                  <td className="py-3 px-2 text-right font-mono font-black text-amber-300">
                    {tr.ldi.toFixed(1)}
                  </td>
                  <td className="py-3 px-2 text-right font-mono text-blue-300 font-bold">{tr.demand}</td>
                  <td className="py-3 px-2 text-right font-mono text-emerald-400 font-bold">{tr.supply}</td>
                  <td className="py-3 px-2 text-right font-mono font-bold">
                    <span className={tr.gap > 0 ? "text-[#DE1110] font-black" : "text-purple-300"}>
                      {tr.gap > 0 ? `+${tr.gap}` : tr.gap}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-center">
                    <div className="inline-flex flex-col items-center">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${tr.badgeColor}`}>
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
                        className="px-2.5 py-1 bg-[#255DCE] hover:bg-[#1e4eb2] text-white rounded text-[11px] font-bold transition-colors shadow-sm"
                        title="View multi-horizon probabilistic forecast"
                      >
                        {t.forecastButton}
                      </button>
                      <button
                        onClick={() => onOpenWhy(tr.id)}
                        className="px-2.5 py-1 bg-[#010e3b] hover:bg-[#05216e] text-blue-200 border border-[#255DCE]/50 rounded text-[11px] font-semibold transition-colors"
                        title="Inspect exact source attribution and Kalman weights"
                      >
                        {t.whyButton}
                      </button>
                      <button
                        onClick={() => onOpenScenario(tr.id)}
                        className="px-2.5 py-1 bg-[#255DCE]/20 hover:bg-[#255DCE]/40 text-blue-200 border border-[#255DCE]/60 rounded text-[11px] font-bold transition-colors"
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
