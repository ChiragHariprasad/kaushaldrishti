"""
Run backtests and generate performance reports.
Usage: python scripts/backtest.py
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kaushaldrishti.backtest")


def main():
    """Run rolling-origin backtests for all models."""
    logger.info("Running backtests...")
    logger.info("  → Baselines, LightGBM, ensemble (stub)")
    logger.info("Backtest complete. Results in docs/")


if __name__ == "__main__":
    main()
