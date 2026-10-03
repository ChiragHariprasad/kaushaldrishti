"""
Taxonomy Engine: Title and Text Normalization & Script Detection.
Supports Latin, Devanagari (Hindi), Kannada, and Tamil.
"""

import re
import unicodedata
from typing import Dict, Tuple


# Script Unicode Ranges
SCRIPT_RANGES: Dict[str, Tuple[int, int]] = {
    "devanagari": (0x0900, 0x097F),
    "kannada": (0x0C80, 0x0CFF),
    "tamil": (0x0B80, 0x0BFF),
}

# Common Job Title Abbreviations & Expansion Mapping
TITLE_ABBREVIATIONS: Dict[str, str] = {
    "sr": "senior",
    "jr": "junior",
    "tech": "technician",
    "asst": "assistant",
    "mgr": "manager",
    "exec": "executive",
    "op": "operator",
    "mech": "mechanic",
    "maint": "maintenance",
    "gda": "general duty assistant",
    "mlt": "medical laboratory technician",
    "emt": "emergency medical technician",
    "cctv": "cctv installation technician",
    "ev": "electric vehicle",
    "qc": "quality control",
    "qa": "quality assurance",
    "elec": "electrician",
    "wh": "warehouse",
    "hha": "home health aide",
}


def detect_script(text: str) -> str:
    """
    Detect dominant script in input text.
    Returns: 'devanagari', 'kannada', 'tamil', or 'latin' (default).
    """
    counts = {"devanagari": 0, "kannada": 0, "tamil": 0, "latin": 0}
    for char in text:
        cp = ord(char)
        matched = False
        for script, (start, end) in SCRIPT_RANGES.items():
            if start <= cp <= end:
                counts[script] += 1
                matched = True
                break
        if not matched and char.isalpha():
            counts["latin"] += 1

    dominant = max(counts, key=counts.get)
    return dominant if counts[dominant] > 0 else "latin"


def normalize_title(title: str) -> str:
    """
    Normalise title for matching:
    - Lowercase
    - Unicode NFKD normalization
    - Strip punctuation and symbols (preserving Indic characters)
    - Expand common job abbreviations
    - Collapse extra whitespace
    """
    if not title:
        return ""

    # Normalize unicode
    text = unicodedata.normalize("NFKD", title.strip())

    # Lowercase
    text = text.lower()

    # Replace special separators with space
    text = re.sub(r"[/\\_\-\|,\.;:\(\)\[\]\{\}]", " ", text)

    # Remove digits and emojis
    text = re.sub(r"[0-9\+#@!\$%^&\*~`\?<>=\"\']", "", text)

    # Word-level expansion
    tokens = text.split()
    expanded = [TITLE_ABBREVIATIONS.get(t, t) for t in tokens]

    return " ".join(expanded)
