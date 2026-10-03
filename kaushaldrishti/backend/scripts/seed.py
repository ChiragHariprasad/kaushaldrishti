"""
Seed reference data into the database.
Usage: python scripts/seed.py
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kaushaldrishti.seed")


def main():
    """Seed reference tables: states, districts, sectors, trades, sources."""
    logger.info("Seeding reference data...")
    logger.info("  → States, districts, sectors, trades (stub)")
    logger.info("Seed complete.")


if __name__ == "__main__":
    main()
