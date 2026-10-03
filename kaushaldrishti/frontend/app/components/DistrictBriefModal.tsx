"use client";

import React from "react";
import { Language, translations } from "../i18n";

interface DistrictBriefModalProps {
  isOpen: boolean;
  onClose: () => void;
  stateCode: string;
  districtId: number;
  lang: Language;
}

export const DistrictBriefModal: React.FC<DistrictBriefModalProps> = ({
  isOpen,
  onClose,
  stateCode,
  districtId,
  lang,
}) => {
  if (!isOpen) return null;

  const t = translations[lang];

  // District metadata lookup
  const districtName =
    districtId === 1
      ? "Bengaluru Urban"
      : districtId === 32
      ? "Chennai"
      : districtId === 70
      ? "Gautam Buddha Nagar"
      : `District #${districtId}`;

  const stateName =
    stateCode === "KA" ? "Karnataka" : stateCode === "TN" ? "Tamil Nadu" : "Uttar Pradesh";

  const lgdCode = districtId === 1 ? "556" : districtId === 32 ? "603" : "154";
  const population = districtId === 1 ? "9,621,551" : districtId === 32 ? "7,088,403" : "1,648,195";

  const topShortages = [
    { trade: "EV Service Technician", sector: "Automotive", demand: 198, supply: 162, gap: 36, p_S: 0.84, sev: 40.0 },
    { trade: "Solar PV Installation Technician", sector: "Electronics", demand: 154, supply: 122, gap: 32, p_S: 0.78, sev: 33.2 },
    { trade: "CNC Machining Technician", sector: "Capital Goods", demand: 135, supply: 128, gap: 7, p_S: 0.28, sev: 11.2 },
    { trade: "Drone Assembly & Pilot", sector: "Aerospace", demand: 88, supply: 52, gap: 36, p_S: 0.81, sev: 38.5 },
    { trade: "Heavy Machinery Mechanic", sector: "Capital Goods", demand: 110, supply: 85, gap: 25, p_S: 0.74, sev: 29.8 },
  ];

  const topSaturations = [
    { trade: "Data Entry Operator", sector: "IT-ITeS", demand: 85, supply: 160, gap: -75, p_O: 0.92, sev: 68.4 },
    { trade: "Basic Sewing Machine Operator", sector: "Apparel", demand: 140, supply: 190, gap: -50, p_O: 0.85, sev: 51.0 },
    { trade: "General Office Assistant", sector: "Management", demand: 60, supply: 105, gap: -45, p_O: 0.81, sev: 46.2 },
  ];

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-sm">
      <div className="bg-white text-slate-900 rounded-2xl max-w-3xl w-full max-h-[92vh] overflow-y-auto shadow-2xl p-6 sm:p-8 space-y-6 print:p-0 print:shadow-none print:max-h-none print:rounded-none">
        {/* Print & Close Toolbar (hidden during print) */}
        <div className="flex items-center justify-between border-b border-slate-200 pb-3 print:hidden">
          <div className="text-xs text-slate-500 font-medium">
            1-Page District Executive Brief • Ready for Print
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              className="px-4 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-slate-950 text-xs font-bold transition flex items-center gap-1.5 shadow"
            >
              <span>🖨️</span>
              <span>{t.printBrief}</span>
            </button>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center font-bold text-lg transition"
            >
              &times;
            </button>
          </div>
        </div>

        {/* Official Header */}
        <div className="border-b-2 border-slate-900 pb-4 text-center space-y-1">
          <div className="text-[10px] tracking-widest uppercase font-semibold text-slate-600">
            Government of India • Ministry of Skill Development &amp; Entrepreneurship
          </div>
          <h1 className="text-xl sm:text-2xl font-black tracking-tight text-slate-950 uppercase">
            District Skill Development Executive Brief
          </h1>
          <div className="text-xs font-bold text-amber-800">
            {districtName.toUpperCase()} &bull; {stateName.toUpperCase()}
          </div>
          <div className="text-[11px] text-slate-500 flex justify-center items-center gap-4 pt-1 font-mono">
            <span>LGD Code: {lgdCode}</span>
            <span>&bull;</span>
            <span>Census Pop: {population}</span>
            <span>&bull;</span>
            <span>Refreshed: Month 48 (Current)</span>
          </div>
        </div>

        {/* Executive Summary */}
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
          <div className="text-xs font-bold uppercase tracking-wider text-slate-800">
            Executive Summary
          </div>
          <p className="text-xs text-slate-700 leading-relaxed">
            In <strong>{districtName}</strong>, 40 priority trades were evaluated across a 48-month panel dataset. Analysis indicates an aggregate monthly demand of <strong>3,410 vacancies</strong> against a certified institutional output of <strong>2,980 graduates</strong>. Net district deficit stands at <strong>430 skilled workers</strong>, concentrated in Electric Mobility, Solar Installations, and High-Precision Machining.
          </p>
        </div>

        {/* Top 5 Shortages Table */}
        <div className="space-y-2">
          <div className="text-xs font-bold uppercase tracking-wider text-rose-800 flex items-center justify-between">
            <span>Critical Shortage Trades (Immediate Intervention Needed)</span>
            <span className="text-[10px] font-normal text-slate-500">Ranked by Severity</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border border-slate-200 border-collapse">
              <thead>
                <tr className="bg-slate-100 text-slate-700 border-b border-slate-200 font-semibold">
                  <th className="py-2 px-2.5">Trade Name</th>
                  <th className="py-2 px-2">Sector</th>
                  <th className="py-2 px-2 text-right">Demand</th>
                  <th className="py-2 px-2 text-right">Supply</th>
                  <th className="py-2 px-2 text-right">Net Gap</th>
                  <th className="py-2 px-2 text-right">p_S</th>
                  <th className="py-2 px-2 text-right">Severity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono text-slate-800">
                {topShortages.map((s) => (
                  <tr key={s.trade} className="hover:bg-slate-50">
                    <td className="py-2 px-2.5 font-sans font-medium text-slate-900">{s.trade}</td>
                    <td className="py-2 px-2 font-sans text-slate-600">{s.sector}</td>
                    <td className="py-2 px-2 text-right">{s.demand}</td>
                    <td className="py-2 px-2 text-right text-emerald-700">{s.supply}</td>
                    <td className="py-2 px-2 text-right font-bold text-rose-700">+{s.gap}</td>
                    <td className="py-2 px-2 text-right">{(s.p_S * 100).toFixed(0)}%</td>
                    <td className="py-2 px-2 text-right font-bold">{s.sev.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Top Saturations Table */}
        <div className="space-y-2">
          <div className="text-xs font-bold uppercase tracking-wider text-purple-800 flex items-center justify-between">
            <span>Saturated Trades (Recommended Seat Right-Sizing)</span>
            <span className="text-[10px] font-normal text-slate-500">Over-supplied Capacity</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border border-slate-200 border-collapse">
              <thead>
                <tr className="bg-slate-100 text-slate-700 border-b border-slate-200 font-semibold">
                  <th className="py-2 px-2.5">Trade Name</th>
                  <th className="py-2 px-2">Sector</th>
                  <th className="py-2 px-2 text-right">Demand</th>
                  <th className="py-2 px-2 text-right">Supply</th>
                  <th className="py-2 px-2 text-right">Surplus</th>
                  <th className="py-2 px-2 text-right">p_O</th>
                  <th className="py-2 px-2 text-right">Severity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono text-slate-800">
                {topSaturations.map((s) => (
                  <tr key={s.trade} className="hover:bg-slate-50">
                    <td className="py-2 px-2.5 font-sans font-medium text-slate-900">{s.trade}</td>
                    <td className="py-2 px-2 font-sans text-slate-600">{s.sector}</td>
                    <td className="py-2 px-2 text-right">{s.demand}</td>
                    <td className="py-2 px-2 text-right text-emerald-700">{s.supply}</td>
                    <td className="py-2 px-2 text-right font-bold text-purple-700">{s.gap}</td>
                    <td className="py-2 px-2 text-right">{(s.p_O * 100).toFixed(0)}%</td>
                    <td className="py-2 px-2 text-right font-bold">{s.sev.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Policy Recommendations Callout */}
        <div className="bg-amber-50 border border-amber-200 p-3.5 rounded-xl text-xs space-y-1 text-slate-800">
          <div className="font-bold text-amber-900 uppercase tracking-wider text-[11px]">
            Action Recommendations for District Skill Committee (DSC)
          </div>
          <p>
            1. <strong>Seat Reallocation:</strong> Reallocate 30 under-utilized seats from <em>Data Entry Operator</em> to <em>EV Service Technician</em> in government ITIs.
          </p>
          <p>
            2. <strong>Apprenticeship Corroboration:</strong> Expand NAPS contracts with automotive clusters in Peenya and Hosur Road to bridge cohort lag.
          </p>
        </div>

        {/* Mandatory Honest Labelling Stamp */}
        <div className="border-t border-slate-200 pt-3 flex flex-wrap items-center justify-between text-[10px] text-slate-500 font-mono">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-700 uppercase">Labelling Standard:</span>
            <span className="px-1.5 py-0.5 rounded bg-amber-100 text-amber-900 border border-amber-300">
              data_mode: synthetic (SIH 2026 Evaluation Dataset)
            </span>
          </div>
          <div>System: KaushalDrishti LMIS v1.0.0</div>
        </div>
      </div>
    </div>
  );
};
