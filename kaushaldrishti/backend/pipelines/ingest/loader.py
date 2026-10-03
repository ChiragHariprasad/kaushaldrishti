"""
Ingest Loader: Adapter-driven data ingestion with Pydantic validation,
de-duplication, quarantine logging, and graceful synthetic fallback.
"""

import glob
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import yaml
from pydantic import BaseModel, Field, ValidationError

from app.db.models import QuarantineRecord, Source, DataQualityScorecard
from app.db.session import async_session_factory
from pipelines.taxonomy.filters import QualityFilter


from pydantic import BaseModel, Field, ValidationError, field_validator

logger = logging.getLogger("kaushaldrishti.ingest")


class IngestDataContract(BaseModel):
    """Canonical data contract for incoming records."""
    title: str = Field(..., min_length=2)
    district_name: Optional[str] = None
    state_name: Optional[str] = None
    posted_date: Optional[str] = None
    employer: Optional[str] = "Unknown"
    num_openings: int = Field(default=1, ge=0)
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    nco_code: Optional[str] = None
    data_mode: str = "live"

    model_config = {"extra": "ignore"}

    @field_validator("nco_code", mode="before")
    @classmethod
    def coerce_nco_code(cls, v: Any) -> Optional[str]:
        if v is None or pd.isna(v):
            return None
        return str(v).strip()

    @field_validator("title", "district_name", "state_name", "posted_date", "employer", mode="before")
    @classmethod
    def coerce_str_fields(cls, v: Any) -> Optional[str]:
        if v is None or pd.isna(v):
            return None
        return str(v).strip()


class IngestLoader:
    """
    Adapter-driven ingest processor.
    """

    def __init__(
        self,
        adapters_dir: Optional[str] = None,
        incoming_dir: Optional[str] = None,
        synthetic_dir: Optional[str] = None,
    ):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        self.adapters_dir = adapters_dir or os.path.join(base_dir, "adapters")
        self.incoming_dir = incoming_dir or os.path.join(base_dir, "data", "incoming")
        self.synthetic_dir = synthetic_dir or os.path.join(base_dir, "data", "synthetic")
        self.adapters: Dict[str, Dict[str, Any]] = self._load_adapters()

    def _load_adapters(self) -> Dict[str, Dict[str, Any]]:
        adapters = {}
        for yml_file in glob.glob(os.path.join(self.adapters_dir, "*.yaml")):
            try:
                with open(yml_file, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f)
                    if cfg and "adapter" in cfg:
                        name = cfg["adapter"]["name"]
                        adapters[name] = cfg["adapter"]
            except Exception as e:
                logger.error(f"Failed to parse adapter config {yml_file}: {e}")
        return adapters

    def find_incoming_file(self, adapter_name: str) -> Optional[str]:
        """Looks for an incoming file matching adapter patterns in data/incoming/."""
        adapter = self.adapters.get(adapter_name)
        if not adapter:
            return None
        patterns = adapter.get("file_patterns", [])
        for pat in patterns:
            matches = glob.glob(os.path.join(self.incoming_dir, pat))
            if matches:
                return matches[0]
        return None

    def ingest_source(self, source_name: str) -> Dict[str, Any]:
        """
        Loads data for a given source:
        1. Checks data/incoming/ for raw file
        2. If present, runs through adapter column mapping and Pydantic validation
        3. If absent, logs warning and falls back to synthetic dataset (data_mode='synthetic')
        """
        incoming_file = self.find_incoming_file(source_name)
        adapter = self.adapters.get(source_name, {})

        if incoming_file and os.path.exists(incoming_file):
            logger.info(f"Ingesting real data for '{source_name}' from {incoming_file}")
            return self._process_incoming_file(source_name, incoming_file, adapter)
        else:
            logger.warning(
                f"No incoming file found for source '{source_name}' in {self.incoming_dir}. "
                f"Falling back to synthetic data (data_mode='synthetic')."
            )
            return self._fallback_to_synthetic(source_name)

    def _process_incoming_file(
        self, source_name: str, file_path: str, adapter: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Reads file, maps columns, validates records, quarantines failures."""
        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path, encoding=adapter.get("encoding", "utf-8"))
            elif file_path.endswith((".xlsx", ".xls")):
                df = pd.read_excel(file_path)
            else:
                return {"status": "error", "message": f"Unsupported format: {file_path}"}
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return {"status": "error", "message": str(e)}

        col_map = adapter.get("column_mapping", {})
        # Rename available columns
        df_mapped = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

        qf = QualityFilter()
        valid_records = []
        quarantined_count = 0

        for _, row in df_mapped.iterrows():
            record_dict = row.to_dict()
            record_dict["data_mode"] = adapter.get("data_mode", "partner")

            # 1. Pydantic validation
            try:
                validated = IngestDataContract(**record_dict)
            except ValidationError as ve:
                quarantined_count += 1
                continue

            # 2. Quality filter (dedup, ghost/spam)
            passes, reason = qf.process_record(validated.model_dump())
            if passes:
                valid_records.append(validated.model_dump())
            else:
                quarantined_count += 1

        quality_stats = qf.get_quality_metrics()
        return {
            "source": source_name,
            "data_mode": adapter.get("data_mode", "partner"),
            "file": file_path,
            "total_records": len(df),
            "valid_records": len(valid_records),
            "quarantined": quarantined_count,
            "dedup_rate": quality_stats["dedup_rate"],
            "ghost_spam_rate": quality_stats["ghost_spam_rate"],
            "records": valid_records,
        }

    def _fallback_to_synthetic(self, source_name: str) -> Dict[str, Any]:
        """Loads pre-generated synthetic parquet for this source."""
        evidence_parquet = os.path.join(self.synthetic_dir, "evidence_units.parquet")
        if not os.path.exists(evidence_parquet):
            return {
                "source": source_name,
                "data_mode": "synthetic",
                "valid_records": 0,
                "message": "Synthetic dataset not yet generated.",
            }

        # Read only rows for this source
        df = pd.read_parquet(evidence_parquet)
        src_df = df[df["source_id"] == source_name]

        return {
            "source": source_name,
            "data_mode": "synthetic",
            "total_records": len(src_df),
            "valid_records": len(src_df),
            "quarantined": 0,
            "dedup_rate": 0.0,
            "ghost_spam_rate": 0.0,
            "is_synthetic_fallback": True,
        }
