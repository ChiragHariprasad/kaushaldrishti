"use client";

import React, { useState, useEffect } from "react";
import { Language, translations } from "./i18n";
import { Navbar } from "./components/Navbar";
import { NationalOverview } from "./components/NationalOverview";
import { DistrictExplorer } from "./components/DistrictExplorer";
import { ForecastCentre } from "./components/ForecastCentre";
import { EarlyWarningCentre } from "./components/EarlyWarningCentre";
import { ScenarioLab } from "./components/ScenarioLab";
import { MethodologyValidation } from "./components/MethodologyValidation";
import { WhyPanel } from "./components/WhyPanel";
import { DistrictBriefModal } from "./components/DistrictBriefModal";

export default function Home() {
  // Navigation & Localization
  const [currentTab, setCurrentTab] = useState<string>("national");
  const [lang, setLang] = useState<Language>("en");
  const [lowBandwidth, setLowBandwidth] = useState<boolean>(false);

  // Selected hierarchy state (Default: Golden Path -> Karnataka -> Bengaluru Urban -> EV Service Technician)
  const [selectedState, setSelectedState] = useState<string>("KA");
  const [selectedDistrictId, setSelectedDistrictId] = useState<number>(1);
  const [selectedTradeId, setSelectedTradeId] = useState<number>(1);

  // Modals
  const [isWhyOpen, setIsWhyOpen] = useState<boolean>(false);
  const [whyTradeId, setWhyTradeId] = useState<number>(1);
  const [isBriefOpen, setIsBriefOpen] = useState<boolean>(false);

  // Backend Health State
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  const t = translations[lang];
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    async function checkHealth() {
      try {
        const res = await fetch(`${apiUrl}/api/v1/health`, { method: "GET" });
        if (res.ok) {
          setBackendOnline(true);
        } else {
          setBackendOnline(false);
        }
      } catch {
        setBackendOnline(false);
      }
    }
    checkHealth();
  }, [apiUrl]);

  // Handler for cell selection from National Overview or Alerts
  const handleSelectCell = (stateCode: string, districtId: number, tradeId: number) => {
    setSelectedState(stateCode);
    setSelectedDistrictId(districtId);
    setSelectedTradeId(tradeId);
    setCurrentTab("forecast");
  };

  const handleOpenWhy = (tradeId: number) => {
    setWhyTradeId(tradeId);
    setIsWhyOpen(true);
  };

  const handleOpenScenario = (tradeId: number) => {
    setSelectedTradeId(tradeId);
    setCurrentTab("scenario");
  };

  // Golden path steps helper
  const goldenPathSteps = [
    { num: 1, label: "National Overview", tab: "national", action: () => setCurrentTab("national") },
    {
      num: 2,
      label: "Karnataka State",
      tab: "explorer",
      action: () => {
        setSelectedState("KA");
        setCurrentTab("explorer");
      },
    },
    {
      num: 3,
      label: "Bengaluru Urban",
      tab: "explorer",
      action: () => {
        setSelectedState("KA");
        setSelectedDistrictId(1);
        setCurrentTab("explorer");
      },
    },
    {
      num: 4,
      label: "EV Service Technician",
      tab: "forecast",
      action: () => {
        setSelectedState("KA");
        setSelectedDistrictId(1);
        setSelectedTradeId(1);
        setCurrentTab("forecast");
      },
    },
    {
      num: 5,
      label: 'Inspect "Why"',
      tab: "forecast",
      action: () => {
        setSelectedState("KA");
        setSelectedDistrictId(1);
        setSelectedTradeId(1);
        setCurrentTab("forecast");
        setIsWhyOpen(true);
      },
    },
    {
      num: 6,
      label: "Scenario Lab (+15% Seats)",
      tab: "scenario",
      action: () => {
        setSelectedTradeId(1);
        setCurrentTab("scenario");
      },
    },
    {
      num: 7,
      label: "Export CSV",
      tab: "export",
      action: () => {
        window.open(`${apiUrl}/api/v1/export?format=csv`, "_blank");
      },
    },
  ];

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100 font-sans antialiased selection:bg-amber-500 selection:text-slate-950">
      {/* Primary Navigation Bar */}
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        lang={lang}
        setLang={setLang}
        lowBandwidth={lowBandwidth}
        setLowBandwidth={setLowBandwidth}
        onPrintBrief={() => setIsBriefOpen(true)}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6 sm:px-6 lg:px-8 space-y-6">
        {/* Golden Path Evaluation Walkthrough Banner */}
        <div className="bg-slate-900/90 border border-amber-500/30 rounded-xl p-4 shadow-md backdrop-blur">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-2.5">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping" />
              <span className="text-xs font-bold uppercase tracking-wider text-amber-400">
                Official SIH 2026 Evaluation Golden Path
              </span>
              <span className="text-[11px] text-slate-400">
                (Click any step to jump directly to the target level)
              </span>
            </div>
            <div className="flex items-center gap-2 text-[11px]">
              <span className="text-slate-400">Backend API:</span>
              {backendOnline === true ? (
                <span className="text-emerald-400 font-mono font-medium flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  Online
                </span>
              ) : backendOnline === false ? (
                <span className="text-amber-400 font-mono font-medium flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-amber-500" />
                  Standalone Pilot Mode
                </span>
              ) : (
                <span className="text-slate-400 font-mono">Checking...</span>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-1.5 text-center text-xs">
            {goldenPathSteps.map((step) => {
              const isActive =
                currentTab === step.tab &&
                (step.num !== 4 || selectedTradeId === 1) &&
                (step.num !== 5 || isWhyOpen);

              return (
                <button
                  key={step.num}
                  onClick={step.action}
                  className={`p-2 rounded-lg border text-left transition flex flex-col justify-between ${
                    isActive
                      ? "bg-amber-500/20 border-amber-500/80 text-white font-semibold shadow"
                      : "bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-800/40"
                  }`}
                >
                  <div className="text-[10px] text-amber-400 font-mono font-bold">
                    Step {step.num}
                  </div>
                  <div className="text-[11px] mt-0.5 leading-tight">{step.label}</div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab 1: National Overview */}
        {currentTab === "national" && (
          <NationalOverview
            lang={lang}
            onSelectCell={handleSelectCell}
            onNavigateTab={setCurrentTab}
          />
        )}

        {/* Tab 2: State & District Explorer */}
        {currentTab === "explorer" && (
          <DistrictExplorer
            lang={lang}
            selectedState={selectedState}
            setSelectedState={setSelectedState}
            selectedDistrictId={selectedDistrictId}
            setSelectedDistrictId={setSelectedDistrictId}
            onSelectTrade={(tradeId) => {
              setSelectedTradeId(tradeId);
              setCurrentTab("forecast");
            }}
            onOpenWhy={handleOpenWhy}
            onOpenScenario={handleOpenScenario}
          />
        )}

        {/* Tab 3: Forecast Centre */}
        {currentTab === "forecast" && (
          <ForecastCentre
            lang={lang}
            selectedState={selectedState}
            selectedDistrictId={selectedDistrictId}
            selectedTradeId={selectedTradeId}
            setSelectedTradeId={setSelectedTradeId}
            onOpenWhy={handleOpenWhy}
            onOpenScenario={handleOpenScenario}
            lowBandwidth={lowBandwidth}
          />
        )}

        {/* Tab 4: Early Warning Centre */}
        {currentTab === "alerts" && (
          <EarlyWarningCentre
            lang={lang}
            onSelectCell={handleSelectCell}
            onOpenWhy={handleOpenWhy}
            lowBandwidth={lowBandwidth}
          />
        )}

        {/* Tab 5: Policy Scenario Lab */}
        {currentTab === "scenario" && (
          <ScenarioLab
            lang={lang}
            selectedTradeId={selectedTradeId}
            lowBandwidth={lowBandwidth}
          />
        )}

        {/* Tab 6: Methodology & Validation */}
        {currentTab === "methodology" && (
          <MethodologyValidation lang={lang} lowBandwidth={lowBandwidth} />
        )}
      </main>

      {/* Slide-in / Modal Why Attribution Panel */}
      <WhyPanel
        isOpen={isWhyOpen}
        onClose={() => setIsWhyOpen(false)}
        tradeId={whyTradeId}
        districtId={selectedDistrictId}
        stateCode={selectedState}
        lang={lang}
        onOpenScenario={handleOpenScenario}
      />

      {/* Printable District Executive Brief Modal */}
      <DistrictBriefModal
        isOpen={isBriefOpen}
        onClose={() => setIsBriefOpen(false)}
        stateCode={selectedState}
        districtId={selectedDistrictId}
        lang={lang}
      />

      {/* Footer */}
      <footer className="bg-slate-950 border-t border-slate-900 py-6 text-xs text-slate-500 mt-auto">
        <div className="max-w-7xl mx-auto px-4 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="font-semibold text-slate-400">KaushalDrishti LMIS</span>
            <span>&bull;</span>
            <span>Ministry of Skill Development &amp; Entrepreneurship (MSDE)</span>
            <span>&bull;</span>
            <span>Problem Statement SIH26246</span>
          </div>

          <div className="flex items-center gap-4 font-mono text-[11px]">
            <a
              href={`${apiUrl}/api/v1/docs`}
              target="_blank"
              rel="noreferrer"
              className="text-amber-400 hover:underline"
            >
              OpenAPI Swagger
            </a>
            <span>&bull;</span>
            <span className="text-slate-400">48-Month Panel Fusion</span>
            <span>&bull;</span>
            <span className="text-emerald-400">100% Deterministic Serving</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
