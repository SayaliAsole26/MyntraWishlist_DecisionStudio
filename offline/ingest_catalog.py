"""CLI: python -m offline.ingest_catalog"""

import argparse
import json
import sys

from offline.ingestion.pipeline import ingest_catalog
from offline.ingestion.validate import ValidationError


def main() -> int:
    parser = argparse.ArgumentParser(description="Load seed JSON into SQLite catalog tables.")
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Override data/ directory (default: project data/)",
    )
    args = parser.parse_args()

    try:
        result = ingest_catalog(
            data_dir=args.data_dir,
        )
    except ValidationError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"Missing seed file: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Invalid seed data: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
