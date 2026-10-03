"""
Export OpenAPI specification to a file.
Usage: python scripts/export_openapi.py
"""

import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kaushaldrishti.openapi")


def main():
    """Export the OpenAPI spec from the FastAPI app."""
    from app.main import app

    spec = app.openapi()
    output_path = "docs/openapi.json"

    with open(output_path, "w") as f:
        json.dump(spec, f, indent=2)

    logger.info(f"OpenAPI spec exported to {output_path}")
    logger.info(f"  Endpoints: {len(spec.get('paths', {}))}")


if __name__ == "__main__":
    main()
