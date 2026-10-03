"""
Scheduled and CLI Data Exporter (Layer 8).
Exports complete intelligence records into CSV, XLSX, JSON, GeoJSON, and Parquet
to data/exports/ standing in for SFTP/S3 delivery.
Usage: python scripts/export.py
"""

import asyncio
import io
import json
import logging
from pathlib import Path
import pandas as pd
from sqlalchemy import select

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.models import Alert, District, Gap, Sector, State, Trade
from app.db.session import async_session_factory

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXPORT_DIR = REPO_ROOT / "data" / "exports"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("kaushaldrishti.export")


async def export_all_formats():
    """Build unified dataset and write all export formats."""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Querying canonical database for complete intelligence dataset...")

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
        .where(Gap.window_months == 12)
    )

    async with async_session_factory() as session:
        result = await session.execute(stmt)
        rows = result.all()

    logger.info(f"Loaded {len(rows)} records. Compiling export datasets...")

    records = []
    geojson_features = []

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
        row_dict = {
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
        }
        records.append(row_dict)

        feature_geom = geom or {"type": "Point", "coordinates": [77.5946, 12.9716]}
        geojson_features.append({
            "type": "Feature",
            "geometry": feature_geom,
            "properties": row_dict,
        })

    df = pd.DataFrame(records)

    # 1. CSV
    csv_file = EXPORT_DIR / "kaushaldrishti_lmis.csv"
    df.to_csv(csv_file, index=False, encoding="utf-8")
    logger.info(f"  [OK] Exported CSV to {csv_file} ({len(df)} rows)")

    # 2. Parquet
    parquet_file = EXPORT_DIR / "kaushaldrishti_lmis.parquet"
    df.to_parquet(parquet_file, index=False)
    logger.info(f"  [OK] Exported Parquet to {parquet_file}")

    # 3. JSON
    json_file = EXPORT_DIR / "kaushaldrishti_lmis.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    logger.info(f"  [OK] Exported JSON to {json_file}")

    # 4. GeoJSON
    geojson_file = EXPORT_DIR / "kaushaldrishti_lmis.geojson"
    geojson_doc = {
        "type": "FeatureCollection",
        "name": "KaushalDrishti_LMIS_Export",
        "features": geojson_features,
    }
    with open(geojson_file, "w", encoding="utf-8") as f:
        json.dump(geojson_doc, f, indent=2)
    logger.info(f"  [OK] Exported GeoJSON to {geojson_file}")

    # 5. Excel (XLSX)
    xlsx_file = EXPORT_DIR / "kaushaldrishti_lmis.xlsx"
    with pd.ExcelWriter(xlsx_file, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="KaushalDrishti_LMIS")
    logger.info(f"  [OK] Exported XLSX to {xlsx_file}")

    logger.info("[SUCCESS] Full scheduled export completed successfully!")


def main():
    asyncio.run(export_all_formats())


if __name__ == "__main__":
    main()
