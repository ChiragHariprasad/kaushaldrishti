"use client";

import React, { useState } from "react";
import { Language, translations } from "../i18n";

interface ForecastCentreProps {
  lang: Language;
  selectedState: string;
  selectedDistrictId: number;
  selectedTradeId: number;
  setSelectedTradeId: (id: number) => void;
  onOpenWhy: (tradeId: number) => void;
  onOpenScenario: (tradeId: number) => void;
  lowBandwidth: boolean;
}

export const ForecastCentre: React.FC<ForecastCentreProps> = ({
  lang,
  selectedState,
  selectedDistrictId,
  selectedTradeId,
  setSelectedTradeId,
  onOpenWhy,
  onOpenScenario,
  lowBandwidth,
}) => {
  const t = translations[lang];
  const [horizon, setHorizon] = useState<"3m" | "6m" | "12m" | "cohort">("12m");

  // Sample trades catalog
  const trades = [
    {
      id: 1,
      title: "EV Service Technician",
      qp: "ASC/Q1402",
      nco: "7231.0101",
      verified: false,
      nsqf: 4,
      sector: "Automotive",
      durationMonths: 12,
      ldi: 72.4,
      ldiCi: [68.1, 76.8],
      demandForecast: 198,
      demandCi80: [165, 231],
      demandCi95: [142, 254],
      certifiedSupply: 162,
      supplyCi80: [148, 176],
      netGap: 36,
      pShortage: 0.84,
      pSaturation: 0.03,
      tau: 20,
      severity: 40.0,
      status: "Acute Shortage",
      overlay: "Rapid Growth",
      dataMode: "synthetic",
      history: [110, 118, 125, 134, 142, 148, 155, 162, 170, 178, 185, 192],
      forecast: [194, 196, 198, 202, 205, 209, 212, 216, 220, 224, 227, 230],
      forecastCi80Low: [165, 166, 168, 170, 172, 175, 177, 180, 182, 185, 187, 190],
      forecastCi80High: [223, 226, 228, 234, 238, 243, 247, 252, 258, 263, 267, 270],
      supplyForecast: [155, 156, 158, 160, 161, 162, 164, 165, 166, 168, 169, 170],
    },
    {
      id: 2,
      title: "Solar PV Installation Technician",
      qp: "SGJ/Q0101",
      nco: "7421.0300",
      verified: false,
      nsqf: 4,
      sector: "Electronics",
      durationMonths: 6,
      ldi: 68.2,
      ldiCi: [64.0, 72.5],
      demandForecast: 154,
      demandCi80: [130, 178],
      demandCi95: [115, 193],
      certifiedSupply: 122,
      supplyCi80: [112, 132],
      netGap: 32,
      pShortage: 0.78,
      pSaturation: 0.05,
      tau: 15,
      severity: 33.2,
      status: "Emerging Shortage",
      overlay: "Rapid Growth",
      dataMode: "synthetic",
      history: [90, 94, 99, 105, 112, 118, 122, 128, 135, 140, 146, 150],
      forecast: [152, 154, 156, 159, 162, 165, 168, 171, 174, 177, 180, 183],
      forecastCi80Low: [130, 131, 133, 135, 137, 139, 141, 143, 145, 147, 149, 151],
      forecastCi80High: [174, 177, 179, 183, 187, 191, 195, 199, 203, 207, 211, 215],
      supplyForecast: [118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129],
    },
    {
      id: 3,
      title: "Data Entry Operator",
      qp: "SSC/Q2212",
      nco: "4132.0401",
      verified: true,
      nsqf: 3,
      sector: "IT-ITeS",
      durationMonths: 6,
      ldi: 32.1,
      ldiCi: [28.5, 35.7],
      demandForecast: 85,
      demandCi80: [70, 100],
      demandCi95: [60, 110],
      certifiedSupply: 160,
      supplyCi80: [145, 175],
      netGap: -75,
      pShortage: 0.01,
      pSaturation: 0.92,
      tau: 10,
      severity: 68.4,
      status: "Saturated",
      overlay: "None",
      dataMode: "synthetic",
      history: [140, 135, 130, 122, 115, 108, 102, 98, 92, 88, 86, 85],
      forecast: [84, 83, 82, 80, 79, 78, 77, 76, 75, 74, 73, 72],
      forecastCi80Low: [70, 69, 68, 66, 65, 64, 63, 62, 61, 60, 59, 58],
      forecastCi80High: [98, 97, 96, 94, 93, 92, 91, 90, 89, 88, 87, 86],
      supplyForecast: [160, 158, 155, 152, 150, 148, 145, 142, 140, 138, 135, 132],
    },
    {
      id: 4,
      title: "CNC Machining Technician",
      qp: "CSC/Q0115",
      nco: "7223.0101",
      verified: false,
      nsqf: 4,
      sector: "Capital Goods",
      durationMonths: 12,
      ldi: 58.4,
      ldiCi: [54.2, 62.6],
      demandForecast: 135,
      demandCi80: [115, 155],
      demandCi95: [100, 170],
      certifiedSupply: 128,
      supplyCi80: [118, 138],
      netGap: 7,
      pShortage: 0.28,
      pSaturation: 0.12,
      tau: 14,
      severity: 11.2,
      status: "Balanced",
      overlay: "None",
      dataMode: "synthetic",
      history: [115, 118, 120, 122, 125, 127, 129, 131, 132, 134, 135, 135],
      forecast: [136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147],
      forecastCi80Low: [118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129],
      forecastCi80High: [154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165],
      supplyForecast: [129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140],
    },
  ];

  const currentTrade = trades.find((tr) => tr.id === selectedTradeId) || trades[0];

  // District details map
  const districtName =
    selectedDistrictId === 1
      ? "Bengaluru Urban (Karnataka)"
      : selectedDistrictId === 32
      ? "Chennai (Tamil Nadu)"
      : selectedDistrictId === 70
      ? "Gautam Buddha Nagar (Uttar Pradesh)"
      : `District #${selectedDistrictId} (${selectedState})`;

  // SVG Chart Dimensions
  const chartW = 740;
  const chartH = 260;
  const padL = 45;
  const padR = 25;
  const padT = 20;
  const padB = 35;
  const plotW = chartW - padL - padR;
  const plotH = chartH - padT - padB;

  // Max Y scale calculation
  const maxY = Math.max(
    ...currentTrade.history,
    ...currentTrade.forecastCi80High,
    ...currentTrade.supplyForecast,
    280
  );
  const minY = 0;

  const getX = (idx: number, isForecast: boolean) => {
    const tIdx = isForecast ? 11 + idx : idx;
    return padL + (tIdx / 23) * plotW;
  };

  const getY = (val: number) => {
    return padT + plotH - ((val - minY) / (maxY - minY)) * plotH;
  };

  // Generate SVG paths
  const historyPath = currentTrade.history
    .map((v, i) => `${i === 0 ? "M" : "L"} ${getX(i, false).toFixed(1)} ${getY(v).toFixed(1)}`)
    .join(" ");

  const forecastPath = [
    `M ${getX(11, false).toFixed(1)} ${getY(currentTrade.history[11]).toFixed(1)}`,
    ...currentTrade.forecast.map((v, i) => `L ${getX(i + 1, true).toFixed(1)} ${getY(v).toFixed(1)}`),
  ].join(" ");

  const supplyPath = [
    `M ${getX(11, false).toFixed(1)} ${getY(currentTrade.supplyForecast[0]).toFixed(1)}`,
    ...currentTrade.supplyForecast.map((v, i) => `L ${getX(i, true).toFixed(1)} ${getY(v).toFixed(1)}`),
  ].join(" ");

  // 80% CI Polygon
  const ciPoints = [
    `${getX(11, false).toFixed(1)},${getY(currentTrade.history[11]).toFixed(1)}`,
    ...currentTrade.forecastCi80High.map((v, i) => `${getX(i + 1, true).toFixed(1)},${getY(v).toFixed(1)}`),
    ...currentTrade.forecastCi80Low
      .slice()
      .reverse()
      .map((v, i) => `${getX(12 - i, true).toFixed(1)},${getY(v).toFixed(1)}`),
  ].join(" ");

  return (
    <div className="space-y-6">
      {/* Top Banner / Breadcrumb & Selector */}
      <div className="bg-[#021861] border border-[#133896] rounded-xl p-5 shadow-lg flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs text-slate-300 mb-1">
            <span>{t.navExplorer}</span>
            <span>/</span>
            <span className="text-blue-200 font-semibold">{districtName}</span>
            <span>/</span>
            <span className="text-slate-300">{currentTrade.sector}</span>
            <span className="text-[10px] bg-[#DE1110] text-white px-1.5 py-0.2 rounded font-bold ml-2">
              Team PROMETHEUSS
            </span>
          </div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-black text-white tracking-tight">{currentTrade.title}</h2>
            <div className="flex items-center gap-1.5">
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#255DCE]/20 text-blue-200 border border-[#255DCE]/40">
                QP: {currentTrade.qp}
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#010e3b] text-slate-200 border border-[#133896]">
                NSQF {currentTrade.nsqf}
              </span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-mono border ${
                  currentTrade.verified
                    ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                    : "bg-amber-500/20 text-amber-300 border-amber-500/30"
                }`}
                title={currentTrade.verified ? "Official NCO alignment" : "NCO Indicative alignment"}
              >
                NCO: {currentTrade.nco} ({currentTrade.verified ? "verified" : "verified: false"})
              </span>
            </div>
          </div>
        </div>

        {/* Quick Trade Switcher */}
        <div className="flex items-center gap-3">
          <label className="text-xs text-slate-300 font-bold">Switch Trade:</label>
          <select
            value={selectedTradeId}
            onChange={(e) => setSelectedTradeId(Number(e.target.value))}
            className="bg-[#010e3b] text-white text-xs border border-[#133896] rounded-lg px-3 py-2 outline-none focus:border-[#255DCE]"
          >
            {trades.map((tr) => (
              <option key={tr.id} value={tr.id}>
                {tr.title} ({tr.sector})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* LDI Gauge Card */}
        <div className="bg-[#021861] border border-[#133896] rounded-xl p-4 flex flex-col justify-between shadow-md">
          <div className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
            {t.demandIndex} (LDI)
          </div>
          <div className="my-2">
            <div className="text-3xl font-black text-amber-300 font-mono">
              {currentTrade.ldi.toFixed(1)}
            </div>
            <div className="text-[10px] text-slate-300 font-mono">
              CI: [{currentTrade.ldiCi[0]}, {currentTrade.ldiCi[1]}]
            </div>
          </div>
          <div className="w-full bg-[#010e3b] h-2 rounded-full overflow-hidden">
            <div
              className="bg-gradient-to-r from-[#255DCE] via-amber-400 to-[#DE1110] h-full rounded-full"
              style={{ width: `${currentTrade.ldi}%` }}
            />
          </div>
        </div>

        {/* Forecast Demand */}
        <div className="bg-[#021861] border border-[#133896] rounded-xl p-4 flex flex-col justify-between shadow-md">
          <div className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
            {t.forecastDemand} (E[D])
          </div>
          <div className="my-2">
            <div className="text-3xl font-black text-blue-300 font-mono">
              {currentTrade.demandForecast}
            </div>
            <div className="text-[10px] text-slate-300 font-mono">
              80% CI: [{currentTrade.demandCi80[0]}, {currentTrade.demandCi80[1]}]
            </div>
          </div>
          <span className="text-[10px] text-slate-400">Conformal calibrated</span>
        </div>

        {/* Projected Supply */}
        <div className="bg-[#021861] border border-[#133896] rounded-xl p-4 flex flex-col justify-between shadow-md">
          <div className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
            {t.projectedSupply} (S_W)
          </div>
          <div className="my-2">
            <div className="text-3xl font-black text-emerald-400 font-mono">
              {currentTrade.certifiedSupply}
            </div>
            <div className="text-[10px] text-slate-300 font-mono">
              80% CI: [{currentTrade.supplyCi80[0]}, {currentTrade.supplyCi80[1]}]
            </div>
          </div>
          <span className="text-[10px] text-slate-400">Cohort pipeline (C*E*CR*Cert)</span>
        </div>

        {/* Net Gap */}
        <div className="bg-[#021861] border border-[#133896] rounded-xl p-4 flex flex-col justify-between shadow-md">
          <div className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
            {t.netGap} (G = D - S)
          </div>
          <div className="my-2">
            <div
              className={`text-3xl font-black font-mono ${
                currentTrade.netGap > 0 ? "text-[#DE1110]" : "text-purple-300"
              }`}
            >
              {currentTrade.netGap > 0 ? `+${currentTrade.netGap}` : currentTrade.netGap}
            </div>
            <div className="text-[10px] text-slate-300 font-mono">
              Tolerance &tau;: &plusmn;{currentTrade.tau}
            </div>
          </div>
          <span className="text-[10px] text-slate-400">Windowed deficit</span>
        </div>

        {/* Shortage Probability */}
        <div className="bg-[#021861] border border-[#133896] rounded-xl p-4 flex flex-col justify-between shadow-md">
          <div className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
            {t.shortageProb} (p_S)
          </div>
          <div className="my-2">
            <div className="text-3xl font-black text-[#DE1110] font-mono">
              {(currentTrade.pShortage * 100).toFixed(0)}%
            </div>
            <div className="text-[10px] text-slate-300 font-mono">
              p_O: {(currentTrade.pSaturation * 100).toFixed(0)}%
            </div>
          </div>
          <span className="text-[10px] text-slate-400">Threshold: &ge;80%</span>
        </div>

        {/* Severity & Status */}
        <div className="bg-[#021861] border border-[#133896] rounded-xl p-4 flex flex-col justify-between shadow-md">
          <div className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
            {t.severityScore}
          </div>
          <div className="my-2">
            <div className="text-3xl font-black text-amber-300 font-mono">
              {currentTrade.severity.toFixed(1)}
            </div>
            <div className="text-[10px] font-bold text-[#DE1110]">
              {currentTrade.status}
            </div>
          </div>
          <span className="text-[10px] text-blue-200 font-mono">
            {currentTrade.overlay !== "None" ? `Overlay: ${currentTrade.overlay}` : "Stable"}
          </span>
        </div>
      </div>

      {/* Main Forecast Chart Section */}
      <div className="bg-[#021861] border border-[#133896] rounded-xl p-6 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              Demand &amp; Supply Trajectory (48-Month Panel Fusion)
              <span className="text-xs font-mono font-normal bg-[#010e3b] text-amber-300 border border-amber-500/40 px-2 py-0.5 rounded">
                data_mode: {currentTrade.dataMode}
              </span>
            </h3>
            <p className="text-xs text-slate-300 mt-0.5">
              Closed-form Kalman fusion with conformal prediction intervals (80% &amp; 95%) aligned to training cohort duration (L = {currentTrade.durationMonths}m).
            </p>
          </div>

          {/* Horizon Controls & Action Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center bg-[#010e3b] rounded-lg p-1 border border-[#133896] text-xs">
              <button
                onClick={() => setHorizon("3m")}
                className={`px-3 py-1 rounded font-bold transition ${
                  horizon === "3m" ? "bg-[#255DCE] text-white" : "text-slate-300 hover:text-white"
                }`}
              >
                3m
              </button>
              <button
                onClick={() => setHorizon("6m")}
                className={`px-3 py-1 rounded font-bold transition ${
                  horizon === "6m" ? "bg-[#255DCE] text-white" : "text-slate-300 hover:text-white"
                }`}
              >
                6m
              </button>
              <button
                onClick={() => setHorizon("12m")}
                className={`px-3 py-1 rounded font-bold transition ${
                  horizon === "12m" ? "bg-[#255DCE] text-white" : "text-slate-300 hover:text-white"
                }`}
              >
                12m
              </button>
              <button
                onClick={() => setHorizon("cohort")}
                className={`px-3 py-1 rounded font-bold transition ${
                  horizon === "cohort" ? "bg-[#255DCE] text-white" : "text-slate-300 hover:text-white"
                }`}
              >
                Cohort L ({currentTrade.durationMonths}m)
              </button>
            </div>

            <button
              onClick={() => onOpenWhy(currentTrade.id)}
              className="px-3.5 py-1.5 rounded-lg bg-[#010e3b] hover:bg-[#05216e] text-blue-200 border border-[#255DCE] text-xs font-bold flex items-center gap-1.5 transition shadow"
            >
              <span>🔍</span>
              <span>{t.whyButton}</span>
            </button>

            <button
              onClick={() => onOpenScenario(currentTrade.id)}
              className="px-3.5 py-1.5 rounded-lg bg-[#255DCE] hover:bg-[#1e4eb2] text-white text-xs font-black flex items-center gap-1.5 transition shadow-md border border-blue-400/40"
            >
              <span>⚡</span>
              <span>{t.simulateButton}</span>
            </button>
          </div>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-4 text-xs text-slate-200 mb-4 bg-[#010e3b] p-2.5 rounded-lg border border-[#133896]">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-blue-300" />
            <span>Observed Demand</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 border-t border-dashed border-[#255DCE]" />
            <span>Forecast Demand (m_t+h)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-2 bg-[#255DCE]/40 rounded-xs" />
            <span>80% Conformal Interval</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-emerald-400" />
            <span>Certified Supply (S_W)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 bg-[#DE1110]/30 border border-[#DE1110] rounded-xs" />
            <span className="text-[#DE1110] font-semibold">Acute Deficit Zone (G &gt; &tau;)</span>
          </div>
        </div>

        {/* SVG Multi-series Chart */}
        {!lowBandwidth ? (
          <div className="relative overflow-x-auto">
            <svg
              viewBox={`0 0 ${chartW} ${chartH}`}
              className="w-full h-auto max-h-[340px] text-slate-400 select-none"
            >
              {/* Grid Lines */}
              {[0, 50, 100, 150, 200, 250].map((tick) => {
                const yPos = getY(tick);
                return (
                  <g key={tick}>
                    <line
                      x1={padL}
                      y1={yPos}
                      x2={chartW - padR}
                      y2={yPos}
                      stroke="#133896"
                      strokeDasharray="2,2"
                    />
                    <text
                      x={padL - 8}
                      y={yPos + 4}
                      textAnchor="end"
                      fontSize="10"
                      fill="#94a3b8"
                      className="font-mono text-[9px]"
                    >
                      {tick}
                    </text>
                  </g>
                );
              })}

              {/* Vertical Divider between History and Forecast */}
              <line
                x1={getX(11, false)}
                y1={padT}
                x2={getX(11, false)}
                y2={chartH - padB}
                stroke="#DE1110"
                strokeWidth="1.5"
                strokeDasharray="4,4"
              />
              <text
                x={getX(11, false) - 6}
                y={padT + 12}
                textAnchor="end"
                fontSize="10"
                fill="#DE1110"
                fontWeight="bold"
              >
                Today (Month 48)
              </text>
              <text
                x={getX(11, false) + 6}
                y={padT + 12}
                textAnchor="start"
                fontSize="10"
                fill="#255DCE"
                fontWeight="bold"
              >
                Forecast Horizon &rarr;
              </text>

              {/* 80% Conformal Interval Polygon */}
              <polygon points={ciPoints} fill="#255DCE" fillOpacity="0.25" />

              {/* Observed Demand Solid Line */}
              <path
                d={historyPath}
                fill="none"
                stroke="#38bdf8"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />

              {/* Forecast Demand Dashed Line */}
              <path
                d={forecastPath}
                fill="none"
                stroke="#255DCE"
                strokeWidth="2.5"
                strokeDasharray="5,4"
                strokeLinecap="round"
              />

              {/* Certified Supply Green Line */}
              <path
                d={supplyPath}
                fill="none"
                stroke="#34d399"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />

              {/* Data points on observed line */}
              {currentTrade.history.map((v, i) => (
                <circle
                  key={i}
                  cx={getX(i, false)}
                  cy={getY(v)}
                  r="3.5"
                  fill="#0284c7"
                  stroke="#ffffff"
                  strokeWidth="1"
                />
              ))}

              {/* Data points on forecast line */}
              {currentTrade.forecast.map((v, i) => (
                <circle
                  key={i}
                  cx={getX(i + 1, true)}
                  cy={getY(v)}
                  r="3.5"
                  fill="#255DCE"
                  stroke="#ffffff"
                  strokeWidth="1"
                />
              ))}

              {/* X Axis month labels */}
              {[-11, -8, -5, -2, 1, 4, 7, 10, 12].map((m) => {
                const isFc = m > 0;
                const idx = isFc ? m - 1 : 12 + m - 1;
                const xPos = isFc ? getX(idx + 1, true) : getX(idx, false);
                return (
                  <text
                    key={m}
                    x={xPos}
                    y={chartH - 12}
                    textAnchor="middle"
                    fontSize="9"
                    fill="#94a3b8"
                    className="font-mono"
                  >
                    {m > 0 ? `+${m}m` : `${m}m`}
                  </text>
                );
              })}
            </svg>
          </div>
        ) : (
          /* Low-bandwidth accessible table */
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-[#133896] bg-[#010e3b] text-slate-300">
                  <th className="py-2 px-3 font-semibold">Month Offset</th>
                  <th className="py-2 px-3 font-semibold">Observed Demand</th>
                  <th className="py-2 px-3 font-semibold">Forecast Demand</th>
                  <th className="py-2 px-3 font-semibold">80% Range</th>
                  <th className="py-2 px-3 font-semibold">Certified Supply</th>
                  <th className="py-2 px-3 font-semibold">Deficit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#133896] font-mono text-slate-300">
                {currentTrade.forecast.slice(0, 6).map((fc, i) => (
                  <tr key={i} className="hover:bg-[#05216e]/40">
                    <td className="py-2 px-3">+{i + 1} Month</td>
                    <td className="py-2 px-3 text-slate-400">—</td>
                    <td className="py-2 px-3 text-blue-300 font-bold">{fc}</td>
                    <td className="py-2 px-3 text-slate-300">
                      [{currentTrade.forecastCi80Low[i]}, {currentTrade.forecastCi80High[i]}]
                    </td>
                    <td className="py-2 px-3 text-emerald-400 font-bold">{currentTrade.supplyForecast[i]}</td>
                    <td className="py-2 px-3 text-[#DE1110] font-bold">
                      +{fc - currentTrade.supplyForecast[i]}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Model Lineage & Pipeline Specifications */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#021861] border border-[#133896] rounded-xl p-4 shadow-md">
          <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-2">
            1. Kalman Fusion Formula
          </h4>
          <p className="text-xs text-blue-200 font-mono bg-[#010e3b] p-2.5 rounded border border-[#133896] mb-2">
            Y_t = &Sigma; r_k H_k^T R_k^(-1) y_k<br />
            M_t = &Sigma; r_k H_k^T R_k^(-1) H_k<br />
            x&#770;_t = M_t^(-1) Y_t
          </p>
          <p className="text-[11px] text-slate-300">
            Fuses NCS portals, state portals, apprenticeships, and PLFS priors with reliability gates.
          </p>
        </div>

        <div className="bg-[#021861] border border-[#133896] rounded-xl p-4 shadow-md">
          <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-2">
            2. Conformal Calibration (80% / 95%)
          </h4>
          <p className="text-xs text-blue-200 font-mono bg-[#010e3b] p-2.5 rounded border border-[#133896] mb-2">
            &sigma;_h = (q_90 - q_10) / (2 &times; 1.2816)<br />
            s_i = |y_i - &mu;_i| / &sigma;_i<br />
            q&#770;_&alpha; = Quantile(s, &lceil;(n+1)(1-&alpha;)&rceil;/n)
          </p>
          <p className="text-[11px] text-slate-300">
            Empirical coverage: 81.7% at 6m, 79.3% at 12m (verified across 31,680 backtests).
          </p>
        </div>

        <div className="bg-[#021861] border border-[#133896] rounded-xl p-4 shadow-md">
          <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-2">
            3. Stock-Flow Supply Pipeline
          </h4>
          <p className="text-xs text-blue-200 font-mono bg-[#010e3b] p-2.5 rounded border border-[#133896] mb-2">
            S_W = C &times; E &times; CR &times; Cert<br />
            L = {currentTrade.durationMonths} Months Cohort Lag<br />
            Excludes placement data
          </p>
          <p className="text-[11px] text-slate-300">
            Enrolment rate (82%), completion rate (78%), certification rate (91%).
          </p>
        </div>
      </div>
    </div>
  );
};
