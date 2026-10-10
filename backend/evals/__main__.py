import argparse
import asyncio
import logging

from app.core.config import settings
from evals import generation, retrieval


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m evals")
    parser.add_argument("suite", choices=["retrieval", "generation"])
    parser.add_argument("--set", dest="case_set", choices=["main", "heldout", "fresh"], default="main")
    parser.add_argument("--no-rerank", action="store_true", help="select references by similarity threshold only")
    args = parser.parse_args()
    if args.no_rerank:
        settings.RERANK_ENABLED = False  # must happen before the services are constructed
    logging.basicConfig(level=logging.WARNING)

    suite = retrieval if args.suite == "retrieval" else generation
    asyncio.run(suite.run(args.case_set, variant="threshold" if args.no_rerank else ""))


if __name__ == "__main__":
    main()
