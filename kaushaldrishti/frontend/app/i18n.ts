/**
 * Multilingual Translations for KaushalDrishti Dashboard.
 * Supports English (en), Hindi (hi), Kannada (kn), and Tamil (ta).
 * Pre-translated canonical glossary terms aligned with glossary.csv.
 */

export type Language = "en" | "hi" | "kn" | "ta";

export interface Translations {
  appTitle: string;
  ministryName: string;
  subTitle: string;
  navNational: string;
  navExplorer: string;
  navForecast: string;
  navAlerts: string;
  navScenario: string;
  navMethodology: string;
  printBrief: string;
  lowBandwidth: string;
  standardMode: string;
  textSize: string;
  
  // KPI Titles
  kpiAcuteShortage: string;
  kpiEmergingShortage: string;
  kpiApproachingSaturation: string;
  kpiSaturated: string;
  kpiRapidGrowth: string;
  kpiReliability: string;
  kpiMonitoredDistricts: string;
  
  // Badges & Labels
  badgeLive: string;
  badgeSynthetic: string;
  badgeHighConfidence: string;
  badgeMediumConfidence: string;
  badgeLowConfidence: string;
  whyButton: string;
  simulateButton: string;
  forecastButton: string;
  exportCsv: string;
  
  // Flags
  flagAcuteShortage: string;
  flagEmergingShortage: string;
  flagApproachingSaturation: string;
  flagSaturated: string;
  flagStable: string;
  overlayRapidGrowth: string;
  overlayVolatile: string;
  
  // Metrics
  demandIndex: string;
  forecastDemand: string;
  projectedSupply: string;
  netGap: string;
  shortageProb: string;
  severityScore: string;
  status: string;
  
  // Scenario Lab
  scenarioTitle: string;
  seatDeltaLabel: string;
  completionDeltaLabel: string;
  newCentreLabel: string;
  demandCaseLabel: string;
  closingCycleCallout: string;
  graduatesAdded: string;
  simulatedSupply: string;
  baselineSupply: string;
  interventionGap: string;
  baselineGap: string;
}

