"""
Policy Scenario Simulator API Endpoints (Layer 7 & 8).
Enables interactive "what-if" policy simulation with stock-flow pipeline delays.
Persists simulation runs to the database and retrieves scenario outputs.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path as FPath, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import District, Gap, ScenarioRun, Trade, TrainingPipeline
from app.db.session import get_db
from pipelines.scenario.simulator import PolicyScenarioSimulator

router = APIRouter()
simulator = PolicyScenarioSimulator(simulation_months=24)


class ScenarioRequest(BaseModel):
    district_id: int = Field(..., description="Target district ID")
    trade_id: int = Field(..., description="Target trade ID")
    seat_delta_pct: float = Field(0.15, ge=-0.50, le=0.50, description="Seat allocation change % (-0.50 to +0.50)")
    completion_delta_pp: float = Field(0.0, ge=-0.30, le=0.30, description="Completion rate delta in percentage points")
    new_centre_capacity: int = Field(0, ge=0, description="Additional capacity from a newly sanctioned training centre")
    new_centre_build_lag_months: int = Field(6, ge=0, le=24, description="Months before new centre becomes operational")
    demand_case: str = Field("base", description="'base', 'high', or 'low'")
    start_month: str = Field("2025-01", description="Intervention start cycle (YYYY-MM)")


class ScenarioResponse(BaseModel):
    scenario_id: str
    created_at: str
    district_id: int
    district_name: str
    trade_id: int
    trade_name: str
    parameters: Dict[str, Any]
    summary: Dict[str, Any]
    series: Dict[str, Any]
    assumptions: List[str]


@router.post("/scenarios", response_model=ScenarioResponse)
async def create_scenario(
    req: ScenarioRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Simulate a policy intervention (e.g. +15% seat allocation, new centre, completion bump).
    Returns monthly baseline vs intervention time-series and identifies the gap closure cycle.
    """
    # 1. Fetch district and trade
    d_stmt = select(District.name).where(District.id == req.district_id)
    d_res = await db.execute(d_stmt)
    dist_row = d_res.first()
    if not dist_row:
        raise HTTPException(status_code=404, detail="District not found")
    dist_name = dist_row[0]

    t_stmt = select(Trade.name, Trade.course_months).where(Trade.id == req.trade_id)
    t_res = await db.execute(t_stmt)
    trade_row = t_res.first()
    if not trade_row:
        raise HTTPException(status_code=404, detail="Trade not found")
    trade_name, course_months = trade_row

    # 2. Fetch baseline gap record
    g_stmt = (
        select(Gap)
        .where(Gap.district_id == req.district_id)
        .where(Gap.trade_id == req.trade_id)
        .where(Gap.window_months == 12)
    )
    g_res = await db.execute(g_stmt)
    gap_row = g_res.scalar_one_or_none()

    base_demand = gap_row.d_mean if gap_row else 200.0
    demand_sigma = (base_demand * 0.20)  # estimated 20% volatility
    base_supply = gap_row.s_mean if gap_row else 150.0

    # 3. Fetch training pipeline throughput parameters
    pipe_stmt = (
        select(TrainingPipeline)
        .where(TrainingPipeline.district_id == req.district_id)
        .where(TrainingPipeline.trade_id == req.trade_id)
        .order_by(TrainingPipeline.month.desc())
        .limit(1)
    )
    pipe_res = await db.execute(pipe_stmt)
    pipe_row = pipe_res.scalar_one_or_none()

    if pipe_row and pipe_row.capacity > 0:
        base_capacity = pipe_row.capacity
        fill_rate = min(1.0, pipe_row.enrolled / max(1, pipe_row.allocated_seats))
        completion_rate = min(1.0, pipe_row.completed / max(1, pipe_row.enrolled))
        cert_rate = min(1.0, pipe_row.certified / max(1, pipe_row.completed))
    else:
        base_capacity = int(base_supply * 1.5)
        fill_rate = 0.85
        completion_rate = 0.80
        cert_rate = 0.90

    # 4. Run stock-flow simulation
    sim_result = simulator.simulate(
        base_demand=base_demand,
        demand_sigma=demand_sigma,
        base_capacity=base_capacity,
        fill_rate=fill_rate,
        completion_rate=completion_rate,
        cert_rate=cert_rate,
        course_months=course_months,
        seat_delta_pct=req.seat_delta_pct,
        completion_delta_pp=req.completion_delta_pp,
        new_centre_capacity=req.new_centre_capacity,
        new_centre_build_lag_months=req.new_centre_build_lag_months,
        demand_case=req.demand_case,
        start_month_str=req.start_month,
    )

    # 5. Persist scenario run
    scenario_id = str(uuid.uuid4())
    now_utc = datetime.now(timezone.utc)

    run_obj = ScenarioRun(
        id=scenario_id,
        district_id=req.district_id,
        trade_id=req.trade_id,
        seat_delta_pct=req.seat_delta_pct,
        completion_delta_pp=req.completion_delta_pp,
        new_centre_capacity=req.new_centre_capacity,
        demand_case=req.demand_case,
        results_json=sim_result,
        created_at=now_utc,
    )
    db.add(run_obj)
    await db.commit()

    return ScenarioResponse(
        scenario_id=scenario_id,
        created_at=now_utc.isoformat(),
        district_id=req.district_id,
        district_name=dist_name,
        trade_id=req.trade_id,
        trade_name=trade_name,
        parameters=sim_result["parameters"],
        summary=sim_result["summary"],
        series=sim_result["series"],
        assumptions=sim_result["assumptions"],
    )


@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: str = FPath(..., description="Scenario run UUID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a previously simulated policy scenario by ID.
    """
    stmt = (
        select(ScenarioRun, District.name, Trade.name)
        .join(District, ScenarioRun.district_id == District.id)
        .join(Trade, ScenarioRun.trade_id == Trade.id)
        .where(ScenarioRun.id == scenario_id)
    )
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Scenario run not found")

    run_obj, dist_name, trade_name = row
    sim_data = run_obj.results_json

    return ScenarioResponse(
        scenario_id=run_obj.id,
        created_at=run_obj.created_at.isoformat(),
        district_id=run_obj.district_id,
        district_name=dist_name,
        trade_id=run_obj.trade_id,
        trade_name=trade_name,
        parameters=sim_data["parameters"],
        summary=sim_data["summary"],
        series=sim_data["series"],
        assumptions=sim_data["assumptions"],
    )
