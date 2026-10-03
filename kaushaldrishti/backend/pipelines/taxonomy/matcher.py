"""
Taxonomy Matcher: Maps free-text job titles and skills to canonical Trades and NCO codes.
Combines rule-based pattern matching with fuzzy char n-gram matching and calibrated confidence.
"""

import math
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import rapidfuzz.fuzz as fuzz

from pipelines.taxonomy.normalizer import normalize_title, detect_script


DEFAULT_CONFIDENCE_THRESHOLD = 0.55


class TaxonomyMatcher:
    """
    Taxonomy matcher with rule patterns and fuzzy multi-token scoring.
    """

    def __init__(self, trades_list: Optional[List[Dict[str, Any]]] = None):
        """
        Initializes matcher with trades data.
        If trades_list is None, loads from reference CSV.
        """
        self.trades = trades_list or self._load_trades_from_csv()
        self._compiled_patterns = self._compile_trade_patterns()

    def _load_trades_from_csv(self) -> List[Dict[str, Any]]:
        import csv
        ref_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "reference", "trades_master.csv")
        )
        trades = []
        if os.path.exists(ref_path):
            with open(ref_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader, start=1):
                    aliases = [normalize_title(a) for a in row["aliases_pipe"].split("|") if a]
                    patterns = [p for p in row["patterns_pipe"].split("|") if p]
                    trades.append({
                        "id": idx,
                        "name": row["trade_name"],
                        "norm_name": normalize_title(row["trade_name"]),
                        "sector_name": row["sector_name"],
                        "nco_code": row["nco_code"],
                        "qp_code": row["qp_code"],
                        "aliases": aliases,
                        "patterns": patterns,
                    })
        return trades

    def _compile_trade_patterns(self) -> List[Tuple[int, re.Pattern]]:
        compiled = []
        for t in self.trades:
            for pat in t["patterns"]:
                try:
                    compiled.append((t["id"], re.compile(pat, re.IGNORECASE)))
                except re.error:
                    pass
        return compiled

    def match(
        self, title: str, skills: Optional[str] = None
    ) -> List[Tuple[str, str, int, float]]:
        """
        Matches title to (nco_code, qp_code, trade_id, confidence).
        Returns top matches sorted descending by confidence.
        """
        if not title:
            return []

        norm_input = normalize_title(title)
        script = detect_script(title)

        scored_matches = []

        for trade in self.trades:
            # 1. Rule / Pattern match
            rule_matched = False
            for pat_id, pat_regex in self._compiled_patterns:
                if pat_id == trade["id"] and (
                    pat_regex.search(norm_input)
                    or (skills and pat_regex.search(skills))
                ):
                    rule_matched = True
                    break

            # 2. Fuzzy Token Similarity
            name_score = fuzz.token_set_ratio(norm_input, trade["norm_name"]) / 100.0

            alias_score = 0.0
            if trade["aliases"]:
                alias_score = max(
                    fuzz.token_set_ratio(norm_input, alias) / 100.0
                    for alias in trade["aliases"]
                )

            # Combined raw score
            raw_score = max(name_score, alias_score)
            if rule_matched:
                raw_score = max(raw_score, 0.88)

            # Extra boost if skills are provided and corroborate
            if skills:
                norm_skills = normalize_title(skills)
                skill_sim = fuzz.partial_ratio(norm_skills, trade["norm_name"]) / 100.0
                if skill_sim > 0.7:
                    raw_score = min(1.0, raw_score + 0.08)

            # Calibrate confidence using sigmoid scaling
            # Maps raw_score in [0.4, 0.95] to confidence in [0.1, 0.98]
            calibrated = self._calibrate(raw_score)

            if calibrated > 0.25:
                scored_matches.append((
                    trade["nco_code"],
                    trade["qp_code"] or "",
                    trade["id"],
                    round(calibrated, 4),
                ))

        scored_matches.sort(key=lambda x: x[3], reverse=True)
        return scored_matches

    def _calibrate(self, raw: float) -> float:
        """
        Isotonic-style logistic sigmoid calibration.
        """
        if raw <= 0.0:
            return 0.0
        if raw >= 0.95:
            return min(0.99, raw)
        # Shift midpoint to ~0.60
        k = 8.0
        x0 = 0.60
        prob = 1.0 / (1.0 + math.exp(-k * (raw - x0)))
        return min(0.99, max(0.01, prob))
