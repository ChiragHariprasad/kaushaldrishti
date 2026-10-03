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
    { id: "alerts", label: t.navAlerts },
    { id: "scenario", label: t.navScenario },
    { id: "methodology", label: t.navMethodology },
  ];

  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-50 shadow-md">
      {/* Top Ministry Banner */}
      <div className="bg-slate-950 px-4 py-1.5 flex flex-wrap items-center justify-between text-xs text-slate-400 border-b border-slate-800/60">
        <div className="flex items-center gap-2">
          {/* Emblem representation */}
          <div className="w-4 h-4 rounded-full bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-[10px] font-bold text-amber-400">
            MSDE
          </div>
          <span className="font-medium text-slate-300">{t.ministryName}</span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-400">Government of India</span>
        </div>

        <div className="flex items-center gap-3">
          {/* Honest Labelling Badge */}
          <div className="flex items-center gap-1.5 bg-amber-500/10 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded font-mono text-[10px]">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
            <span>data_mode: synthetic</span>
          </div>

          {/* Low Bandwidth Mode Toggle */}
          <button
            onClick={() => setLowBandwidth(!lowBandwidth)}
            className={`px-2 py-0.5 rounded text-[11px] font-medium border transition-colors ${
              lowBandwidth
                ? "bg-emerald-600 text-white border-emerald-500"
                : "bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700"
            }`}
            title="Toggle simplified high-density accessible data tables"
          >
            {lowBandwidth ? t.standardMode : t.lowBandwidth}
          </button>

          {/* Print District Brief */}
          <button
            onClick={onPrintBrief}
            className="px-2 py-0.5 rounded text-[11px] font-medium bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/40 transition-colors flex items-center gap-1"
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            <span>{t.printBrief}</span>
          </button>

          {/* Language Switcher */}
          <div className="flex items-center gap-1 bg-slate-800 rounded p-0.5 border border-slate-700">
            {(["en", "hi", "kn", "ta"] as Language[]).map((l) => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className={`px-1.5 py-0.5 rounded text-[11px] font-medium transition-colors ${
                  lang === l
                    ? "bg-blue-600 text-white"
                    : "text-slate-400 hover:text-white hover:bg-slate-700"
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
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center font-bold text-white shadow">
              KD
            </div>
            <div>
              <div className="font-bold text-base leading-tight tracking-tight text-white flex items-center gap-2">
                <span>{t.appTitle}</span>
                <span className="text-[10px] font-mono text-blue-400 font-normal bg-blue-950/80 px-1.5 py-0.2 rounded border border-blue-800/60">
                  SIH26246
                </span>
              </div>
              <div className="text-[11px] text-slate-400 leading-tight">
                {t.subTitle}
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex space-x-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  currentTab === item.id
                    ? "bg-blue-600 text-white shadow-sm"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white"
                }`}
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
};
