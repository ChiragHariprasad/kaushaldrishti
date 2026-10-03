"""
Multilingual Templated Explanations (Layer 6).
Generates deterministic, audit-proof natural language explanations in
English (en), Hindi (hi), Kannada (kn), and Tamil (ta) using pre-translated glossary terms.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class MultilingualExplainer:
    """
    Deterministic explainability engine producing bilingual/multilingual narrative briefs.
    """

    def __init__(self, glossary_csv: Optional[str] = None):
        self.glossary_csv = Path(glossary_csv) if glossary_csv else REPO_ROOT / "data" / "reference" / "glossary.csv"
        self.glossary: Dict[str, Dict[str, str]] = {}
        self._load_glossary()

    def _load_glossary(self):
        if not self.glossary_csv.exists():
            return
        df = pd.read_csv(self.glossary_csv)
        for _, row in df.iterrows():
            key = str(row["key"])
            self.glossary[key] = {
                "en": str(row.get("en", "")),
                "hi": str(row.get("hi", "")),
                "kn": str(row.get("kn", "")),
                "ta": str(row.get("ta", "")),
            }

    def term(self, key: str, lang: str = "en") -> str:
        """Retrieve pre-translated term with English fallback."""
        if key in self.glossary:
            return self.glossary[key].get(lang) or self.glossary[key].get("en", key)
        return key

    def explain_cell(
        self,
        trade_name: str,
        district_name: str,
        state_code: str,
        flag: str,
        overlays: List[str],
        gap_info: Dict[str, Any],
        confidence: str = "Medium",
        data_mode: str = "synthetic",
        drivers: Optional[Dict[str, Any]] = None,
        source_contributions: Optional[List[Dict[str, Any]]] = None,
        lang: str = "en",
    ) -> Dict[str, Any]:
        """
        Builds deterministic structured explanation in specified language.
        """
        lang = lang.lower() if lang in ["en", "hi", "kn", "ta"] else "en"
        drivers = drivers or {}
        source_contributions = source_contributions or []

        # Flag key mapping
        flag_key_map = {
            "Acute Shortage": "flag_acute_shortage",
            "Emerging Shortage": "flag_emerging_shortage",
            "Approaching Saturation": "flag_approaching_saturation",
            "Saturated": "flag_saturated",
            "Stable": "flag_stable",
        }
        flag_translated = self.term(flag_key_map.get(flag, "flag_stable"), lang)

        # Overlay mapping
        overlay_translated = [
            self.term("overlay_rapid_growth" if o == "Rapid Growth" else "overlay_volatile", lang)
            for o in overlays
        ]

        # Confidence badge
        conf_key_map = {"High": "confidence_high", "Medium": "confidence_medium", "Low": "confidence_low"}
        conf_translated = self.term(conf_key_map.get(confidence, "confidence_medium"), lang)

        # Action recommendation
        if "Shortage" in flag:
            action_translated = self.term("action_expand_training" if flag == "Acute Shortage" else "action_review_seats", lang)
        elif "Saturat" in flag:
            action_translated = self.term("action_consolidate_capacity", lang)
        else:
            action_translated = self.term("action_review_seats", lang)

        # Compose narrative
        d_mean = gap_info.get("d_mean", 0.0)
        s_mean = gap_info.get("s_mean", 0.0)
        g_mean = gap_info.get("g_mean", 0.0)
        p_shortage = gap_info.get("p_shortage", 0.0)
        p_oversupply = gap_info.get("p_oversupply", 0.0)
        severity = gap_info.get("severity", 0.0)

        if lang == "hi":
            narrative = (
                f"{district_name} ({state_code}) में {trade_name} के लिए स्थिति '{flag_translated}' के रूप में आंकी गई है "
                f"(गंभीरता: {severity}/100, {conf_translated})। "
                f"अगले 12 महीनों में अनुमानित मांग {d_mean:.0f} और अनुमानित आपूर्ति {s_mean:.0f} है, "
                f"जिससे {abs(g_mean):.0f} सीटों का {'अभाव (कमी)' if g_mean > 0 else 'अधिशेष (अतिरिक्त)'} अपेक्षित है "
                f"(कमी की संभावना: {p_shortage * 100:.1f}%)। "
                f"अनुशंसा: {action_translated}।"
            )
        elif lang == "kn":
            narrative = (
                f"{district_name} ({state_code}) ನಲ್ಲಿ {trade_name} ವೃತ್ತಿಗಾಗಿ ಸ್ಥಿತಿಯನ್ನು '{flag_translated}' ಎಂದು ಗುರುತಿಸಲಾಗಿದೆ "
                f"(ತೀವ್ರತೆ: {severity}/100, {conf_translated}). "
                f"ಮುಂದಿನ 12 ತಿಂಗಳುಗಳಲ್ಲಿ ಅಂದಾಜು ಬೇಡಿಕೆ {d_mean:.0f} ಮತ್ತು ಯೋಜಿತ ಪೂರೈಕೆ {s_mean:.0f} ಆಗಿದೆ, "
                f"ಇದರಿಂದ {abs(g_mean):.0f} ಸೀಟುಗಳ {'ಕೊರತೆ' if g_mean > 0 else 'ಹೆಚ್ಚುವರಿ'} ಉಂಟಾಗುವ ಸಾಧ್ಯತೆಯಿದೆ "
                f"(ಕೊರತೆಯ ಸಂಭವನೀಯತೆ: {p_shortage * 100:.1f}%). "
                f"ಶಿಫಾರಸು: {action_translated}."
            )
        elif lang == "ta":
            narrative = (
                f"{district_name} ({state_code}) இல் {trade_name} பணிக்கான நிலை '{flag_translated}' என கணக்கிடப்பட்டுள்ளது "
                f"(தீவிரம்: {severity}/100, {conf_translated}). "
                f"அடுத்த 12 மாதங்களில் எதிர்பார்க்கப்படும் தேவை {d_mean:.0f} மற்றும் திட்டமிடப்பட்ட விநியோகம் {s_mean:.0f} ஆகும், "
                f"இதனால் {abs(g_mean):.0f} இடங்களின் {'பற்றாக்குறை' if g_mean > 0 else 'மிகை'} எதிர்பார்க்கப்படுகிறது "
                f"(பற்றாக்குறை நிகழ்தகவு: {p_shortage * 100:.1f}%). "
                f"பரிந்துரை: {action_translated}."
            )
        else:  # English
            narrative = (
                f"In {district_name} ({state_code}), {trade_name} is classified as '{flag_translated}' "
                f"(Severity: {severity}/100, {conf_translated}). "
                f"Projected 12-month demand of {d_mean:.0f} against supply of {s_mean:.0f} results in a projected "
                f"{'shortage' if g_mean > 0 else 'surplus'} of {abs(g_mean):.0f} certified trainees "
                f"(P(Shortage) = {p_shortage * 100:.1f}%, P(Oversupply) = {p_oversupply * 100:.1f}%). "
                f"Advisory Action: {action_translated}."
            )

        return {
            "lang": lang,
            "district_name": district_name,
            "state_code": state_code,
            "trade_name": trade_name,
            "flag": flag,
            "flag_label": flag_translated,
            "overlays": overlay_translated,
            "confidence": conf_translated,
            "data_mode": data_mode,
            "severity": severity,
            "narrative": narrative,
            "suggested_action": action_translated,
            "gap_summary": {
                "d_mean": d_mean,
                "s_mean": s_mean,
                "g_mean": g_mean,
                "p_shortage": p_shortage,
                "p_oversupply": p_oversupply,
            },
            "source_contributions": source_contributions,
            "drivers": drivers,
        }
