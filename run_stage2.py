from __future__ import annotations

import argparse
import json

from stage2.service import NavigationService


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Stage II semantic indoor navigation queries")
    parser.add_argument("--detection-dir", default="detection_results")
    parser.add_argument("--db-path", default="stage2_navigation.db")
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("query", help="Natural-language query, e.g. 'Where is the nearest painting?'")
    args = parser.parse_args()

    service = NavigationService(args.detection_dir, args.db_path)
    service.initialize(rebuild=args.rebuild)
    response = service.query(args.query)
    print(json.dumps(response.model_dump(), indent=2))


if __name__ == "__main__":
    main()
