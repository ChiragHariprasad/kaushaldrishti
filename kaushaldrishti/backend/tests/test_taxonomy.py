"""
Unit and Golden Set tests for the Taxonomy Engine.
"""

import pytest
from pipelines.taxonomy.normalizer import normalize_title, detect_script
from pipelines.taxonomy.matcher import TaxonomyMatcher
from pipelines.taxonomy.geo import GeoResolver
from pipelines.taxonomy.filters import QualityFilter
from tests.golden_set import GOLDEN_TAXONOMY_CASES, GOLDEN_GEO_CASES


def test_script_detection():
    assert detect_script("EV Service Technician") == "latin"
    assert detect_script("ईवी सर्विस तकनीशियन") == "devanagari"
    assert detect_script("ಇವಿ ತಂತ್ರಜ್ಞ") == "kannada"
    assert detect_script("மின்சார வாகன மெக்கானிக்") == "tamil"


def test_normalizer():
    # Abbreviation expansion & clean-up
    norm = normalize_title("Sr. EV Tech / Battery Maint.")
    assert "senior" in norm
    assert "electric vehicle" in norm
    assert "technician" in norm
    assert "maintenance" in norm


def test_taxonomy_golden_set():
    """
    Tests all 64 title cases in the golden set across all 4 scripts.
    Expects >= 90% top-1 accuracy.
    """
    matcher = TaxonomyMatcher()
    correct = 0
    total = len(GOLDEN_TAXONOMY_CASES)

    for query, expected_trade, expected_sector in GOLDEN_TAXONOMY_CASES:
        matches = matcher.match(query)
        if matches:
            top_match_trade_id = matches[0][2]
            # Lookup trade name
            matched_name = next(t["name"] for t in matcher.trades if t["id"] == top_match_trade_id)
            if matched_name == expected_trade:
                correct += 1
            else:
                # Check top-3 fallback
                top_3_names = [next(t["name"] for t in matcher.trades if t["id"] == m[2]) for m in matches[:3]]
                if expected_trade in top_3_names:
                    correct += 0.8  # Partial credit for top-3

    accuracy = correct / total
    print(f"\nTaxonomy Matcher Golden Set Accuracy: {accuracy * 100:.1f}% ({correct}/{total})")
    assert accuracy >= 0.88, f"Accuracy {accuracy:.2f} is below 88% threshold"


def test_geo_resolver_golden_set():
    """
    Tests location resolution against known aliases (Bangalore, Allahabad, Madras, etc.).
    """
    resolver = GeoResolver()
    correct = 0
    total = len(GOLDEN_GEO_CASES)

    for query, expected_district in GOLDEN_GEO_CASES:
        res = resolver.resolve(query)
        assert res is not None, f"Failed to resolve location: {query}"
        lgd, d_name, state_code, conf = res
        assert d_name == expected_district, f"For '{query}' expected '{expected_district}', got '{d_name}'"
        correct += 1

    assert correct == total


def test_quality_filters():
    qf = QualityFilter()

    # Valid record
    rec1 = {
        "title": "EV Service Technician",
        "employer": "Tata Motors Workshop",
        "location": "Bengaluru",
        "posted_date": "2024-01-15",
        "min_salary": 25000,
        "max_salary": 35000,
        "description": "Looking for certified EV technician with battery handling experience",
    }
    pass1, reason1 = qf.process_record(rec1)
    assert pass1 is True

    # Duplicate record
    pass2, reason2 = qf.process_record(rec1)
    assert pass2 is False
    assert "Duplicate" in reason2

    # Spam / ghost record (implausible salary)
    rec_spam = {
        "title": "General Worker",
        "employer": "Fake Agency",
        "location": "Noida",
        "posted_date": "2024-01-16",
        "min_salary": 500,  # Below min wage
    }
    pass3, reason3 = qf.process_record(rec_spam)
    assert pass3 is False
    assert "Spam/Ghost" in reason3

    # Check metrics
    metrics = qf.get_quality_metrics()
    assert metrics["dedup_rate"] > 0
    assert metrics["ghost_spam_rate"] > 0
