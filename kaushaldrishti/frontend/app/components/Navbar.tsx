"use client";

import React from "react";
import { Language, translations } from "../i18n";

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  lang: Language;
  setLang: (lang: Language) => void;
  lowBandwidth: boolean;
  setLowBandwidth: (val: boolean) => void;
  onPrintBrief: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setCurrentTab,
  lang,
  setLang,
  lowBandwidth,
  setLowBandwidth,
  onPrintBrief,
}) => {
  const t = translations[lang];

  const navItems = [
    { id: "national", label: t.navNational },
    { id: "explorer", label: t.navExplorer },
    { id: "forecast", label: t.navForecast },
    { id: "alerts", label: t.navAlerts, hasAlertDot: true },
    { id: "scenario", label: t.navScenario },
    { id: "methodology", label: t.navMethodology },
  ];

  return (
    <header className="bg-[#021861] border-b border-[#133896] text-white sticky top-0 z-50 shadow-lg">
      {/* Top Ministry Banner */}
      <div className="bg-[#010e3b] px-4 py-1.5 flex flex-wrap items-center justify-between text-xs text-slate-300 border-b border-[#133896]/60">
        <div className="flex items-center gap-2">
          {/* Emblem with subtle crimson accent hint */}
          <div className="w-5 h-5 rounded-full bg-[#255DCE]/30 border border-[#255DCE] flex items-center justify-center text-[10px] font-black text-white shadow-inner">
            <span className="text-[#DE1110] font-black mr-0.5">●</span>M
          </div>
          <span className="font-semibold text-slate-200">{t.ministryName}</span>
          <span className="text-slate-500">|</span>
          <span className="text-slate-400">Government of India</span>
          <span className="text-slate-500 hidden sm:inline">|</span>
          <span className="hidden sm:inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-[#255DCE]/20 text-white border border-[#255DCE]/40">
            <span className="w-1.5 h-1.5 rounded-full bg-[#DE1110] animate-pulse" />
            Team PROMETHEUSS
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* Honest Labelling Badge */}
          <div className="flex items-center gap-1.5 bg-[#021861] text-amber-300 border border-amber-500/40 px-2 py-0.5 rounded font-mono text-[10px]">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            <span>data_mode: synthetic</span>
          </div>

          {/* Low Bandwidth Mode Toggle */}
          <button
            onClick={() => setLowBandwidth(!lowBandwidth)}
            className={`px-2 py-0.5 rounded text-[11px] font-semibold border transition-colors ${
              lowBandwidth
                ? "bg-emerald-600 text-white border-emerald-500"
                : "bg-[#05216e] text-slate-200 border-[#133896] hover:bg-[#255DCE]/30"
            }`}
            title="Toggle simplified high-density accessible data tables"
          >
            {lowBandwidth ? t.standardMode : t.lowBandwidth}
          </button>

          {/* Print District Brief */}
          <button
            onClick={onPrintBrief}
            className="px-2 py-0.5 rounded text-[11px] font-semibold bg-[#255DCE]/20 hover:bg-[#255DCE]/40 text-blue-200 border border-[#255DCE]/50 transition-colors flex items-center gap-1"
          >
            <svg className="w-3 h-3 text-[#255DCE]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            <span>{t.printBrief}</span>
          </button>

          {/* Language Switcher */}
          <div className="flex items-center gap-1 bg-[#021861] rounded p-0.5 border border-[#133896]">
            {(["en", "hi", "kn", "ta"] as Language[]).map((l) => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className={`px-1.5 py-0.5 rounded text-[11px] font-semibold transition-colors ${
                  lang === l
                    ? "bg-[#255DCE] text-white shadow-sm"
                    : "text-slate-300 hover:text-white hover:bg-[#05216e]"
                }`}
              >
                {l === "en" ? "EN" : l === "hi" ? "हिन्दी" : l === "kn" ? "ಕನ್ನಡ" : "தமிழ்"}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Nav Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-[#021861] via-[#255DCE] to-[#447ef2] border border-[#255DCE]/60 flex items-center justify-center font-black text-white shadow-md">
              <span className="tracking-tighter">KD</span>
            </div>
            <div>
              <div className="font-extrabold text-base leading-tight tracking-tight text-white flex items-center gap-2">
                <span>{t.appTitle}</span>
                <span className="text-[10px] font-mono text-blue-200 font-bold bg-[#010e3b] px-1.5 py-0.2 rounded border border-[#255DCE]/50">
                  SIH26246
                </span>
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#DE1110] bg-[#DE1110]/10 px-1.5 py-0.2 rounded border border-[#DE1110]/30 sm:hidden">
                  PROMETHEUSS
                </span>
              </div>
              <div className="text-[11px] text-slate-300 leading-tight">
                {t.subTitle}
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex space-x-1">
            {navItems.map((item) => {
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentTab(item.id)}
                  className={`relative px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                    isActive
                      ? "bg-[#255DCE] text-white shadow-md shadow-[#255DCE]/20 border border-[#447ef2]/60"
                      : "text-slate-200 hover:bg-[#05216e] hover:text-white"
                  }`}
                >
                  <span className="flex items-center gap-1.5">
                    {item.label}
                    {item.hasAlertDot && (
                      <span className="w-2 h-2 rounded-full bg-[#DE1110] animate-pulse" title="Active Acute Shortage alerts" />
                    )}
                  </span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
};
