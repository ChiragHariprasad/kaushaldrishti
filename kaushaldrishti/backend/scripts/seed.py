"""
Seeds canonical reference data into the database:
- States (KA, TN, UP)
- Districts (144 districts)
- Sectors (5 sectors)
- Trades (40 trades with nco_verified=False)
- Sources (ncs, portal, plfs, eshram, udyam)
"""

import asyncio
import csv
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select
from app.db.session import engine, async_session_factory, Base
from app.db.models import State, District, Sector, Trade, Source


REFERENCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "reference"))


SOURCES_INIT = [
    {
        "id": "ncs",
        "name": "National Career Service",
        "nominal_update_days": 30,
        "independence_group": "government_vacancy",
        "licence": "Government Open Data",
        "access_mode": "live",
    },
    {
        "id": "portal",
        "name": "Job Portal Aggregate",
        "nominal_update_days": 7,
        "independence_group": "portal",
        "licence": "Aggregated Partner Data",
        "access_mode": "partner",
    },
    {
        "id": "plfs",
        "name": "Periodic Labour Force Survey",
        "nominal_update_days": 90,
        "independence_group": "government_survey",
        "licence": "Official Statistics",
        "access_mode": "public_aggregate",
    },
    {
        "id": "eshram",
        "name": "e-Shram Portal",
        "nominal_update_days": 30,
        "independence_group": "government_registry",
        "licence": "Official Aggregate Registry",
        "access_mode": "public_aggregate",
    },
    {
        "id": "udyam",
        "name": "Udyam Leading Indicators",
        "nominal_update_days": 60,
        "independence_group": "government_enterprise",
        "licence": "Enterprise Registry Aggregates",
        "access_mode": "public_aggregate",
    },
]


async def seed_all():
    print("[INFO] Creating database schema tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # 1. Sources
        for src in SOURCES_INIT:
            existing = await session.get(Source, src["id"])
            if not existing:
                session.add(Source(**src))
        await session.commit()
        print(f"[OK] Seeded {len(SOURCES_INIT)} sources.")

        # 2. States & Districts from lgd_districts.csv
        districts_file = os.path.join(REFERENCE_DIR, "lgd_districts.csv")
        state_cache = {}

        with open(districts_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                s_code = row["state_code"]
                s_name = row["state_name"]
                if s_code not in state_cache:
                    stmt = select(State).where(State.code == s_code)
                    res = await session.execute(stmt)
                    st_obj = res.scalar_one_or_none()
                    if not st_obj:
                        st_obj = State(code=s_code, name=s_name)
                        session.add(st_obj)
                        await session.flush()
                    state_cache[s_code] = st_obj

                lgd = row["lgd_code"]
                stmt = select(District).where(District.lgd_code == lgd)
                res = await session.execute(stmt)
                d_obj = res.scalar_one_or_none()
                if not d_obj:
                    session.add(
                        District(
                            lgd_code=lgd,
                            state_id=state_cache[s_code].id,
                            name=row["district_name"],
                            population_working_age=int(row["population_working_age"]),
                            urban_rural_aspirational=row["urban_rural_aspirational"],
                            name_variants={"en": row["district_name"]},
                        )
                    )

        await session.commit()
        print("[OK] Seeded States and 144 Districts.")

        # 3. Sectors & Trades from trades_master.csv
        trades_file = os.path.join(REFERENCE_DIR, "trades_master.csv")
        sector_cache = {}

        with open(trades_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sec_code = row["sector_code"]
                sec_name = row["sector_name"]
                if sec_code not in sector_cache:
                    stmt = select(Sector).where(Sector.code == sec_code)
                    res = await session.execute(stmt)
                    sec_obj = res.scalar_one_or_none()
                    if not sec_obj:
                        sec_obj = Sector(code=sec_code, name=sec_name)
                        session.add(sec_obj)
                        await session.flush()
                    sector_cache[sec_code] = sec_obj

                t_name = row["trade_name"]
                stmt = select(Trade).where(Trade.name == t_name)
                res = await session.execute(stmt)
                t_obj = res.scalar_one_or_none()
                if not t_obj:
                    aliases = row["aliases_pipe"].split("|") if row["aliases_pipe"] else []
                    patterns = row["patterns_pipe"].split("|") if row["patterns_pipe"] else []
                    session.add(
                        Trade(
                            sector_id=sector_cache[sec_code].id,
                            name=t_name,
                            nco_code=row["nco_code"],
                            nco_verified=False,  # Indicative code, verified=false
                            qp_code=row["qp_code"],
                            nsqf_level=int(row["nsqf_level"]),
                            course_months=int(row["course_months"]),
                            aliases=aliases,
                            title_patterns=patterns,
                        )
                    )

        await session.commit()
        print("[OK] Seeded 5 Sectors and 40 Trades.")

    print("[SUCCESS] All reference tables seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed_all())
