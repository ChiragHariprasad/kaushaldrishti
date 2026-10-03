"""
Unit and Integration tests for Ingest Loader, Adapters, and Data Contracts.
"""

import os
import pytest
import pandas as pd
from pipelines.ingest.loader import IngestLoader, IngestDataContract


def test_adapters_loaded():
    loader = IngestLoader()
    assert len(loader.adapters) >= 4
    assert "ncs" in loader.adapters
    assert "portal" in loader.adapters
    assert "plfs" in loader.adapters
    assert "eshram" in loader.adapters


def test_data_contract_validation():
    # Valid record
    valid = IngestDataContract(
        title="EV Service Technician",
        district_name="Bengaluru Urban",
        state_name="Karnataka",
        posted_date="2024-02-01",
        num_openings=5,
        min_salary=20000,
        data_mode="partner",
    )
    assert valid.title == "EV Service Technician"
    assert valid.num_openings == 5

    # Invalid title (< 2 chars)
    with pytest.raises(Exception):
        IngestDataContract(title="x")


def test_synthetic_fallback():
    loader = IngestLoader()
    # No file in incoming -> fallback to synthetic
    res = loader.ingest_source("ncs")
    assert res["data_mode"] == "synthetic"
    assert res["valid_records"] > 0
    assert res.get("is_synthetic_fallback") is True


def test_real_file_adapter_processing(tmp_path):
    # Create temporary dummy NCS CSV
    dummy_csv = tmp_path / "ncs_sample.csv"
    df = pd.DataFrame([
        {
            "job_title": "EV Service Technician",
            "occupation_code": "7231.0101",
            "district": "Bengaluru Urban",
            "state": "Karnataka",
            "date_posted": "2024-03-01",
            "employer_name": "EV Motors Ltd",
            "vacancies": 3,
            "salary_min": 25000,
            "salary_max": 35000,
            "skills": "EV Battery",
        },
        {
            # Invalid short title -> should quarantine
            "job_title": "a",
            "occupation_code": "0000",
            "district": "Bengaluru Urban",
            "state": "Karnataka",
            "date_posted": "2024-03-01",
            "employer_name": "Bad Agency",
            "vacancies": 1,
            "salary_min": 25000,
            "salary_max": 35000,
            "skills": "None",
        },
    ])
    df.to_csv(dummy_csv, index=False)

    loader = IngestLoader(incoming_dir=str(tmp_path))
    res = loader._process_incoming_file("ncs", str(dummy_csv), loader.adapters["ncs"])

    assert res["total_records"] == 2
    assert res["valid_records"] == 1
    assert res["quarantined"] == 1
    assert res["records"][0]["title"] == "EV Service Technician"
