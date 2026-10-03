"""
Filters: De-duplication, Ghost/Spam detection, and Salary/Experience Normalization.
Tracks quality metrics (dedup rate, ghost rate).
"""

import hashlib
import re
from typing import Any, Dict, List, Optional, Set, Tuple


class QualityFilter:
    """
    Applies de-duplication, spam/ghost filtering, and salary validation.
    """

    def __init__(self):
        self._seen_hashes: Set[str] = set()
        self.total_processed: int = 0
        self.duplicates_count: int = 0
        self.ghost_spam_count: int = 0

    def compute_signature(self, title: str, employer: str, location: str, posted_date: str) -> str:
        """
        Creates a normalised deterministic hash of posting signature.
        """
        raw = f"{title.lower().strip()}|{employer.lower().strip()}|{location.lower().strip()}|{posted_date[:7]}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def is_ghost_or_spam(
        self,
        title: str,
        description: Optional[str] = None,
        salary_min: Optional[float] = None,
        salary_max: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Detects ghost/spam postings:
        - Implausible salary (< 4,000 INR/month or > 5,000,000 INR/month)
        - Very short / empty description and title
        - Obvious spam keyword patterns
        """
        if len(title.strip()) < 3:
            return True, "Title too short"

        if description and len(description.strip()) < 10:
            return True, "Description too short"

        # Salary plausibility check (monthly INR)
        if salary_min is not None and salary_min > 0:
            if salary_min < 3000:
                return True, "Salary below statutory minimum wage threshold"
            if salary_min > 5000000:
                return True, "Implausibly high monthly salary"

        if salary_max is not None and salary_max > 0:
            if salary_max > 10000000:
                return True, "Implausibly high salary ceiling"

        # Spam keywords
        lower_title = title.lower()
        if any(w in lower_title for w in ["earn from home fast", "click here", "guaranteed lakh daily", "100% lottery"]):
            return True, "Spam pattern matched in title"

        return False, None

    def process_record(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Evaluates record.
        Returns: (passes_filter: bool, reason: Optional[str])
        """
        self.total_processed += 1

        title = str(record.get("title", ""))
        employer = str(record.get("employer", "unknown"))
        location = str(record.get("location", ""))
        posted_date = str(record.get("posted_date", "2024-01-01"))
        salary_min = record.get("min_salary")
        salary_max = record.get("max_salary")
        desc = record.get("description")

        # 1. Ghost/Spam check
        is_spam, spam_reason = self.is_ghost_or_spam(title, desc, salary_min, salary_max)
        if is_spam:
            self.ghost_spam_count += 1
            return False, f"Spam/Ghost: {spam_reason}"

        # 2. Duplicate check
        sig = self.compute_signature(title, employer, location, posted_date)
        if sig in self._seen_hashes:
            self.duplicates_count += 1
            return False, "Duplicate record"
        self._seen_hashes.add(sig)

        return True, None

    def get_quality_metrics(self) -> Dict[str, float]:
        """Returns quality rates."""
        if self.total_processed == 0:
            return {"dedup_rate": 0.0, "ghost_spam_rate": 0.0}
        return {
            "dedup_rate": round(self.duplicates_count / self.total_processed, 4),
            "ghost_spam_rate": round(self.ghost_spam_count / self.total_processed, 4),
        }
