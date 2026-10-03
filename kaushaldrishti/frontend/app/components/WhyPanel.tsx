"use client";

import React from "react";
import { Language } from "../i18n";

interface WhyPanelProps {
  isOpen: boolean;
  onClose: () => void;
  tradeId: number;
  districtId: number;
  stateCode: string;
  lang: Language;
  onOpenScenario: (tradeId: number) => void;
}

export const WhyPanel: React.FC<WhyPanelProps> = ({
  isOpen,
  onClose,
  tradeId,
  districtId,
  stateCode,
  lang,
  onOpenScenario,
}) => {
  if (!isOpen) return null;

  // Exact attribution breakdown
  const sources = [
    { name: "National Career Service (NCS)", share: 42.1, mode: "live", count: 83, reliability: 0.95 },
    { name: "Karnataka Skill Mission (Kaushalkar)", share: 31.8, mode: "partner", count: 63, reliability: 0.90 },
    { name: "Apprenticeship Portal (NAPS)", share: 17.5, mode: "live", count: 35, reliability: 0.88 },
    { name: "PLFS & e-Shram Aggregate Prior", share: 8.6, mode: "public_aggregate", count: 17, reliability: 0.75 },
  ];

  // 6 Driver descriptors
  const drivers = [
    { code: "V", name: "Posting Volume", val: "198 / mo", note: "+18.2% vs frozen 24m baseline", status: "high" },
    { code: "G", name: "Posting Growth", val: "+3.4% MoM", note: "Top 5% sector acceleration", status: "high" },
    { code: "R", name: "Replacement Demand", val: "2.8% p.a.", note: "Standard natural churn", status: "normal" },
    { code: "P", name: "Persistence (P_persist)", val: "18 months", note: "Exceeds 2-refresh hysteresis threshold", status: "high" },
    { code: "B", name: "Employer Breadth", val: "34 firms", note: "Multi-employer corroboration (no single-firm distortion)", status: "safe" },
    { code: "I", name: "Wage / Intensity Premium", val: "₹24,500/mo", note: "+14.5% above automotive technician median", status: "high" },
  ];

  // Multilingual narratives aligned with glossary
  const narratives: Record<Language, string> = {
    en: "EV Service Technician exhibits an Acute Shortage in Bengaluru Urban. The Kalman information fusion model indicates 198 monthly demand versus 162 certified supply (deficit of +36, p_S = 84%, severity = 40.0). Primary drivers are sustained hiring expansion from commercial EV fleet depots (NCS 42.1%, State Portal 31.8%) and multi-employer breadths (34 verified hiring firms). The deficit is prolonged by the 12-month cohort training lag in existing ITIs.",
    hi: "बेंगलुरु अर्बन में ईवी सर्विस तकनीशियन की तीव्र कमी (Acute Shortage) दर्ज की गई है। कलमन सूचना संलयन मॉडल 198 मासिक मांग के मुकाबले 162 प्रमाणित आपूर्ति दिखाता है (+36 की शुद्ध कमी, कमी संभावना p_S = 84%, गंभीरता = 40.0)। मुख्य चालक वाणिज्यिक ईवी बेड़े के रखरखाव केंद्रों से निरंतर मांग (एनसीएस 42.1%, राज्य पोर्टल 31.8%) और 34 नियोक्ताओं की व्यापकता है।",
    kn: "ಬೆಂಗಳೂರು ನಗರದಲ್ಲಿ ಇವಿ ಸರ್ವಿಸ್ ಟೆಕ್ನಿಷಿಯನ್ ತೀವ್ರ ಕೊರತೆಯನ್ನು (Acute Shortage) ಪ್ರದರ್ಶಿಸುತ್ತದೆ. ಕಲ್ಮನ್ ಮಾಹಿತಿ ಸಮ್ಮಿಶ್ರಣ ಮಾದರಿಯು 198 ಮಾಸಿಕ ಬೇಡಿಕೆ ಮತ್ತು 162 ಪ್ರಮಾಣೀಕೃತ ಪೂರೈಕೆಯನ್ನು ಸೂಚಿಸುತ್ತದೆ (+36 ರ ನಿವ್ವಳ ಕೊರತೆ, p_S = 84%, ತೀವ್ರತೆ = 40.0). ವಾಣಿಜ್ಯ ಇವಿ ಫ್ಲೀಟ್ ಡಿಪೋಗಳಿಂದ ನೇಮಕಾತಿ ವಿಸ್ತರಣೆ ಮತ್ತು 34 ಪರಿಶೀಲಿಸಿದ ಸಂಸ್ಥೆಗಳ ವಿಶಾಲ ನೇಮಕಾತಿಯು ಪ್ರಮುಖ ಕಾರಣಗಳಾಗಿವೆ.",
    ta: "பெங்களூரு நகர்ப்புறத்தில் EV சேவை தொழில்நுட்ப வல்லுநர் கடுமையான பற்றாக்குறையை (Acute Shortage) காட்டுகிறது. கல்மான் தகவல் இணைவு மாதிரி 198 மாதாந்திர தேவைக்கு எதிராக 162 சான்றளிக்கப்பட்ட விநியோகத்தைக் காட்டுகிறது (+36 பற்றாக்குறை, p_S = 84%, தீவிரம் = 40.0). வணிக EV கடற்படை பராமரிப்பு நிலையங்களின் தொடர்ச்சியான தேவை மற்றும் 34 சரிபார்க்கப்பட்ட நிறுவனங்களின் பரந்த பணியமர்த்தல் ஆகியவை முக்கிய இயக்கிகளாகும்.",
  };

  const getDriverColor = (st: string) => {
    switch (st) {
      case "high":
        return "text-[#DE1110] bg-[#DE1110]/15 border-[#DE1110]/40 font-bold";
      case "safe":
        return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
      default:
        return "text-blue-300 bg-[#255DCE]/15 border-[#255DCE]/40";
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#010e3b]/85 backdrop-blur-md animate-fadeIn">
      <div className="bg-[#021861] border border-[#133896] rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl p-6 space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-[#133896] pb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-[#DE1110]/20 text-[#DE1110] border border-[#DE1110]/40">
                Acute Shortage
              </span>
              <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-[#010e3b] text-blue-200 border border-[#133896]">
                data_mode: synthetic
              </span>
              <span className="text-[10px] bg-[#DE1110] text-white px-1.5 py-0.2 rounded font-bold">
                Team PROMETHEUSS
              </span>
            </div>
            <h3 className="text-xl font-black text-white tracking-tight">
              Evidence Attribution &amp; Drivers: EV Service Technician
            </h3>
            <p className="text-xs text-slate-300 mt-0.5">
              District: Bengaluru Urban (KA) • LGD: 556 • Cell ID: KA-1-1-48
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-300 hover:text-white bg-[#010e3b] hover:bg-[#05216e] w-8 h-8 rounded-lg flex items-center justify-center text-lg font-bold border border-[#133896] transition"
          >
            &times;
          </button>
        </div>

        {/* Narrative Box */}
        <div className="bg-[#010e3b] p-4 rounded-xl border border-[#133896] space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-200 flex items-center gap-1.5">
              <span>🧠</span> Deterministic Explainability Narrative ({lang.toUpperCase()})
            </span>
            <span className="text-[10px] text-slate-400 font-mono">
              Rule 8: Exact Attribution
            </span>
          </div>
          <p className="text-sm text-slate-200 leading-relaxed font-sans">
            {narratives[lang]}
          </p>
        </div>

        {/* Information Fusion Weight Breakdown */}
        <div>
          <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">
            Source Contribution Shares (Closed-Form Kalman Information Matrix)
          </h4>
          <div className="space-y-2.5">
            {sources.map((src) => (
              <div key={src.name} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="text-white font-semibold">{src.name}</span>
                    <span className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-[#010e3b] text-slate-300 border border-[#133896]">
                      {src.mode}
                    </span>
                  </div>
                  <span className="text-blue-300 font-mono font-black">{src.share}%</span>
                </div>
                <div className="w-full bg-[#010e3b] h-2.5 rounded-full overflow-hidden flex border border-[#133896]">
                  <div
                    className="bg-[#255DCE] h-full rounded-full transition-all"
                    style={{ width: `${src.share}%` }}
                  />
                </div>
                <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                  <span>Valid Postings: {src.count}</span>
                  <span>Reliability r_k: {src.reliability.toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 6 Driver Descriptors Grid */}
        <div>
          <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">
            Driver Descriptors (V, G, R, P, B, I)
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
            {drivers.map((drv) => (
              <div
                key={drv.code}
                className="bg-[#010e3b] p-3 rounded-xl border border-[#133896] flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold text-slate-300">
                      [{drv.code}] {drv.name}
                    </span>
                  </div>
                  <div className="text-base font-black text-white font-mono my-1">
                    {drv.val}
                  </div>
                </div>
                <div className={`text-[10px] px-1.5 py-0.5 rounded border ${getDriverColor(drv.status)}`}>
                  {drv.note}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="border-t border-[#133896] pt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="text-[11px] text-slate-300 flex items-center gap-2">
            <span>Audit Trail:</span>
            <code className="text-blue-300 font-mono bg-[#010e3b] px-1.5 py-0.5 rounded border border-[#133896] text-[10px]">
              /api/v1/lineage/KA-1-1-48
            </code>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-[#010e3b] hover:bg-[#05216e] text-slate-200 border border-[#133896] text-xs font-bold transition"
            >
              Close
            </button>
            <button
              onClick={() => {
                onClose();
                onOpenScenario(tradeId);
              }}
              className="px-4 py-2 rounded-lg bg-[#255DCE] hover:bg-[#1e4eb2] text-white text-xs font-black transition flex items-center gap-1.5 shadow-md border border-blue-400/40"
            >
              <span>⚡</span>
              <span>Test in Policy Scenario Lab</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
