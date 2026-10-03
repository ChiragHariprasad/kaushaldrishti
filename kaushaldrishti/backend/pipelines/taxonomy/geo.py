"""
Geography Resolver: Maps free-text location strings to canonical LGD District records.
Handles common Indian aliases (e.g., Bangalore -> Bengaluru Urban, Allahabad -> Prayagraj, Madras -> Chennai).
"""

import csv
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import rapidfuzz.fuzz as fuzz

from pipelines.taxonomy.normalizer import normalize_title


COMMON_LOCATION_ALIASES: Dict[str, str] = {
    "bangalore rural": "bengaluru rural",
    "bangalore urban": "bengaluru urban",
    "greater noida": "gautam buddha nagar",
    "hubli dharwad": "dharwad",
    "kanpur nagar": "kanpur nagar",
    "kanpur dehat": "kanpur dehat",
    "bangalore": "bengaluru urban",
    "bengaluru": "bengaluru urban",
    "mysore": "mysuru",
    "belgaum": "belagavi",
    "hubli": "dharwad",
    "mangalore": "dakshina kannada",
    "shimoga": "shivamogga",
    "bellary": "ballari",
    "gulbarga": "kalaburagi",
    "bijapur": "vijayapura",
    "davangere": "davanagere",
    "chickmagalur": "chikkamagaluru",
    "bagalkot": "bagalkote",
    "madras": "chennai",
    "trichy": "tiruchirappalli",
    "trivellore": "tiruvallur",
    "tuticorin": "thoothukudi",
    "tanjore": "thanjavur",
    "ooty": "nilgiris",
    "allahabad": "prayagraj",
    "banaras": "varanasi",
    "kashi": "varanasi",
    "faizabad": "ayodhya",
    "noida": "gautam buddha nagar",
    "kanpur": "kanpur nagar",
    "lucknow": "lucknow",
    "agra": "agra",
    "varanasi": "varanasi",
    "meerut": "meerut",
    "ghaziabad": "ghaziabad",
}


class GeoResolver:
    """
    Resolves free-text locations to LGD District records with confidence scoring.
    """

    def __init__(self, districts_file: Optional[str] = None):
        if not districts_file:
            districts_file = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "reference", "lgd_districts.csv")
            )
        self.districts: List[Dict[str, Any]] = []
        if os.path.exists(districts_file):
            with open(districts_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.districts.append({
                        "lgd_code": row["lgd_code"],
                        "district_name": row["district_name"],
                        "norm_name": normalize_title(row["district_name"]),
                        "state_code": row["state_code"],
                        "state_name": row["state_name"],
                    })

    def resolve(self, location_text: str) -> Optional[Tuple[str, str, str, float]]:
        """
        Resolves location_text to (lgd_code, district_name, state_code, confidence).
        Returns None if no candidate achieves minimum threshold.
        """
        if not location_text:
            return None

        norm_loc = normalize_title(location_text)

        # 1. Exact match with canonical district name
        for d in self.districts:
            if norm_loc == d["norm_name"]:
                return (d["lgd_code"], d["district_name"], d["state_code"], 1.0)

        # 2. Check explicit alias dictionary (longest alias first with word boundaries)
        sorted_aliases = sorted(COMMON_LOCATION_ALIASES.items(), key=lambda x: len(x[0]), reverse=True)
        for alias, target in sorted_aliases:
            if alias == norm_loc or re.search(r"\b" + re.escape(alias) + r"\b", norm_loc):
                for d in self.districts:
                    if d["norm_name"] == target:
                        return (d["lgd_code"], d["district_name"], d["state_code"], 0.95)

        # 3. Fuzzy match using Levenshtein / WRatio across all districts
        best_match = None
        best_score = 0.0

        for d in self.districts:
            score = fuzz.ratio(norm_loc, d["norm_name"]) / 100.0
            if score > best_score:
                best_score = score
                best_match = d

        if best_match and best_score >= 0.70:
            return (
                best_match["lgd_code"],
                best_match["district_name"],
                best_match["state_code"],
                round(best_score, 3),
            )

        return None
