"""
Gap, Early Warning Alerts & Rankings Endpoints (Layer 6).
Provides probabilistic gap analysis, early warning alerts with hysteresis,
rankings (top shortages / top saturations), and multilingual deterministic explanations.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Alert, District, Gap, Sector, State, Trade
from app.db.session import get_db
from pipelines.gap.explain import MultilingualExplainer

router = APIRouter()
explainer = MultilingualExplainer()


class GapItem(BaseModel):
    origin_month: str
    district_id: int
    district_name: str
    state_code: str
    trade_id: int
    trade_name: str
    window_months: int
    d_mean: float
    s_mean: float
    g_mean: float
    gap_rate: float
    p_shortage: float
    p_oversupply: float
    tolerance: float
    severity: float
    status: str
    confidence: str
    data_mode: str


class GapResponse(BaseModel):
    total: int
    items: List[GapItem]


class AlertItem(BaseModel):
    origin_month: str
    district_id: int
    district_name: str
    state_code: str
    trade_id: int
    trade_name: str
    flag: str
    overlays: Optional[List[str]] = None
    since_month: str
    persistence_count: int
    p_value: float
    expected_gap: float
    demand_trend: float
    capacity_trend: float
    confidence: str
    drivers: Optional[Dict[str, Any]] = None
    suggested_action: str
    data_mode: str


class AlertResponse(BaseModel):
    total: int
    items: List[AlertItem]


class RankingItem(BaseModel):
    rank: int
    district_name: str
    state_code: str
    trade_name: str
    sector_name: str
    severity: float
    expected_gap: float
    gap_rate: float
    probability: float
    status: str
    confidence: str
    data_mode: str


class RankingsResponse(BaseModel):
    top_shortages: List[RankingItem]
    top_saturations: List[RankingItem]


@router.get("/gaps", response_model=GapResponse)
async def get_gaps(
    district_id: Optional[int] = Query(None, description="District ID filter"),
    state_code: Optional[str] = Query(None, description="State code filter (KA, TN, UP)"),
    trade_id: Optional[int] = Query(None, description="Trade ID filter"),
    window_months: int = Query(12, description="Window months (12 or 3)"),
    status: Optional[str] = Query(None, description="Status filter (Shortage, Balanced, Surplus)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Query probabilistic demand-supply gaps.
    Includes expected gap, gap rate, shortage probability, tolerance, and severity.
    """
    stmt = (
        select(Gap, District.name, State.code, Trade.name)
        .join(District, Gap.district_id == District.id)
        .join(State, District.state_id == State.id)
        .join(Trade, Gap.trade_id == Trade.id)
        .where(Gap.window_months == window_months)
    )

    if district_id is not None:
        stmt = stmt.where(Gap.district_id == district_id)
    if state_code is not None:
        stmt = stmt.where(State.code == state_code.upper())
    if trade_id is not None:
        stmt = stmt.where(Gap.trade_id == trade_id)
    if status is not None:
        stmt = stmt.where(Gap.status == status)

    stmt = stmt.order_by(desc(Gap.severity)).offset(offset).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()

    items = [
        GapItem(
            origin_month=g.origin_month,
            district_id=g.district_id,
            district_name=dist_name,
            state_code=st_code,
            trade_id=g.trade_id,
            trade_name=tr_name,
            window_months=g.window_months,
            d_mean=g.d_mean,
            s_mean=g.s_mean,
            g_mean=g.g_mean,
            gap_rate=g.gap_rate,
            p_shortage=g.p_shortage,
            p_oversupply=g.p_oversupply,
            tolerance=g.tolerance,
            severity=g.severity,
            status=g.status,
            confidence=g.confidence,
            data_mode=g.data_mode,
        )
        for g, dist_name, st_code, tr_name in rows
    ]

    return GapResponse(total=len(items), items=items)


