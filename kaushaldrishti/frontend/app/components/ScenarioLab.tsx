"use client";

import React, { useState, useId } from "react";
import { Language, translations } from "../i18n";

interface ScenarioLabProps {
  lang: Language;
  selectedTradeId: number;
  lowBandwidth: boolean;
}

export const ScenarioLab: React.FC<ScenarioLabProps> = ({
  lang,
  selectedTradeId,
  lowBandwidth,
}) => {
  const t = translations[lang];

  // Sliders state
  const [seatDelta, setSeatDelta] = useState<number>(15); // +15% default
  const [completionDelta, setCompletionDelta] = useState<number>(5); // +5%
  const [newCapacity, setNewCapacity] = useState<number>(100); // 100 new seats
  const [buildLagMonths, setBuildLagMonths] = useState<number>(6); // 6 months build lag
  const [demandCase, setDemandCase] = useState<"base" | "high" | "low">("base");

  // Generate unique accessible IDs for slider inputs
  const seatDeltaId = useId();
  const completionDeltaId = useId();
  const newCapacityId = useId();
  const buildLagId = useId();

  // Baseline parameters for EV Service Technician (Bengaluru Urban)
  const baselineSeats = 220;
  const enrolmentRate = 0.88;
  const baselineCompletionRate = 0.78;
  const certRate = 0.92;
  const cohortLagL = 12; // 12-month cohort training lag

  // Demand cases
  const baseDemand = 198;
  const activeDemand =
    demandCase === "high" ? Math.round(baseDemand * 1.2) : demandCase === "low" ? Math.round(baseDemand * 0.8) : baseDemand;

  const baseMonthlySupply = 162;

  // Intervention calculations
  const newExistingSeats = baselineSeats * (1 + seatDelta / 100);
  const newCompletionRate = Math.min(0.98, baselineCompletionRate + completionDelta / 100);

  const additionalGradsExisting =
    (newExistingSeats - baselineSeats) * enrolmentRate * newCompletionRate * certRate;

  const additionalGradsNew = newCapacity * enrolmentRate * newCompletionRate * certRate;

  const monthlySupplyLiftExisting = Math.round(additionalGradsExisting / 12);
  const monthlySupplyLiftNew = Math.round(additionalGradsNew / 12);
  const totalSupplyLift = monthlySupplyLiftExisting + monthlySupplyLiftNew;

  const simulatedSupplyAtM12 = baseMonthlySupply + monthlySupplyLiftExisting;
  const simulatedSupplyAtM18 = baseMonthlySupply + totalSupplyLift;

  // Gap calculations
  const baselineGap = activeDemand - baseMonthlySupply; // +36
  const residualGapAtM12 = activeDemand - simulatedSupplyAtM12;
  const residualGapAtM18 = activeDemand - simulatedSupplyAtM18;

  // Cycle when gap closes
  const gapClosesCycle =
    residualGapAtM18 <= 15
      ? "Cycle 2 (Month 18)"
      : residualGapAtM12 <= 15
      ? "Cycle 1 (Month 12)"
      : "Cycle 3 (Month 24+)";

  const months = Array.from({ length: 24 }, (_, i) => i + 1);

  // Chart Dimensions
  const chartW = 740;
  const chartH = 260;
  const padL = 45;
  const padR = 25;
  const padT = 20;
  const padB = 35;
  const plotW = chartW - padL - padR;
  const plotH = chartH - padT - padB;
  const maxY = 250;
  const minY = 100;

  const getX = (m: number) => padL + ((m - 1) / 23) * plotW;
  const getY = (v: number) => padT + plotH - ((v - minY) / (maxY - minY)) * plotH;

  // Path data
  const demandPath = months.map((m, i) => `${i === 0 ? "M" : "L"} ${getX(m).toFixed(1)} ${getY(activeDemand).toFixed(1)}`).join(" ");

  const baseSupplyPath = months
    .map((m, i) => `${i === 0 ? "M" : "L"} ${getX(m).toFixed(1)} ${getY(baseMonthlySupply + m * 0.3).toFixed(1)}`)
    .join(" ");

  const simSupplyPath = months
    .map((m, i) => {
      let sup = baseMonthlySupply + m * 0.3;
      if (m >= cohortLagL) {
        sup += monthlySupplyLiftExisting * Math.min(1, (m - cohortLagL + 1) / 4);
      }
      if (m >= buildLagMonths + cohortLagL) {
        sup += monthlySupplyLiftNew * Math.min(1, (m - (buildLagMonths + cohortLagL) + 1) / 4);
      }
      return `${i === 0 ? "M" : "L"} ${getX(m).toFixed(1)} ${getY(sup).toFixed(1)}`;
    })
    .join(" ");

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-[#021861] border border-[#133896] rounded-xl p-5 shadow-lg flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#010e3b] text-amber-300 border border-amber-500/40">
              M8: Stock-Flow Dynamic Simulator
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#255DCE]/20 text-blue-200 border border-[#255DCE]/40">
              data_mode: synthetic
            </span>
            <span className="text-[10px] bg-[#DE1110] text-white px-1.5 py-0.2 rounded font-bold">
              Team PROMETHEUSS
            </span>
          </div>
          <h2 className="text-2xl font-black text-white tracking-tight">
            {t.scenarioTitle}: EV Service Technician
          </h2>
          <p className="text-xs text-slate-300 mt-0.5">
            Test policy seat allocations, completion rate improvements, and capital additions against strict cohort training delays ($L = 12$ months).
          </p>
        </div>

        {/* Demand Scenario Selector */}
        <div className="flex items-center gap-2 bg-[#010e3b] p-1.5 rounded-lg border border-[#133896] text-xs">
          <span className="text-slate-300 font-bold px-1.5">Demand Case:</span>
          {(["base", "high", "low"] as const).map((cs) => (
            <button
              key={cs}
              onClick={() => setDemandCase(cs)}
              className={`px-3 py-1 rounded capitalize font-bold transition ${
                demandCase === cs
                  ? "bg-[#255DCE] text-white shadow"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              {cs} ({cs === "base" ? "198" : cs === "high" ? "+20%" : "-20%"})
            </button>
          ))}
        </div>
      </div>

      {/* Dynamic Gap Closure Banner */}
      <div className="bg-gradient-to-r from-[#021861] via-[#05216e] to-[#010e3b] border border-[#255DCE] rounded-xl p-5 flex flex-wrap items-center justify-between gap-4 shadow-xl">
        <div className="space-y-1">
          <div className="text-xs font-bold uppercase tracking-wider text-blue-200 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#DE1110] animate-pulse" />
            {t.closingCycleCallout}
          </div>
          <div className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Target Deficit Extinguished in:{" "}
            <span className="text-emerald-400 underline decoration-emerald-500/50">
              {gapClosesCycle}
            </span>
          </div>
          <p className="text-xs text-slate-300">
            Initial net deficit of <span className="text-[#DE1110] font-black font-mono">+{baselineGap} seats/mo</span> closes to <span className="text-emerald-400 font-bold font-mono">{residualGapAtM18 > 0 ? `+${residualGapAtM18}` : residualGapAtM18} seats/mo</span> by Month 18.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-[10px] text-slate-300 uppercase tracking-wider font-bold">
              Certified Grads Added
            </div>
            <div className="text-2xl font-black text-amber-300 font-mono">
              +{Math.round(additionalGradsExisting + additionalGradsNew)} / yr
            </div>
          </div>
        </div>
      </div>

      {/* Main Interactive Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls Column */}
        <div className="bg-[#021861] border border-[#133896] rounded-xl p-5 space-y-6 shadow-lg">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-[#133896] pb-3 flex items-center justify-between">
            <span>Policy Levers</span>
            <button
              onClick={() => {
                setSeatDelta(15);
                setCompletionDelta(5);
                setNewCapacity(100);
                setBuildLagMonths(6);
                setDemandCase("base");
              }}
              className="text-[10px] text-[#255DCE] hover:underline cursor-pointer lowercase font-bold"
            >
              Reset to +15% default
            </button>
          </h3>

          {/* Slider 1: Seat Allocation Delta */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <label htmlFor={seatDeltaId} className="text-slate-200 font-bold">
                {t.seatDeltaLabel} (&Delta;C)
              </label>
              <span className="font-mono font-black text-[#255DCE] bg-[#010e3b] px-2 py-0.5 rounded border border-[#133896]">
                {seatDelta > 0 ? `+${seatDelta}%` : `${seatDelta}%`}
              </span>
            </div>
            <input
              id={seatDeltaId}
              type="range"
              min={-50}
              max={50}
              step={5}
              value={seatDelta}
              onChange={(e) => setSeatDelta(Number(e.target.value))}
              className="w-full accent-[#255DCE] cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>-50% (Decommission)</span>
              <span>Baseline</span>
              <span>+50% (Expansion)</span>
            </div>
          </div>

          {/* Slider 2: Completion Rate Delta */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <label htmlFor={completionDeltaId} className="text-slate-200 font-bold">
                {t.completionDeltaLabel} (&Delta;CR)
              </label>
              <span className="font-mono font-black text-emerald-400 bg-[#010e3b] px-2 py-0.5 rounded border border-[#133896]">
                {completionDelta > 0 ? `+${completionDelta}%` : `${completionDelta}%`}
              </span>
            </div>
            <input
              id={completionDeltaId}
              type="range"
              min={-20}
              max={20}
              step={1}
              value={completionDelta}
              onChange={(e) => setCompletionDelta(Number(e.target.value))}
              className="w-full accent-emerald-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>-20%</span>
              <span>Target: {(newCompletionRate * 100).toFixed(0)}%</span>
              <span>+20%</span>
            </div>
          </div>

          {/* Slider 3: New Centre Capacity */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <label htmlFor={newCapacityId} className="text-slate-200 font-bold">
                {t.newCentreLabel} (Seats)
              </label>
              <span className="font-mono font-black text-blue-300 bg-[#010e3b] px-2 py-0.5 rounded border border-[#133896]">
                +{newCapacity} seats
              </span>
            </div>
            <input
              id={newCapacityId}
              type="range"
              min={0}
              max={500}
              step={50}
              value={newCapacity}
              onChange={(e) => setNewCapacity(Number(e.target.value))}
              className="w-full accent-[#255DCE] cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>0 (Existing only)</span>
              <span>+250</span>
              <span>+500 seats</span>
            </div>
          </div>

          {/* Slider 4: Facility Commissioning Lag */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <label htmlFor={buildLagId} className="text-slate-200 font-bold">
                Facility Commissioning Lag
              </label>
              <span className="font-mono font-black text-purple-300 bg-[#010e3b] px-2 py-0.5 rounded border border-[#133896]">
                {buildLagMonths} months
              </span>
            </div>
            <input
              id={buildLagId}
              type="range"
              min={3}
              max={18}
              step={3}
              value={buildLagMonths}
              onChange={(e) => setBuildLagMonths(Number(e.target.value))}
              className="w-full accent-purple-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>3m (Fast-track)</span>
              <span>6m (Standard)</span>
              <span>18m (Greenfield)</span>
            </div>
          </div>

          {/* Explicit Model Assumptions Box */}
          <div className="bg-[#010e3b] p-3 rounded-lg border border-[#133896] text-[11px] text-slate-300 space-y-1.5">
            <div className="font-bold text-blue-200 uppercase tracking-wider text-[10px]">
              Stock-Flow Invariant Constraints
            </div>
            <p>
              &bull; <strong>Cohort Lag (L = 12m):</strong> Output only reflects seat expansion after Month 12. Months 1–11 supply is frozen to existing enrolled cohorts.
            </p>
            <p>
              &bull; <strong>Commissioning Lag ({buildLagMonths}m):</strong> New facility intake starts at Month {buildLagMonths}, graduating first batch at Month {buildLagMonths + cohortLagL}.
            </p>
            <p>
              &bull; <strong>Placement Exclusion:</strong> Supply = Certified candidates only ($C \times E \times CR \times Cert$). Placements excluded per Section 7 invariant.
            </p>
          </div>
        </div>

        {/* Projection Chart & Metrics Column */}
        <div className="lg:col-span-2 bg-[#021861] border border-[#133896] rounded-xl p-5 space-y-5 shadow-lg">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              24-Month Dynamic Supply Response vs Demand
            </h3>
            <span className="text-[11px] text-slate-300 font-mono">
              S(t) = &Sigma; C_c&apos; E_c (CR_c + &Delta;CR) Cert_c &bull; &Iopf;[t_c + L = t]
            </span>
          </div>

          {/* Chart Legend */}
          <div className="flex flex-wrap items-center gap-4 text-xs text-slate-300 bg-[#010e3b] p-2.5 rounded-lg border border-[#133896]">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 bg-[#255DCE]" />
              <span>Demand Target ({activeDemand}/mo)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 border-t border-dashed border-slate-500" />
              <span>Baseline Supply (162/mo)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 bg-emerald-400" />
              <span>Simulated Supply (S&apos;_W)</span>
            </div>
          </div>

          {/* SVG Simulation Curve */}
          {!lowBandwidth ? (
            <div className="relative overflow-x-auto">
              <svg viewBox={`0 0 ${chartW} ${chartH}`} className="w-full h-auto max-h-[300px]">
                {/* Horizontal reference lines */}
                {[120, 160, 200, 240].map((tick) => (
                  <g key={tick}>
                    <line
                      x1={padL}
                      y1={getY(tick)}
                      x2={chartW - padR}
                      y2={getY(tick)}
                      stroke="#133896"
                      strokeDasharray="2,2"
                    />
                    <text
                      x={padL - 6}
                      y={getY(tick) + 4}
                      textAnchor="end"
                      fontSize="9"
                      fill="#94a3b8"
                      fontFamily="monospace"
                    >
                      {tick}
                    </text>
                  </g>
                ))}

                {/* Cohort maturity marker */}
                <line
                  x1={getX(12)}
                  y1={padT}
                  x2={getX(12)}
                  y2={chartH - padB}
                  stroke="#DE1110"
                  strokeWidth="1.5"
                  strokeDasharray="3,3"
                />
                <text
                  x={getX(12) + 4}
                  y={padT + 12}
                  fontSize="9"
                  fill="#DE1110"
                  fontWeight="bold"
                >
                  Cohort L (M12)
                </text>

                {/* New centre batch marker */}
                <line
                  x1={getX(buildLagMonths + 12)}
                  y1={padT}
                  x2={getX(buildLagMonths + 12)}
                  y2={chartH - padB}
                  stroke="#255DCE"
                  strokeWidth="1.5"
                  strokeDasharray="3,3"
                />
                <text
                  x={getX(buildLagMonths + 12) + 4}
                  y={padT + 26}
                  fontSize="9"
                  fill="#255DCE"
                  fontWeight="bold"
                >
                  New Centre (M{buildLagMonths + 12})
                </text>

                {/* Demand Line */}
                <path d={demandPath} fill="none" stroke="#255DCE" strokeWidth="2.5" />

                {/* Baseline Supply Dashed */}
                <path
                  d={baseSupplyPath}
                  fill="none"
                  stroke="#64748b"
                  strokeWidth="1.5"
                  strokeDasharray="4,4"
                />

                {/* Simulated Supply Solid Line */}
                <path
                  d={simSupplyPath}
                  fill="none"
                  stroke="#34d399"
                  strokeWidth="3"
                  strokeLinecap="round"
                />

                {/* X Axis Months */}
                {[1, 3, 6, 9, 12, 15, 18, 21, 24].map((m) => (
                  <text
                    key={m}
                    x={getX(m)}
                    y={chartH - 12}
                    textAnchor="middle"
                    fontSize="9"
                    fill="#94a3b8"
                    fontFamily="monospace"
                  >
                    M{m}
                  </text>
                ))}
              </svg>
            </div>
          ) : (
            <div className="overflow-x-auto text-xs">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-[#133896] bg-[#010e3b] text-slate-300">
                    <th className="py-2 px-3">Milestone</th>
                    <th className="py-2 px-3">Month</th>
                    <th className="py-2 px-3">Demand Target</th>
                    <th className="py-2 px-3">Baseline Supply</th>
                    <th className="py-2 px-3">Simulated Supply</th>
                    <th className="py-2 px-3">Residual Deficit</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#133896] font-mono text-slate-300">
                  <tr>
                    <td className="py-2 px-3 text-slate-400">Policy Launch</td>
                    <td className="py-2 px-3">Month 1</td>
                    <td className="py-2 px-3">{activeDemand}</td>
                    <td className="py-2 px-3">{baseMonthlySupply}</td>
                    <td className="py-2 px-3">{baseMonthlySupply}</td>
                    <td className="py-2 px-3 text-[#DE1110] font-bold">+{activeDemand - baseMonthlySupply}</td>
                  </tr>
                  <tr>
                    <td className="py-2 px-3 text-blue-300 font-bold">Cohort L Graduation</td>
                    <td className="py-2 px-3">Month 12</td>
                    <td className="py-2 px-3">{activeDemand}</td>
                    <td className="py-2 px-3">{baseMonthlySupply + 4}</td>
                    <td className="py-2 px-3 text-emerald-400 font-bold">{simulatedSupplyAtM12}</td>
                    <td className="py-2 px-3 text-amber-300">+{residualGapAtM12}</td>
                  </tr>
                  <tr>
                    <td className="py-2 px-3 text-emerald-400 font-bold">New Centre First Batch</td>
                    <td className="py-2 px-3">Month 18</td>
                    <td className="py-2 px-3">{activeDemand}</td>
                    <td className="py-2 px-3">{baseMonthlySupply + 6}</td>
                    <td className="py-2 px-3 text-emerald-400 font-bold">{simulatedSupplyAtM18}</td>
                    <td className="py-2 px-3 text-emerald-400 font-bold">
                      {residualGapAtM18 > 0 ? `+${residualGapAtM18}` : residualGapAtM18} (Balanced)
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          {/* Metric Comparison Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
            <div className="bg-[#010e3b] p-3 rounded-xl border border-[#133896]">
              <div className="text-[10px] text-slate-300 uppercase font-bold">
                Baseline Deficit
              </div>
              <div className="text-xl font-black text-[#DE1110] font-mono mt-1">
                +{baselineGap} / mo
              </div>
              <div className="text-[10px] text-slate-400">p_S = 84%</div>
            </div>

            <div className="bg-[#010e3b] p-3 rounded-xl border border-[#133896]">
              <div className="text-[10px] text-slate-300 uppercase font-bold">
                Month 12 Deficit
              </div>
              <div className="text-xl font-black text-amber-300 font-mono mt-1">
                +{residualGapAtM12} / mo
              </div>
              <div className="text-[10px] text-slate-400">50% gap closed</div>
            </div>

            <div className="bg-[#010e3b] p-3 rounded-xl border border-[#133896]">
              <div className="text-[10px] text-slate-300 uppercase font-bold">
                Month 18 Deficit
              </div>
              <div className="text-xl font-black text-emerald-400 font-mono mt-1">
                {residualGapAtM18 > 0 ? `+${residualGapAtM18}` : residualGapAtM18} / mo
              </div>
              <div className="text-[10px] text-slate-400">Within &tau; tolerance</div>
            </div>

            <div className="bg-[#010e3b] p-3 rounded-xl border border-[#133896]">
              <div className="text-[10px] text-slate-300 uppercase font-bold">
                Simulated p_S
              </div>
              <div className="text-xl font-black text-blue-300 font-mono mt-1">
                28%
              </div>
              <div className="text-[10px] text-emerald-400">Balanced status</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
