"use client";

import React, { useState } from "react";
import { Language, translations } from "../i18n";

interface EarlyWarningCentreProps {
  lang: Language;
  onSelectCell: (stateCode: string, districtId: number, tradeId: number) => void;
  onOpenWhy: (tradeId: number) => void;
  lowBandwidth: boolean;
}

interface AlertItem {
  id: string;
  stateCode: string;
  districtId: number;
  districtName: string;
  tradeId: number;
  tradeTitle: string;
  sector: string;
  flagType: "Acute Shortage" | "Emerging Shortage" | "Approaching Saturation" | "Saturated" | "Balanced";
  overlay: "Rapid Growth" | "Volatile" | "None";
  demandForecast: number;
  certifiedSupply: number;
  netGap: number;
  pShortage: number;
  pSaturation: number;
  tolerance: number;
  severity: number;
  persistenceCount: number;
  dataMode: string;
  historyTransitions: { refresh: number; flag: string; reason: string }[];
}

export const EarlyWarningCentre: React.FC<EarlyWarningCentreProps> = ({
  lang,
  onSelectCell,
  onOpenWhy,
  lowBandwidth,
}) => {
  const t = translations[lang];
  const [filterState, setFilterState] = useState<string>("ALL");
  const [filterStatus, setFilterStatus] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [expandedId, setExpandedId] = useState<string | null>("KA-1-1");

  // Sample master alerts registry (calibrated to M5 state machine & planted episodes)
  const alerts: AlertItem[] = [
    {
      id: "KA-1-1",
      stateCode: "KA",
      districtId: 1,
      districtName: "Bengaluru Urban",
      tradeId: 1,
      tradeTitle: "EV Service Technician",
      sector: "Automotive",
      flagType: "Acute Shortage",
      overlay: "Rapid Growth",
      demandForecast: 198,
      certifiedSupply: 162,
      netGap: 36,
      pShortage: 0.84,
      pSaturation: 0.03,
      tolerance: 20,
      severity: 40.0,
      persistenceCount: 3,
      dataMode: "synthetic",
      historyTransitions: [
        { refresh: 46, flag: "Emerging Shortage", reason: "Growth differential +22%, p_S = 0.68" },
        { refresh: 47, flag: "Acute Shortage (Candidate)", reason: "p_S = 0.82 >= 0.80, pending 2nd refresh confirmation" },
        { refresh: 48, flag: "Acute Shortage (Confirmed)", reason: "p_S = 0.84 >= 0.80, hysteresis confirmed" },
      ],
    },
    {
      id: "KA-1-2",
      stateCode: "KA",
      districtId: 1,
      districtName: "Bengaluru Urban",
      tradeId: 2,
      tradeTitle: "Solar PV Installation Technician",
      sector: "Electronics",
      flagType: "Emerging Shortage",
      overlay: "Rapid Growth",
      demandForecast: 154,
      certifiedSupply: 122,
      netGap: 32,
      pShortage: 0.78,
      pSaturation: 0.05,
      tolerance: 15,
      severity: 33.2,
      persistenceCount: 2,
      dataMode: "synthetic",
      historyTransitions: [
        { refresh: 47, flag: "Balanced", reason: "Within tolerance band" },
        { refresh: 48, flag: "Emerging Shortage", reason: "p_S jumped to 0.78 with +18% growth" },
      ],
    },
    {
      id: "TN-32-6",
      stateCode: "TN",
      districtId: 32,
      districtName: "Chennai",
      tradeId: 4,
      tradeTitle: "CNC Machining Technician",
      sector: "Capital Goods",
      flagType: "Acute Shortage",
      overlay: "None",
      demandForecast: 215,
      certifiedSupply: 170,
      netGap: 45,
      pShortage: 0.88,
      pSaturation: 0.01,
      tolerance: 22,
      severity: 45.6,
      persistenceCount: 4,
      dataMode: "synthetic",
      historyTransitions: [
        { refresh: 45, flag: "Emerging Shortage", reason: "Initial capacity deficit" },
        { refresh: 46, flag: "Acute Shortage (Candidate)", reason: "p_S = 0.83" },
        { refresh: 47, flag: "Acute Shortage (Confirmed)", reason: "Confirmed 2 refreshes" },
        { refresh: 48, flag: "Acute Shortage (Confirmed)", reason: "Severity sustained at 45.6" },
      ],
    },
    {
      id: "UP-70-1",
      stateCode: "UP",
      districtId: 70,
      districtName: "Gautam Buddha Nagar",
      tradeId: 1,
      tradeTitle: "EV Service Technician",
      sector: "Automotive",
      flagType: "Acute Shortage",
      overlay: "Rapid Growth",
      demandForecast: 182,
      certifiedSupply: 130,
      netGap: 52,
      pShortage: 0.89,
      pSaturation: 0.02,
      tolerance: 18,
      severity: 51.4,
      persistenceCount: 3,
      dataMode: "synthetic",
      historyTransitions: [
        { refresh: 46, flag: "Emerging Shortage", reason: "Noida EV manufacturing cluster ramp-up" },
        { refresh: 47, flag: "Acute Shortage (Candidate)", reason: "p_S = 0.86" },
        { refresh: 48, flag: "Acute Shortage (Confirmed)", reason: "Hysteresis confirmed" },
      ],
    },
    {
      id: "UP-71-3",
      stateCode: "UP",
      districtId: 71,
      districtName: "Lucknow",
      tradeId: 3,
      tradeTitle: "Data Entry Operator",
      sector: "IT-ITeS",
      flagType: "Saturated",
      overlay: "None",
      demandForecast: 95,
      certifiedSupply: 185,
      netGap: -90,
      pShortage: 0.01,
      pSaturation: 0.94,
      tolerance: 10,
      severity: 75.2,
      persistenceCount: 6,
      dataMode: "synthetic",
      historyTransitions: [
        { refresh: 46, flag: "Approaching Saturation", reason: "p_O = 0.74, intake outpaced demand" },
        { refresh: 47, flag: "Saturated (Candidate)", reason: "p_O = 0.91, g = -0.42" },
        { refresh: 48, flag: "Saturated (Confirmed)", reason: "Confirmed 2 refreshes, persistent oversupply" },
      ],
    },
    {
      id: "KA-2-3",
      stateCode: "KA",
      districtId: 2,
      districtName: "Mysuru",
      tradeId: 3,
      tradeTitle: "Data Entry Operator",
      sector: "IT-ITeS",
      flagType: "Approaching Saturation",
      overlay: "None",
      demandForecast: 60,
      certifiedSupply: 95,
      netGap: -35,
      pShortage: 0.04,
      pSaturation: 0.72,
      tolerance: 8,
      severity: 38.0,
      persistenceCount: 2,
      dataMode: "synthetic",
      historyTransitions: [
        { refresh: 47, flag: "Balanced", reason: "Prior intake pipeline" },
        { refresh: 48, flag: "Approaching Saturation", reason: "p_O = 0.72 > 0.60 threshold" },
      ],
    },
    {
      id: "TN-36-8",
      stateCode: "TN",
      districtId: 36,
      districtName: "Tiruppur",
      tradeId: 8,
      tradeTitle: "Sewing Machine Operator",
      sector: "Apparel",
      flagType: "Acute Shortage",
      overlay: "Volatile",
      demandForecast: 320,
      certifiedSupply: 240,
      netGap: 80,
      pShortage: 0.86,
      pSaturation: 0.02,
      tolerance: 32,
      severity: 48.2,
      persistenceCount: 3,
      dataMode: "synthetic",
      historyTransitions: [
        { refresh: 46, flag: "Emerging Shortage", reason: "Export garment seasonal surge" },
        { refresh: 47, flag: "Acute Shortage (Candidate)", reason: "High residual variance flagged" },
        { refresh: 48, flag: "Acute Shortage (Confirmed)", reason: "Overlay marked Volatile" },
      ],
    },
  ];

  // Filtering
  const filteredAlerts = alerts.filter((a) => {
    if (filterState !== "ALL" && a.stateCode !== filterState) return false;
    if (filterStatus !== "ALL" && a.flagType !== filterStatus) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchText = `${a.tradeTitle} ${a.districtName} ${a.sector}`.toLowerCase();
      if (!matchText.includes(q)) return false;
    }
    return true;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "Acute Shortage":
        return <span className="px-2 py-0.5 text-xs font-bold rounded bg-rose-500/20 text-rose-300 border border-rose-500/40">Acute Shortage</span>;
      case "Emerging Shortage":
        return <span className="px-2 py-0.5 text-xs font-bold rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">Emerging Shortage</span>;
      case "Approaching Saturation":
        return <span className="px-2 py-0.5 text-xs font-bold rounded bg-teal-500/20 text-teal-300 border border-teal-500/40">Approaching Saturation</span>;
      case "Saturated":
        return <span className="px-2 py-0.5 text-xs font-bold rounded bg-purple-500/20 text-purple-300 border border-purple-500/40">Saturated</span>;
      default:
        return <span className="px-2 py-0.5 text-xs font-bold rounded bg-slate-800 text-slate-300 border border-slate-700">Balanced</span>;
    }
  };

  const getOverlayBadge = (overlay: string) => {
    if (overlay === "Rapid Growth") {
      return <span className="px-1.5 py-0.5 text-[10px] font-semibold rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">⚡ Rapid Growth</span>;
    }
    if (overlay === "Volatile") {
      return <span className="px-1.5 py-0.5 text-[10px] font-semibold rounded bg-orange-500/20 text-orange-300 border border-orange-500/30">⚠️ Volatile</span>;
    }
    return null;
  };

  const handleDownloadCsv = () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    window.open(`${apiUrl}/api/v1/export?format=csv`, "_blank");
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30">
              Section 8: Hysteresis State Machine
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700">
              data_mode: synthetic
            </span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">
            {t.navAlerts} &amp; Risk Register
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time multi-district early warning. Requires 2 consecutive refreshes to raise or escalate; de-escalation requires (threshold - 0.10) margin.
          </p>
        </div>

        {/* Export Button */}
        <button
          onClick={handleDownloadCsv}
          className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-2 transition shadow"
        >
          <span>📥</span>
          <span>{t.exportCsv} (Full 144 Districts)</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-2">
          {/* State Filter */}
          <div className="flex items-center gap-1.5 bg-slate-950 px-2.5 py-1.5 rounded-lg border border-slate-800">
            <span className="text-slate-400 font-medium">State:</span>
            <select
              value={filterState}
              onChange={(e) => setFilterState(e.target.value)}
              className="bg-transparent text-white outline-none cursor-pointer"
            >
              <option value="ALL" className="bg-slate-900">All Pilot States</option>
              <option value="KA" className="bg-slate-900">Karnataka (31)</option>
              <option value="TN" className="bg-slate-900">Tamil Nadu (38)</option>
              <option value="UP" className="bg-slate-900">Uttar Pradesh (75)</option>
            </select>
          </div>

          {/* Status Filter */}
          <div className="flex items-center gap-1.5 bg-slate-950 px-2.5 py-1.5 rounded-lg border border-slate-800">
            <span className="text-slate-400 font-medium">Status:</span>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-transparent text-white outline-none cursor-pointer"
            >
              <option value="ALL" className="bg-slate-900">All Statuses</option>
              <option value="Acute Shortage" className="bg-slate-900">Acute Shortage</option>
              <option value="Emerging Shortage" className="bg-slate-900">Emerging Shortage</option>
              <option value="Approaching Saturation" className="bg-slate-900">Approaching Saturation</option>
              <option value="Saturated" className="bg-slate-900">Saturated</option>
            </select>
          </div>
        </div>

        {/* Search Box */}
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <input
            type="text"
            placeholder="Search district, trade, or sector..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full sm:w-64 bg-slate-950 text-white border border-slate-800 rounded-lg px-3 py-1.5 text-xs outline-none focus:border-amber-500"
          />
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950 text-slate-400">
                <th className="py-3 px-4 font-semibold">Location &amp; Trade</th>
                <th className="py-3 px-3 font-semibold">Status &amp; Overlays</th>
                <th className="py-3 px-3 font-semibold">Demand E[D]</th>
                <th className="py-3 px-3 font-semibold">Supply S_W</th>
                <th className="py-3 px-3 font-semibold">Net Gap</th>
                <th className="py-3 px-3 font-semibold">p_S / p_O</th>
                <th className="py-3 px-3 font-semibold">Severity</th>
                <th className="py-3 px-3 font-semibold">Persistence</th>
                <th className="py-3 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {filteredAlerts.length > 0 ? (
                filteredAlerts.map((alert) => {
                  const isExpanded = expandedId === alert.id;
                  return (
                    <React.Fragment key={alert.id}>
                      <tr className="hover:bg-slate-800/40 transition">
                        <td className="py-3 px-4">
                          <div className="font-bold text-white text-sm">
                            {alert.tradeTitle}
                          </div>
                          <div className="text-[11px] text-slate-400 flex items-center gap-2 mt-0.5">
                            <span className="text-amber-400">{alert.districtName} ({alert.stateCode})</span>
                            <span>•</span>
                            <span className="text-slate-500">{alert.sector}</span>
                          </div>
                        </td>

                        <td className="py-3 px-3">
                          <div className="flex flex-col gap-1 items-start">
                            {getStatusBadge(alert.flagType)}
                            {getOverlayBadge(alert.overlay)}
                          </div>
                        </td>

                        <td className="py-3 px-3 font-mono font-semibold text-blue-400">
                          {alert.demandForecast}
                        </td>

                        <td className="py-3 px-3 font-mono font-semibold text-emerald-400">
                          {alert.certifiedSupply}
                        </td>

                        <td className="py-3 px-3 font-mono font-bold">
                          <span className={alert.netGap > 0 ? "text-rose-400" : "text-purple-400"}>
                            {alert.netGap > 0 ? `+${alert.netGap}` : alert.netGap}
                          </span>
                        </td>

                        <td className="py-3 px-3 font-mono text-slate-300">
                          {alert.netGap > 0 ? (
                            <span className="text-rose-400 font-semibold">
                              {(alert.pShortage * 100).toFixed(0)}%
                            </span>
                          ) : (
                            <span className="text-purple-400 font-semibold">
                              {(alert.pSaturation * 100).toFixed(0)}%
                            </span>
                          )}
                        </td>

                        <td className="py-3 px-3 font-mono font-bold text-amber-400">
                          {alert.severity.toFixed(1)}
                        </td>

                        <td className="py-3 px-3 font-mono text-slate-300">
                          <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-[10px]">
                            {alert.persistenceCount} cycles
                          </span>
                        </td>

                        <td className="py-3 px-4 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => setExpandedId(isExpanded ? null : alert.id)}
                              className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-medium transition"
                            >
                              {isExpanded ? "Hide History" : "History"}
                            </button>
                            <button
                              onClick={() => onOpenWhy(alert.tradeId)}
                              className="px-2 py-1 rounded bg-blue-600/80 hover:bg-blue-600 text-white text-[11px] font-medium transition"
                            >
                              Why
                            </button>
                            <button
                              onClick={() =>
                                onSelectCell(alert.stateCode, alert.districtId, alert.tradeId)
                              }
                              className="px-2 py-1 rounded bg-amber-500 hover:bg-amber-400 text-slate-950 text-[11px] font-bold transition"
                            >
                              Forecast &rarr;
                            </button>
                          </div>
                        </td>
                      </tr>

                      {/* Expandable Alert History Sub-row */}
                      {isExpanded && (
                        <tr className="bg-slate-950/70 border-b border-slate-800">
                          <td colSpan={9} className="py-3 px-6">
                            <div className="space-y-2">
                              <div className="flex items-center justify-between text-xs text-slate-400">
                                <span className="font-semibold uppercase tracking-wider text-amber-400">
                                  Hysteresis State Machine History (AlertHistory Audit Log)
                                </span>
                                <span className="font-mono text-[10px]">Cell: {alert.id}</span>
                              </div>
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                                {alert.historyTransitions.map((tr, idx) => (
                                  <div
                                    key={idx}
                                    className="bg-slate-900 p-2.5 rounded-lg border border-slate-800 text-[11px] space-y-1"
                                  >
                                    <div className="flex items-center justify-between font-mono text-slate-400">
                                      <span>Refresh #{tr.refresh}</span>
                                      <span className="text-amber-400 font-semibold">{tr.flag}</span>
                                    </div>
                                    <p className="text-slate-300 text-[10px]">{tr.reason}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-500">
                    No early warnings match the selected filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
