"""
Supply Intelligence Endpoints (Layer 5).
Provides probabilistic supply forecasts with credibility intervals (q10, q90),
window aggregations (3-month quarterly watch, 12-month target setting), and explicit basis labels.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import District, Sector, State, SupplyForecast, Trade
from app.db.session import get_db

router = APIRouter()


class SupplyForecastItem(BaseModel):
    origin_month: str
    target_month: str
    state_code: str
    state_name: str
    district_name: str
    lgd_code: str
    sector_name: str
    trade_name: str
    trade_id: int
    nco_code: str
    window_months: int
    s_mean: float
    s_q10: float
    s_q90: float
    basis: str  # capacity_based, certified, certified_plus_other
    data_mode: str


@router.get("/supply", response_model=List[SupplyForecastItem])
async def get_supply_forecasts(
    state: Optional[str] = Query(None, description="State code (KA, TN, UP) or name"),
    district: Optional[str] = Query(None, description="District name or LGD code"),
    sector: Optional[str] = Query(None, description="Sector name"),
    trade: Optional[str] = Query(None, description="Trade name"),
    window_months: Optional[int] = Query(None, description="Window months (3 or 12)"),
    origin_month: Optional[str] = Query(None, description="Origin month YYYY-MM"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> List[SupplyForecastItem]:
    """
    Returns supply forecast draws and intervals for cohorts graduating in window [t, t+W).
    Strictly reports basis as capacity_based, certified, or certified_plus_other.
    """
    stmt = (
        select(SupplyForecast, District, State, Trade, Sector)
        .join(District, SupplyForecast.district_id == District.id)
        .join(State, District.state_id == State.id)
        .join(Trade, SupplyForecast.trade_id == Trade.id)
        .join(Sector, Trade.sector_id == Sector.id)
    )

    if origin_month:
        stmt = stmt.where(SupplyForecast.origin_month == origin_month)
    if window_months:
        stmt = stmt.where(SupplyForecast.window_months == window_months)
    if state:
        stmt = stmt.where((State.code == state) | (State.name.ilike(f"%{state}%")))
    if district:
        stmt = stmt.where((District.lgd_code == district) | (District.name.ilike(f"%{district}%")))
    if sector:
        stmt = stmt.where((Sector.code == sector) | (Sector.name.ilike(f"%{sector}%")))
    if trade:
        stmt = stmt.where(Trade.name.ilike(f"%{trade}%"))

    stmt = stmt.order_by(SupplyForecast.s_mean.desc()).limit(limit)
    result = await db.execute(stmt)
    rows = result.all()

    items = []
    for sf, dist, st, tr, sec in rows:
        items.append(
            SupplyForecastItem(
                origin_month=sf.origin_month,
                target_month=sf.target_month,
                state_code=st.code,
                state_name=st.name,
                district_name=dist.name,
                lgd_code=dist.lgd_code,
                sector_name=sec.name,
                trade_name=tr.name,
                trade_id=tr.id,
                nco_code=tr.nco_code,
                window_months=sf.window_months,
                s_mean=sf.s_mean,
                s_q10=sf.s_q10,
                s_q90=sf.s_q90,
                basis=sf.basis,
                data_mode=sf.data_mode,
            )
        )

    return items
