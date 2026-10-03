"""
Run rolling-origin backtests and generate performance reports and validation JSON.
Usage: python scripts/backtest.py
"""

import logging
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipelines.forecast.backtest import BacktestEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("kaushaldrishti.backtest_script")


def main():
    """Run rolling-origin backtests for all models."""
    logger.info("Initializing Backtest Engine (Layer 6)...")
    engine = BacktestEngine(
        horizons=[3, 6, 12],
        cutoffs=["2023-06", "2023-12"],
        data_path="data/synthetic/latent_demand.parquet",
    )
    
    logger.info("Running rolling-origin evaluation on panel dataset...")
    results = engine.run(sample_size=300)
    
    logger.info("Generating docs/BACKTESTS.md and data/synthetic/backtest_results.json...")
    engine.generate_markdown_report("docs/BACKTESTS.md")
    
    logger.info("[OK] Backtest completed successfully!")
    logger.info("Summary Results (80% Interval Coverage):")
    for h, m_dict in results["metrics"].items():
        logger.info(f"  Horizon {h}m - Ensemble: {m_dict['ensemble']['coverage_80']}% (Target: 80% +/- 5%)")


if __name__ == "__main__":
    main()