export const translations: Record<Language, Translations> = {
  en: {
    appTitle: "KaushalDrishti",
    ministryName: "Ministry of Skill Development & Entrepreneurship",
    subTitle: "Labour Market Intelligence System (LMIS)",
    navNational: "National Overview",
    navExplorer: "State & District Explorer",
    navForecast: "Forecast Centre",
    navAlerts: "Early Warning Centre",
    navScenario: "Policy Scenario Lab",
    navMethodology: "Methodology & Validation",
    printBrief: "Print District Brief",
    lowBandwidth: "Low-Bandwidth Mode",
    standardMode: "Standard Mode",
    textSize: "Text Size",
    
    kpiAcuteShortage: "Acute Shortages",
    kpiEmergingShortage: "Emerging Shortages",
    kpiApproachingSaturation: "Approaching Saturation",
    kpiSaturated: "Saturated Trades",
    kpiRapidGrowth: "Rapid Growth Overlays",
    kpiReliability: "Source Reliability Score",
    kpiMonitoredDistricts: "Monitored Pilot Districts",
    
    badgeLive: "Live Feed",
    badgeSynthetic: "Synthetic Demonstration (Honest Labelling)",
    badgeHighConfidence: "High Confidence",
    badgeMediumConfidence: "Medium Confidence",
    badgeLowConfidence: "Low Confidence",
    whyButton: "Why? (Attribution)",
    simulateButton: "Simulate Policy",
    forecastButton: "View Forecast",
    exportCsv: "Export CSV",
    
    flagAcuteShortage: "Acute Shortage",
    flagEmergingShortage: "Emerging Shortage",
    flagApproachingSaturation: "Approaching Saturation",
    flagSaturated: "Saturated",
    flagStable: "Stable",
    overlayRapidGrowth: "Rapid Growth",
    overlayVolatile: "Volatile",
    
    demandIndex: "Labour Demand Index (LDI)",
    forecastDemand: "Forecast Demand",
    projectedSupply: "Projected Supply",
    netGap: "Projected Net Gap",
    shortageProb: "Shortage Probability P(S)",
    severityScore: "Severity Score (0-100)",
    status: "Balance Status",
    
    scenarioTitle: "Stock-Flow Policy Simulator (Pipeline Delays)",
    seatDeltaLabel: "Seat Allocation Adjustment (%)",
    completionDeltaLabel: "Completion Rate Shift (pp)",
    newCentreLabel: "New Centre Capacity (seats)",
    demandCaseLabel: "Macro Demand Scenario",
    closingCycleCallout: "GAP CLOSES IN CYCLE",
    graduatesAdded: "Net Additional Certified Graduates",
    simulatedSupply: "Intervention Supply Path",
    baselineSupply: "Baseline Supply Path",
    interventionGap: "Intervention Net Gap",
    baselineGap: "Baseline Net Gap",
  },
  
  hi: {
    appTitle: "कौशल दृष्टि",
    ministryName: "कौशल विकास एवं उद्यमशीलता मंत्रालय",
    subTitle: "श्रम बाजार आसूचना प्रणाली (LMIS)",
    navNational: "राष्ट्रीय अवलोकन",
    navExplorer: "राज्य एवं जिला अन्वेषक",
    navForecast: "पूर्वानुमान केंद्र",
    navAlerts: "पूर्व चेतावनी केंद्र",
    navScenario: "नीति परिदृश्य प्रयोगशाला",
    navMethodology: "कार्यप्रणाली एवं सत्यापन",
    printBrief: "जिला संक्षिप्त विवरण प्रिंट करें",
    lowBandwidth: "कम बैंडविड्थ मोड",
    standardMode: "मानक मोड",
    textSize: "पाठ का आकार",
    
    kpiAcuteShortage: "गंभीर कमियां",
    kpiEmergingShortage: "उभरती कमियां",
    kpiApproachingSaturation: "संतृप्ति के निकट",
    kpiSaturated: "संतृप्त व्यवसाय",
    kpiRapidGrowth: "तीव्र वृद्धि ओवरले",
    kpiReliability: "स्रोत विश्वसनीयता स्कोर",
    kpiMonitoredDistricts: "निगरानी वाले पायलट जिले",
    
    badgeLive: "लाइव डेटा",
    badgeSynthetic: "सिंथेटिक (प्रदर्शनात्मक - ईमानदार लेबलिंग)",
    badgeHighConfidence: "उच्च विश्वसनीयता",
    badgeMediumConfidence: "मध्यम विश्वसनीयता",
    badgeLowConfidence: "निम्न विश्वसनीयता",
    whyButton: "क्यों? (स्रोत योगदान)",
    simulateButton: "नीति अनुकरण",
    forecastButton: "पूर्वानुमान देखें",
    exportCsv: "CSV निर्यात करें",
    
    flagAcuteShortage: "गंभीर कमी",
    flagEmergingShortage: "उभरती कमी",
    flagApproachingSaturation: "संतृप्ति के निकट",
    flagSaturated: "संतृप्त",
    flagStable: "स्थिर",
    overlayRapidGrowth: "तीव्र वृद्धि",
    overlayVolatile: "अस्थिर",
    
    demandIndex: "श्रम मांग सूचकांक (LDI)",
    forecastDemand: "अनुमानित मांग",
    projectedSupply: "अनुमानित आपूर्ति",
    netGap: "अनुमानित अंतर (गैप)",
    shortageProb: "कमी की संभावना P(S)",
    severityScore: "गंभीरता स्कोर (0-100)",
    status: "संतुलन स्थिति",
    
    scenarioTitle: "स्टॉक-फ्लो नीति सिम्युलेटर (पाइपलाइन विलंब)",
    seatDeltaLabel: "सीट आवंटन परिवर्तन (%)",
    completionDeltaLabel: "पूर्णता दर परिवर्तन (pp)",
    newCentreLabel: "नए केंद्र की क्षमता (सीटें)",
    demandCaseLabel: "मांग परिदृश्य",
    closingCycleCallout: "अंतर समाप्त होने का चक्र",
    graduatesAdded: "अतिरिक्त प्रमाणित स्नातक",
    simulatedSupply: "हस्तक्षेप आपूर्ति पथ",
    baselineSupply: "आधारभूत आपूर्ति पथ",
    interventionGap: "हस्तक्षेप पश्चात अंतर",
    baselineGap: "आधारभूत अंतर",
  },

  kn: {
    appTitle: "ಕೌಶಲ ದೃಷ್ಟಿ",
    ministryName: "ಕೌಶಲ್ಯ ಅಭಿವೃದ್ಧಿ ಮತ್ತು ಉದ್ಯಮಶೀಲತೆ ಸಚಿವಾಲಯ",
    subTitle: "ಕಾರ್ಮಿಕ ಮಾರುಕಟ್ಟೆ ಗುಪ್ತಚರ ವ್ಯವಸ್ಥೆ (LMIS)",
    navNational: "ರಾಷ್ಟ್ರೀಯ ಅವಲೋಕನ",
    navExplorer: "ರಾಜ್ಯ ಮತ್ತು ಜಿಲ್ಲಾ ಅನ್ವೇಷಕ",
    navForecast: "ಮುನ್ಸೂಚನಾ ಕೇಂದ್ರ",
    navAlerts: "ಮುನ್ನೆಚ್ಚರಿಕೆ ಕೇಂದ್ರ",
    navScenario: "ನೀತಿ ಸನ್ನಿವೇಶ ಪ್ರಯೋಗಾಲಯ",
    navMethodology: "ವಿಧಾನ ಮತ್ತು ಮೌಲ್ಯೀಕರಣ",
    printBrief: "ಜಿಲ್ಲಾ ವರದಿ ಮುದ್ರಿಸಿ",
    lowBandwidth: "ಕಡಿಮೆ ಬ್ಯಾಂಡ್‌ವಿಡ್ತ್ ಮೋಡ್",
    standardMode: "ಪ್ರಮಾಣಿತ ಮೋಡ್",
    textSize: "ಪಠ್ಯದ ಗಾತ್ರ",
    
    kpiAcuteShortage: "ತೀವ್ರ ಕೊರತೆಗಳು",
    kpiEmergingShortage: "ಹೊರಹೊಮ್ಮುತ್ತಿರುವ ಕೊರತೆಗಳು",
    kpiApproachingSaturation: "ಸಂಪೃಕ್ತತೆಯ ಸಮೀಪಿಸುತ್ತಿದೆ",
    kpiSaturated: "ಸಂಪೃಕ್ತ ವೃತ್ತಿಗಳು",
    kpiRapidGrowth: "ವೇಗದ ಬೆಳವಣಿಗೆ",
    kpiReliability: "ಮೂಲ ವಿಶ್ವಾಸಾರ್ಹತೆ ಸ್ಕೋರ್",
    kpiMonitoredDistricts: "ಪೈಲಟ್ ಜಿಲ್ಲೆಗಳು",
    
    badgeLive: "ಲೈವ್ ಫೀಡ್",
    badgeSynthetic: "ಕೃತಕ ಮಾದರಿ (ಪ್ರಾಮಾಣಿಕ ಲೇಬಲ್)",
    badgeHighConfidence: "ಹೆಚ್ಚಿನ ವಿಶ್ವಾಸಾರ್ಹತೆ",
    badgeMediumConfidence: "ಮಧ್ಯಮ ವಿಶ್ವಾಸಾರ್ಹತೆ",
    badgeLowConfidence: "ಕಡಿಮೆ ವಿಶ್ವಾಸಾರ್ಹತೆ",
    whyButton: "ಏಕೆ? (ಮೂಲ ಕೊಡುಗೆ)",
    simulateButton: "ನೀತಿ ಸಿಮ್ಯುಲೇಶನ್",
    forecastButton: "ಮುನ್ಸೂಚನೆ ವೀಕ್ಷಿಸಿ",
    exportCsv: "CSV ರಫ್ತು ಮಾಡಿ",
    
    flagAcuteShortage: "ತೀವ್ರ ಕೊರತೆ",
    flagEmergingShortage: "ಹೊರಹೊಮ್ಮುತ್ತಿರುವ ಕೊರತೆ",
    flagApproachingSaturation: "ಸಂಪೃಕ್ತತೆಯ ಸಮೀಪಿಸುತ್ತಿದೆ",
    flagSaturated: "ಸಂಪೃಕ್ತವಾಗಿದೆ",
    flagStable: "ಸ್ಥಿರ",
    overlayRapidGrowth: "ವೇಗದ ಬೆಳವಣಿಗೆ",
    overlayVolatile: "ಚಂಚಲ",
    
    demandIndex: "ಕಾರ್ಮಿಕ ಬೇಡಿಕೆ ಸೂಚ್ಯಂಕ (LDI)",
    forecastDemand: "ಮುನ್ಸೂಚಿತ ಬೇಡಿಕೆ",
    projectedSupply: "ಯೋಜಿತ ಪೂರೈಕೆ",
    netGap: "ಅಂದಾಜು ಅಂತರ",
    shortageProb: "ಕೊರತೆಯ ಸಂಭವನೀಯತೆ P(S)",
    severityScore: "ತೀವ್ರತೆಯ ಸ್ಕೋರ್ (0-100)",
    status: "ಸ್ಥಿತಿ",
    
    scenarioTitle: "ನೀತಿ ಸನ್ನಿವೇಶ ಸಿಮ್ಯುಲೇಟರ್ (ಪೈಪ್‌ಲೈನ್ ವಿಳಂಬ)",
    seatDeltaLabel: "ಸೀಟು ಹಂಚಿಕೆ ಬದಲಾವಣೆ (%)",
    completionDeltaLabel: "ಪೂರ್ಣಗೊಳಿಸುವಿಕೆ ದರ ಬದಲಾವಣೆ (pp)",
    newCentreLabel: "ಹೊಸ ಕೇಂದ್ರದ ಸಾಮರ್ಥ್ಯ (ಸೀಟುಗಳು)",
    demandCaseLabel: "ಬೇಡಿಕೆಯ ಸನ್ನಿವೇಶ",
    closingCycleCallout: "ಅಂತರ ಮುಚ್ಚುವ ಚಕ್ರ",
    graduatesAdded: "ನಿವ್ವಳ ಹೆಚ್ಚುವರಿ ಪ್ರಮಾಣೀಕೃತ ಪದವೀಧರರು",
    simulatedSupply: "ಹಸ್ತಕ್ಷೇಪ ಪೂರೈಕೆ ಹಾದಿ",
    baselineSupply: "ಮೂಲ ಪೂರೈಕೆ ಹಾದಿ",
    interventionGap: "ಹಸ್ತಕ್ಷೇಪದ ಅಂತರ",
    baselineGap: "ಮೂಲ ಅಂತರ",
  },

  ta: {
    appTitle: "கௌசல் திருஷ்டி",
    ministryName: "திறன் மேம்பாடு மற்றும் தொழில்முனைவோர் அமைச்சகம்",
    subTitle: "தொழிலாளர் சந்தை நுண்ணறிவு அமைப்பு (LMIS)",
    navNational: "தேசிய கண்ணோட்டம்",
    navExplorer: "மாநில மற்றும் மாவட்ட ஆய்வாளர்",
    navForecast: "முன்கணிப்பு மையம்",
    navAlerts: "முன்னெச்சரிக்கை மையம்",
    navScenario: "கொள்கை காட்சி ஆய்வகம்",
    navMethodology: "முறை மற்றும் சரிபார்ப்பு",
    printBrief: "மாவட்ட அறிக்கையை அச்சிடுக",
    lowBandwidth: "குறைந்த அலைவரிசை பயன்முறை",
    standardMode: "நிலையான பயன்முறை",
    textSize: "எழுத்து அளவு",
    
    kpiAcuteShortage: "கடுமையான பற்றாக்குறைகள்",
    kpiEmergingShortage: "வளர்ந்து வரும் பற்றாக்குறைகள்",
    kpiApproachingSaturation: "செறிவூட்டலை நெருங்குகிறது",
    kpiSaturated: "செறிவூட்டப்பட்ட பணிகள்",
    kpiRapidGrowth: "வேகமான வளர்ச்சி மேலடுக்கு",
    kpiReliability: "மூல நம்பகத்தன்மை மதிப்பெண்",
    kpiMonitoredDistricts: "கண்காணிக்கப்படும் மாவட்டங்கள்",
    
    badgeLive: "நேரலை தரவு",
    badgeSynthetic: "செயற்கை மாதிரி (நேர்மையான பெயரிடல்)",
    badgeHighConfidence: "அதிக நம்பிக்கை",
    badgeMediumConfidence: "நடுத்தர நம்பிக்கை",
    badgeLowConfidence: "குறைந்த நம்பிக்கை",
    whyButton: "ஏன்? (மூல பங்களிப்பு)",
    simulateButton: "கொள்கை உருவகப்படுத்துதல்",
    forecastButton: "முன்கணிப்பைக் காண்க",
    exportCsv: "CSV ஏற்றுமதி செய்",
    
    flagAcuteShortage: "கடுமையான பற்றாக்குறை",
    flagEmergingShortage: "வளர்ந்து வரும் பற்றாக்குறை",
    flagApproachingSaturation: "செறிவூட்டலை நெருங்குகிறது",
    flagSaturated: "செறிவூட்டப்பட்டது",
    flagStable: "நிலையான",
    overlayRapidGrowth: "வேகமான வளர்ச்சி",
    overlayVolatile: "நிலையற்ற",
    
    demandIndex: "தொழிலாளர் தேவை குறியீடு (LDI)",
    forecastDemand: "எதிர்பார்க்கப்படும் தேவை",
    projectedSupply: "திட்டமிடப்பட்ட விநியோகம்",
    netGap: "திட்டமிடப்பட்ட இடைவெளி",
    shortageProb: "பற்றாக்குறை நிகழ்தகவு P(S)",
    severityScore: "தீவிர மதிப்பெண் (0-100)",
    status: "சமநிலை நிலை",
    
    scenarioTitle: "கொள்கை உருவகப்படுத்துதல் ஆய்வகம்",
    seatDeltaLabel: "இட ஒதுக்கீடு மாற்றம் (%)",
    completionDeltaLabel: "நிறைவு விகித மாற்றம் (pp)",
    newCentreLabel: "புதிய மைய திறன் (இடங்கள்)",
    demandCaseLabel: "தேவை காட்சி",
    closingCycleCallout: "இடைவெளி மூடும் சுழற்சி",
    graduatesAdded: "கூடுதல் சான்றளிக்கப்பட்ட பட்டதாரிகள்",
    simulatedSupply: "தலையீட்டு விநியோக பாதை",
    baselineSupply: "அடிப்படை விநியோக பாதை",
    interventionGap: "தலையீட்டு இடைவெளி",
    baselineGap: "அடிப்படை இடைவெளி",
  },
};