@router.get("/alerts", response_model=AlertResponse)
async def get_alerts(
    district_id: Optional[int] = Query(None, description="District ID filter"),
    state_code: Optional[str] = Query(None, description="State code filter (KA, TN, UP)"),
    trade_id: Optional[int] = Query(None, description="Trade ID filter"),
    flag: Optional[str] = Query(None, description="Flag filter (Acute Shortage, Emerging Shortage, Approaching Saturation, Saturated)"),
    confidence: Optional[str] = Query(None, description="Confidence filter"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve early warning alerts with hysteresis state and persistence history.
    """
    stmt = (
        select(Alert, District.name, State.code, Trade.name)
        .join(District, Alert.district_id == District.id)
        .join(State, District.state_id == State.id)
        .join(Trade, Alert.trade_id == Trade.id)
    )

    if district_id is not None:
        stmt = stmt.where(Alert.district_id == district_id)
    if state_code is not None:
        stmt = stmt.where(State.code == state_code.upper())
    if trade_id is not None:
        stmt = stmt.where(Alert.trade_id == trade_id)
    if flag is not None:
        stmt = stmt.where(Alert.flag == flag)
    if confidence is not None:
        stmt = stmt.where(Alert.confidence == confidence)

    stmt = stmt.order_by(desc(Alert.p_value)).offset(offset).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()

    items = [
        AlertItem(
            origin_month=a.origin_month,
            district_id=a.district_id,
            district_name=dist_name,
            state_code=st_code,
            trade_id=a.trade_id,
            trade_name=tr_name,
            flag=a.flag,
            overlays=a.overlays,
            since_month=a.since_month,
            persistence_count=a.persistence_count,
            p_value=round(a.p_value, 3),
            expected_gap=round(a.expected_gap, 1),
            demand_trend=round(a.demand_trend, 3),
            capacity_trend=round(a.capacity_trend, 3),
            confidence=a.confidence,
            drivers=a.drivers_json,
            suggested_action=a.suggested_action,
            data_mode=a.data_mode,
        )
        for a, dist_name, st_code, tr_name in rows
    ]

    return AlertResponse(total=len(items), items=items)


@router.get("/rankings", response_model=RankingsResponse)
async def get_rankings(
    state_code: Optional[str] = Query(None, description="State filter (KA, TN, UP)"),
    sector_code: Optional[str] = Query(None, description="Sector code filter"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Produces two prioritized lists:
      1. Top Emerging / Acute Shortages (ranked by severity & expected gap)
      2. Top Saturation Risks (ranked by severity & expected oversupply)
    """
    base_stmt = (
        select(Gap, District.name, State.code, Trade.name, Sector.name)
        .join(District, Gap.district_id == District.id)
        .join(State, District.state_id == State.id)
        .join(Trade, Gap.trade_id == Trade.id)
        .join(Sector, Trade.sector_id == Sector.id)
        .where(Gap.window_months == 12)
    )

    if state_code is not None:
        base_stmt = base_stmt.where(State.code == state_code.upper())
    if sector_code is not None:
        base_stmt = base_stmt.where(Sector.code == sector_code.upper())

    # 1. Top Shortages
    stmt_short = (
        base_stmt.where(Gap.status == "Shortage")
        .order_by(desc(Gap.severity), desc(Gap.g_mean))
        .limit(limit)
    )
    res_short = await db.execute(stmt_short)
    shortages = [
        RankingItem(
            rank=i + 1,
            district_name=d_name,
            state_code=s_code,
            trade_name=t_name,
            sector_name=sec_name,
            severity=g.severity,
            expected_gap=g.g_mean,
            gap_rate=g.gap_rate,
            probability=g.p_shortage,
            status=g.status,
            confidence=g.confidence,
            data_mode=g.data_mode,
        )
        for i, (g, d_name, s_code, t_name, sec_name) in enumerate(res_short.all())
    ]

    # 2. Top Saturations
    stmt_sat = (
        base_stmt.where(Gap.status == "Surplus")
        .order_by(desc(Gap.severity), Gap.g_mean)
        .limit(limit)
    )
    res_sat = await db.execute(stmt_sat)
    saturations = [
        RankingItem(
            rank=i + 1,
            district_name=d_name,
            state_code=s_code,
            trade_name=t_name,
            sector_name=sec_name,
            severity=g.severity,
            expected_gap=g.g_mean,
            gap_rate=g.gap_rate,
            probability=g.p_oversupply,
            status=g.status,
            confidence=g.confidence,
            data_mode=g.data_mode,
        )
        for i, (g, d_name, s_code, t_name, sec_name) in enumerate(res_sat.all())
    ]

    return RankingsResponse(top_shortages=shortages, top_saturations=saturations)


@router.get("/explain-gap")
async def explain_gap(
    district_id: int = Query(..., description="District ID"),
    trade_id: int = Query(..., description="Trade ID"),
    lang: str = Query("en", description="Language: en, hi, kn, ta"),
    db: AsyncSession = Depends(get_db),
):
    """
    Deterministic explainability endpoint producing full policy narratives
    in 4 languages (English, Hindi, Kannada, Tamil) using pre-translated glossaries.
    """
    # Fetch Gap and Alert info
    stmt = (
        select(Gap, Alert, District.name, State.code, Trade.name)
        .join(District, Gap.district_id == District.id)
        .join(State, District.state_id == State.id)
        .join(Trade, Gap.trade_id == Trade.id)
        .outerjoin(Alert, (Alert.district_id == Gap.district_id) & (Alert.trade_id == Gap.trade_id))
        .where(Gap.district_id == district_id)
        .where(Gap.trade_id == trade_id)
        .where(Gap.window_months == 12)
    )
    res = await db.execute(stmt)
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Cell not found")

    g, a, dist_name, st_code, tr_name = row
    flag = a.flag if a else g.status
    overlays = a.overlays if a and a.overlays else []

    gap_info = {
        "d_mean": g.d_mean,
        "s_mean": g.s_mean,
        "g_mean": g.g_mean,
        "p_shortage": g.p_shortage,
        "p_oversupply": g.p_oversupply,
        "severity": g.severity,
    }

    return explainer.explain_cell(
        trade_name=tr_name,
        district_name=dist_name,
        state_code=st_code,
        flag=flag,
        overlays=overlays,
        gap_info=gap_info,
        confidence=g.confidence,
        data_mode=g.data_mode,
        drivers=a.drivers_json if a else {},
        lang=lang,
    )
