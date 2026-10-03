"""
Export data to local folder.
Usage: python scripts/export.py
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kaushaldrishti.export")


def main():
    """Export demand indices, forecasts, gaps, and alerts."""
    logger.info("Exporting data...")
    logger.info("  → CSV, XLSX, JSON, GeoJSON, Parquet (stub)")
    logger.info("Export complete. Files in data/exports/")


if __name__ == "__main__":
    main()
