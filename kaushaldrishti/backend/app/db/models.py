"""
Canonical Database Schema (SQLAlchemy 2.0 ORM).
Supports PostgreSQL and SQLite.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.session import Base


# ─── Dimension Tables ────────────────────────────────────────────────────────


class State(Base):
    __tablename__ = "state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    districts: Mapped[List["District"]] = relationship("District", back_populates="state")


class District(Base):
    __tablename__ = "district"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lgd_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    state_id: Mapped[int] = mapped_column(Integer, ForeignKey("state.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name_variants: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # alternate names, aliases
    population_working_age: Mapped[int] = mapped_column(Integer, default=500000, nullable=False)
    urban_rural_aspirational: Mapped[str] = mapped_column(String(20), default="rural", nullable=False)
    geometry_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # GeoJSON polygon/centroid

    state: Mapped["State"] = relationship("State", back_populates="districts")


class Sector(Base):
    __tablename__ = "sector"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)

    trades: Mapped[List["Trade"]] = relationship("Trade", back_populates="sector")


class Trade(Base):
    __tablename__ = "trade"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sector_id: Mapped[int] = mapped_column(Integer, ForeignKey("sector.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    nco_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    nco_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # rule 7: false unless official
    qp_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    nsqf_level: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    course_months: Mapped[int] = mapped_column(Integer, default=6, nullable=False)  # L
    aliases: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    title_patterns: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    sector: Mapped["Sector"] = relationship("Sector", back_populates="trades")


class Source(Base):
    __tablename__ = "source"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g., 'ncs', 'portal', 'plfs', 'eshram', 'udyam'
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    nominal_update_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    independence_group: Mapped[str] = mapped_column(String(50), nullable=False)  # for corroboration scoring
    licence: Mapped[str] = mapped_column(String(100), default="Government Open Data", nullable=False)
    access_mode: Mapped[str] = mapped_column(String(50), default="public_aggregate", nullable=False)


# ─── Fact Tables ─────────────────────────────────────────────────────────────


class RawRecord(Base):
    """Immutable log of raw incoming records."""
    __tablename__ = "raw_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(String(50), ForeignKey("source.id"), nullable=False)
    pulled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    schema_version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    data_mode: Mapped[str] = mapped_column(String(30), default="synthetic", nullable=False)  # live, public_aggregate, partner, synthetic
    payload_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)


class EvidenceUnit(Base):
    """Processed evidence unit per source and (month, district, trade) cell."""
    __tablename__ = "evidence_unit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)  # YYYY-MM
    district_id: Mapped[int] = mapped_column(Integer, ForeignKey("district.id"), nullable=False, index=True)
    trade_id: Mapped[int] = mapped_column(Integer, ForeignKey("trade.id"), nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String(50), ForeignKey("source.id"), nullable=False)

    n_eff: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    o_hat: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    y_log: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sigma2: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    alpha: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    beta: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    z: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    v: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    gate_pass: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    gate_reason: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    r_k: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # reliability factor
    data_mode: Mapped[str] = mapped_column(String(30), default="synthetic", nullable=False)

    __table_args__ = (
        Index("idx_evidence_cell", "month", "district_id", "trade_id", "source_id"),
    )


class LatentDemand(Base):
    """Kalman filtered latent demand and published LDI."""
    __tablename__ = "latent_demand"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)  # YYYY-MM
    district_id: Mapped[int] = mapped_column(Integer, ForeignKey("district.id"), nullable=False, index=True)
    trade_id: Mapped[int] = mapped_column(Integer, ForeignKey("trade.id"), nullable=False, index=True)

    m: Mapped[float] = mapped_column(Float, nullable=False)  # posterior log-openings mean
    P: Mapped[float] = mapped_column(Float, nullable=False)  # posterior variance
    slope: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # b_t
    data_share: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # omega
    fallback_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0=district, 1=state, 2=national
    n_gated_sources: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    intensity_iota: Mapped[float] = mapped_column(Float, nullable=False)
    ldi: Mapped[float] = mapped_column(Float, nullable=False)  # 0 to 100
    ldi_lo: Mapped[float] = mapped_column(Float, nullable=False)
    ldi_hi: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[str] = mapped_column(String(10), default="Medium", nullable=False)  # High, Medium, Low

    # Drivers
    V: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # expected openings
    G: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 3-month annualized growth %
    R: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # recency index
    P_persist: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # growth persistence months
    B: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # breadth (effective employers)
    I: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # corroboration score

    data_mode: Mapped[str] = mapped_column(String(30), default="synthetic", nullable=False)

    __table_args__ = (
        Index("idx_latent_demand_cell", "month", "district_id", "trade_id"),
    )


class SourceContribution(Base):
    """Exact source attribution for the Why panel."""
    __tablename__ = "source_contribution"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month: Mapped[str] = mapped_column(String(7), nullable=False)
    district_id: Mapped[int] = mapped_column(Integer, ForeignKey("district.id"), nullable=False)
    trade_id: Mapped[int] = mapped_column(Integer, ForeignKey("trade.id"), nullable=False)
    source_id: Mapped[str] = mapped_column(String(50), ForeignKey("source.id"), nullable=False)

    weight: Mapped[float] = mapped_column(Float, nullable=False)
    contribution: Mapped[float] = mapped_column(Float, nullable=False)


class TrainingPipeline(Base):
    """Training supply pipeline counts per centre, trade, month."""
    __tablename__ = "training_pipeline"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    district_id: Mapped[int] = mapped_column(Integer, ForeignKey("district.id"), nullable=False, index=True)
    trade_id: Mapped[int] = mapped_column(Integer, ForeignKey("trade.id"), nullable=False, index=True)
    centre_id: Mapped[str] = mapped_column(String(50), nullable=False)

    capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    allocated_seats: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    enrolled: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    certified: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    placed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # calibration only, NOT in supply equation
    data_mode: Mapped[str] = mapped_column(String(30), default="synthetic", nullable=False)


class SupplyForecast(Base):
    """Supply forecast draws and statistics."""
    __tablename__ = "supply_forecast"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    origin_month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    target_month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    district_id: Mapped[int] = mapped_column(Integer, ForeignKey("district.id"), nullable=False)
    trade_id: Mapped[int] = mapped_column(Integer, ForeignKey("trade.id"), nullable=False)
    window_months: Mapped[int] = mapped_column(Integer, default=12, nullable=False)

    s_mean: Mapped[float] = mapped_column(Float, nullable=False)
    s_q10: Mapped[float] = mapped_column(Float, nullable=False)
    s_q90: Mapped[float] = mapped_column(Float, nullable=False)
    basis: Mapped[str] = mapped_column(String(40), default="certified", nullable=False)  # capacity_based, certified, certified_plus_other
    data_mode: Mapped[str] = mapped_column(String(30), default="synthetic", nullable=False)


class DemandForecast(Base):
    """Demand forecast models and intervals."""
    __tablename__ = "demand_forecast"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    origin_month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    horizon: Mapped[str] = mapped_column(String(10), nullable=False)  # '3', '6', '12', 'cohort'
    district_id: Mapped[int] = mapped_column(Integer, ForeignKey("district.id"), nullable=False)
    trade_id: Mapped[int] = mapped_column(Integer, ForeignKey("trade.id"), nullable=False)

    mean: Mapped[float] = mapped_column(Float, nullable=False)
    q10: Mapped[float] = mapped_column(Float, nullable=False)
    q90: Mapped[float] = mapped_column(Float, nullable=False)
    model: Mapped[str] = mapped_column(String(50), default="ensemble", nullable=False)
    fallback_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    data_mode: Mapped[str] = mapped_column(String(30), default="synthetic", nullable=False)


class Gap(Base):
    """Gap analysis records."""
    __tablename__ = "gap"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    origin_month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    horizon: Mapped[str] = mapped_column(String(10), nullable=False)
    district_id: Mapped[int] = mapped_column(Integer, ForeignKey("district.id"), nullable=False)
    trade_id: Mapped[int] = mapped_column(Integer, ForeignKey("trade.id"), nullable=False)
    window_months: Mapped[int] = mapped_column(Integer, default=12, nullable=False)

    d_mean: Mapped[float] = mapped_column(Float, nullable=False)
    s_mean: Mapped[float] = mapped_column(Float, nullable=False)
    g_mean: Mapped[float] = mapped_column(Float, nullable=False)
    gap_rate: Mapped[float] = mapped_column(Float, nullable=False)
    p_shortage: Mapped[float] = mapped_column(Float, nullable=False)
    p_oversupply: Mapped[float] = mapped_column(Float, nullable=False)
    tolerance: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[float] = mapped_column(Float, nullable=False)  # 0 to 100
    status: Mapped[str] = mapped_column(String(20), default="Balanced", nullable=False)  # Shortage, Balanced, Surplus
    confidence: Mapped[str] = mapped_column(String(10), default="Medium", nullable=False)
    data_mode: Mapped[str] = mapped_column(String(30), default="synthetic", nullable=False)


class Alert(Base):
    """Early warning alerts with hysteresis."""
    __tablename__ = "alert"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    origin_month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    district_id: Mapped[int] = mapped_column(Integer, ForeignKey("district.id"), nullable=False)
    trade_id: Mapped[int] = mapped_column(Integer, ForeignKey("trade.id"), nullable=False)

    flag: Mapped[str] = mapped_column(String(50), nullable=False)  # Acute Shortage, Emerging Shortage, Approaching Saturation, Saturated, Stable
    overlays: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)  # ['Rapid Growth', 'Volatile']
    since_month: Mapped[str] = mapped_column(String(7), nullable=False)
    persistence_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    p_value: Mapped[float] = mapped_column(Float, nullable=False)
    expected_gap: Mapped[float] = mapped_column(Float, nullable=False)
    demand_trend: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    capacity_trend: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    confidence: Mapped[str] = mapped_column(String(10), default="Medium", nullable=False)
    drivers_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    suggested_action: Mapped[str] = mapped_column(String(255), default="Review next-cycle seat allocation", nullable=False)
    data_mode: Mapped[str] = mapped_column(String(30), default="synthetic", nullable=False)


class AlertHistory(Base):
    """Audit log of alert state transitions (hysteresis)."""
    __tablename__ = "alert_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    district_id: Mapped[int] = mapped_column(Integer, ForeignKey("district.id"), nullable=False)
    trade_id: Mapped[int] = mapped_column(Integer, ForeignKey("trade.id"), nullable=False)
    month: Mapped[str] = mapped_column(String(7), nullable=False)
    previous_flag: Mapped[str] = mapped_column(String(50), nullable=False)
    new_flag: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class MappingReviewQueue(Base):
    """Taxonomy matches with confidence < threshold requiring review."""
    __tablename__ = "mapping_review_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    raw_title: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_id: Mapped[str] = mapped_column(String(50), nullable=False)
    matched_trade_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    matched_nco: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending, approved, rejected, remapped
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DataQualityScorecard(Base):
    """Data quality scorecard per source."""
    __tablename__ = "data_quality_scorecard"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(String(50), ForeignKey("source.id"), nullable=False)
    month: Mapped[str] = mapped_column(String(7), nullable=False)
    records_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_records: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quarantine_records: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dedup_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ghost_spam_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    freshness_days: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reliability_r_k: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class QuarantineRecord(Base):
    """Rejected records that failed schema validation."""
    __tablename__ = "quarantine_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(String(50), nullable=False)
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=False)
    raw_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    quarantined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AuditLog(Base):
    """Audit log of queries and user overrides."""
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user_key: Mapped[str] = mapped_column(String(100), default="anonymous", nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="viewer", nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)


class ScenarioRun(Base):
    """Logged policy scenario simulation runs."""
    __tablename__ = "scenario_run"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    district_id: Mapped[int] = mapped_column(Integer, ForeignKey("district.id"), nullable=False)
    trade_id: Mapped[int] = mapped_column(Integer, ForeignKey("trade.id"), nullable=False)
    seat_delta_pct: Mapped[float] = mapped_column(Float, nullable=False)
    completion_delta_pp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    new_centre_capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    demand_case: Mapped[str] = mapped_column(String(20), default="base", nullable=False)
    results_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
