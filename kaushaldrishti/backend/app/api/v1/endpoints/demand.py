"""
Demand Index and Explainability Endpoints (Layers 4 & 6).
Provides LDI queryability, credible bounds, driver descriptors, and exact source attributions.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import District, LatentDemand, Sector, SourceContribution, State, Trade
from app.db.session import get_db

router = APIRouter()


class DescriptorsSchema(BaseModel):
    V: float  # expected openings
    G: float  # 3-month annualized growth %
    R: float  # recency index
    P_persist: int  # growth persistence months
    B: float  # breadth (effective employers)
    I: float  # corroboration score


class DemandIndexItem(BaseModel):
    month: str
    state_code: str
    state_name: str
    district_name: str
    lgd_code: str
    sector_name: str
    trade_name: str
    trade_id: int
    nco_code: str
    expected_openings: float
    intensity_iota: float
    ldi: float
    ldi_lo: float
    ldi_hi: float
    confidence: str
    fallback_level: int
    data_share: float
    descriptors: DescriptorsSchema
    data_mode: str


class SourceAttributionItem(BaseModel):
    source_id: str
    weight: float
    contribution: float
    percentage: float


class ExplainDemandResponse(BaseModel):
    cell: Dict[str, Any]
    ldi: float
    ldi_lo: float
    ldi_hi: float
    confidence: str
    data_mode: str
    prior_weight: float
    source_contributions: List[SourceAttributionItem]
    descriptors: DescriptorsSchema
    narrative: str


@router.get("/demand-index", response_model=List[DemandIndexItem])
async def get_demand_index(
    state: Optional[str] = Query(None, description="State code (e.g. KA, TN, UP) or name"),
    district: Optional[str] = Query(None, description="District name or LGD code"),
    sector: Optional[str] = Query(None, description="Sector name or code"),
    trade: Optional[str] = Query(None, description="Trade name"),
    month: Optional[str] = Query(None, description="Month YYYY-MM"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> List[DemandIndexItem]:
    """
    Returns Labour Demand Index (LDI) records with credible intervals,
    confidence badges, driver descriptors, and data_mode indicators.
    """
    stmt = (
        select(LatentDemand, District, State, Trade, Sector)
        .join(District, LatentDemand.district_id == District.id)
        .join(State, District.state_id == State.id)
        .join(Trade, LatentDemand.trade_id == Trade.id)
        .join(Sector, Trade.sector_id == Sector.id)
    )

    if month:
        stmt = stmt.where(LatentDemand.month == month)
    if state:
        stmt = stmt.where((State.code == state) | (State.name.ilike(f"%{state}%")))
    if district:
        stmt = stmt.where((District.lgd_code == district) | (District.name.ilike(f"%{district}%")))
    if sector:
        stmt = stmt.where((Sector.code == sector) | (Sector.name.ilike(f"%{sector}%")))
    if trade:
        stmt = stmt.where(Trade.name.ilike(f"%{trade}%"))

    stmt = stmt.order_by(LatentDemand.ldi.desc()).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()

    items = []
    for ld, dist, st, tr, sec in rows:
        items.append(
            DemandIndexItem(
                month=ld.month,
                state_code=st.code,
                state_name=st.name,
                district_name=dist.name,
                lgd_code=dist.lgd_code,
                sector_name=sec.name,
                trade_name=tr.name,
                trade_id=tr.id,
                nco_code=tr.nco_code,
                expected_openings=round(ld.V, 1),
                intensity_iota=ld.intensity_iota,
                ldi=ld.ldi,
                ldi_lo=ld.ldi_lo,
                ldi_hi=ld.ldi_hi,
                confidence=ld.confidence,
                fallback_level=ld.fallback_level,
                data_share=ld.data_share,
                descriptors=DescriptorsSchema(
                    V=ld.V,
                    G=ld.G,
                    R=ld.R,
                    P_persist=ld.P_persist,
                    B=ld.B,
                    I=ld.I,
                ),
                data_mode=ld.data_mode,
            )
        )

    return items


@router.get("/explain", response_model=ExplainDemandResponse)
async def explain_cell(
    district_id: int = Query(..., description="District ID"),
    trade_id: int = Query(..., description="Trade ID"),
    month: Optional[str] = Query(None, description="Month YYYY-MM"),
    db: AsyncSession = Depends(get_db),
) -> ExplainDemandResponse:
    """
    Exact source attribution for the Why Panel.
    Explains LDI drivers, exact Kalman source contributions, and data lineage.
    """
    # 1. Fetch LatentDemand record
    stmt = (
        select(LatentDemand, District, State, Trade, Sector)
        .join(District, LatentDemand.district_id == District.id)
        .join(State, District.state_id == State.id)
        .join(Trade, LatentDemand.trade_id == Trade.id)
        .join(Sector, Trade.sector_id == Sector.id)
        .where(LatentDemand.district_id == district_id, LatentDemand.trade_id == trade_id)
    )
    if month:
        stmt = stmt.where(LatentDemand.month == month)
    stmt = stmt.order_by(LatentDemand.month.desc()).limit(1)

    res = await db.execute(stmt)
    row = res.first()

    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Cell not found")

    ld, dist, st, tr, sec = row

    # 2. Fetch exact source contributions
    contrib_stmt = (
        select(SourceContribution)
        .where(
            SourceContribution.district_id == district_id,
            SourceContribution.trade_id == trade_id,
            SourceContribution.month == ld.month,
        )
    )
    c_res = await db.execute(contrib_stmt)
    c_rows = c_res.scalars().all()

    total_w = sum(c.weight for c in c_rows)
    prior_w = max(0.0, 1.0 - total_w)

    contrib_items = []
    for c in c_rows:
        pct = (c.weight / max(1e-4, total_w + prior_w)) * 100.0
        contrib_items.append(
            SourceAttributionItem(
                source_id=c.source_id,
                weight=round(c.weight, 4),
                contribution=round(c.contribution, 4),
                percentage=round(pct, 1),
            )
        )

    # Deterministic templated narrative (Rule 6: No LLM, deterministic templated explainability)
    narrative = (
        f"In {dist.name} ({st.name}), demand for {tr.name} registered an LDI of {ld.ldi:.1f} "
        f"(80% CI: {ld.ldi_lo:.1f}–{ld.ldi_hi:.1f}) in {ld.month}. "
        f"The 3-month annualized growth trend stands at {ld.G:+.1f}%. "
        f"This posterior index was fused from {len(contrib_items)} active sources with "
        f"{ld.confidence.lower()} confidence and a local data share of {ld.data_share * 100:.1f}%."
    )

    return ExplainDemandResponse(
        cell={
            "district_id": dist.id,
            "district_name": dist.name,
            "state_name": st.name,
            "trade_id": tr.id,
            "trade_name": tr.name,
            "sector_name": sec.name,
            "month": ld.month,
        },
        ldi=ld.ldi,
        ldi_lo=ld.ldi_lo,
        ldi_hi=ld.ldi_hi,
        confidence=ld.confidence,
        data_mode=ld.data_mode,
        prior_weight=round(prior_w, 4),
        source_contributions=contrib_items,
        descriptors=DescriptorsSchema(
            V=ld.V,
            G=ld.G,
            R=ld.R,
            P_persist=ld.P_persist,
            B=ld.B,
            I=ld.I,
        ),
        narrative=narrative,
    )
