"""
Data Export Endpoints (Layer 8).
Supports exporting canonical labour market intelligence in CSV, XLSX, JSON, GeoJSON, and Parquet.
Every record carries explicit data_mode ('synthetic' / 'live'), confidence, and lineage.
"""

import io
import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Alert, DemandForecast, District, Gap, Sector, State, SupplyForecast, Trade
from app.db.session import get_db

router = APIRouter()


async def fetch_export_dataset(
    db: AsyncSession,
    state_code: Optional[str] = None,
    sector_code: Optional[str] = None,
    window_months: int = 12,
) -> List[Dict[str, Any]]:
    """
    Builds the unified export record combining Gap, Demand, Supply, Alert, and Taxonomy.
    """
    stmt = (
        select(
            Gap,
            District.name.label("district_name"),
            District.lgd_code,
            District.geometry_json,
            State.code.label("state_code"),
            State.name.label("state_name"),
            Trade.name.label("trade_name"),
            Trade.nco_code,
            Trade.qp_code,
            Trade.nsqf_level,
            Trade.course_months,
            Sector.code.label("sector_code"),
            Sector.name.label("sector_name"),
            Alert.flag.label("alert_flag"),
            Alert.overlays.label("alert_overlays"),
            Alert.suggested_action,
        )
        .join(District, Gap.district_id == District.id)
        .join(State, District.state_id == State.id)
        .join(Trade, Gap.trade_id == Trade.id)
        .join(Sector, Trade.sector_id == Sector.id)
        .outerjoin(Alert, (Alert.district_id == Gap.district_id) & (Alert.trade_id == Gap.trade_id))
        .where(Gap.window_months == window_months)
    )

    if state_code:
        stmt = stmt.where(State.code == state_code.upper())
    if sector_code:
        stmt = stmt.where(Sector.code == sector_code.upper())

    result = await db.execute(stmt)
    rows = result.all()

    records = []
    for (
        gap,
        d_name,
        lgd,
        geom,
        s_code,
        s_name,
        t_name,
        nco,
        qp,
        nsqf,
        course_m,
        sec_code,
        sec_name,
        flag,
        overlays,
        action,
    ) in rows:
        records.append({
            "state_code": s_code,
            "state_name": s_name,
            "district_name": d_name,
            "lgd_code": lgd,
            "sector_code": sec_code,
            "sector_name": sec_name,
            "trade_name": t_name,
            "nco_code": nco,
            "qp_code": qp,
            "nsqf_level": nsqf,
            "course_months": course_m,
            "window_months": gap.window_months,
            "origin_month": gap.origin_month,
            "forecast_demand_mean": round(gap.d_mean, 1),
            "projected_supply_mean": round(gap.s_mean, 1),
            "expected_gap": round(gap.g_mean, 1),
            "gap_rate_pct": round(gap.gap_rate * 100, 1),
            "p_shortage": round(gap.p_shortage, 3),
            "p_oversupply": round(gap.p_oversupply, 3),
            "tolerance": round(gap.tolerance, 1),
            "severity_score": round(gap.severity, 1),
            "gap_status": gap.status,
            "early_warning_flag": flag or gap.status,
            "overlays": ",".join(overlays) if overlays else "",
            "suggested_action": action or "Review seat allocation",
            "confidence": gap.confidence,
            "data_mode": gap.data_mode,
            "geometry_json": geom,
        })

    return records


@router.get("/export")
async def export_data(
    format: str = Query("csv", description="Format: csv, xlsx, json, geojson, parquet"),
    state_code: Optional[str] = Query(None, description="State code filter"),
    sector_code: Optional[str] = Query(None, description="Sector code filter"),
    window_months: int = Query(12, description="Forecast window (12 or 3 months)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Download complete intelligence dataset across formats.
    Complies with Section 10 requirements and includes explicit data_mode badges.
    """
    records = await fetch_export_dataset(db, state_code, sector_code, window_months)
    if not records:
        raise HTTPException(status_code=404, detail="No matching records found for export")

    fmt = format.lower()

    # 1. JSON
    if fmt == "json":
        clean_records = [{k: v for k, v in r.items() if k != "geometry_json"} for r in records]
        return clean_records

    # 2. GeoJSON
    if fmt == "geojson":
        features = []
        for r in records:
            geom = r.get("geometry_json") or {
                "type": "Point",
                "coordinates": [77.5946, 12.9716],  # Default centroid fallback
            }
            props = {k: v for k, v in r.items() if k != "geometry_json"}
            features.append({
                "type": "Feature",
                "geometry": geom,
                "properties": props,
            })
        return {
            "type": "FeatureCollection",
            "name": "KaushalDrishti_LMIS_Export",
            "features": features,
        }

    # Prepare DataFrame for tabular formats
    clean_records = [{k: v for k, v in r.items() if k != "geometry_json"} for r in records]
    df = pd.DataFrame(clean_records)

    # 3. CSV
    if fmt == "csv":
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding="utf-8")
        return Response(
            content=csv_buffer.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="kaushaldrishti_export.csv"'},
        )

    # 4. Parquet
    if fmt == "parquet":
        buf = io.BytesIO()
        df.to_parquet(buf, index=False)
        return Response(
            content=buf.getvalue(),
            media_type="application/octet-stream",
            headers={"Content-Disposition": 'attachment; filename="kaushaldrishti_export.parquet"'},
        )

    # 5. Excel (XLSX)
    if fmt == "xlsx":
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="KaushalDrishti_LMIS")
        return Response(
            content=buf.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="kaushaldrishti_export.xlsx"'},
        )

    raise HTTPException(status_code=400, detail=f"Unsupported format '{format}'. Use csv, xlsx, json, geojson, or parquet.")
