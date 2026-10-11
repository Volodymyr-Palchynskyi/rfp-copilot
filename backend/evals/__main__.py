import argparse
import asyncio
import logging

from app.core.config import settings
from evals import generation, retrieval
from evals.common import COMBINED_MIN_SIMILARITY


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m evals")
    parser.add_argument("suite", choices=["retrieval", "generation"])
    parser.add_argument("--set", dest="case_set", choices=["main", "heldout", "fresh", "fresh2"], default="main")
    parser.add_argument(
        "--selection", choices=["threshold", "rerank", "combined"], default="rerank",
        help="how references are chosen: similarity threshold only, LLM judge alone, or judge AND similarity floor",
    )
    parser.add_argument("--no-rerank", action="store_true", help="alias for --selection threshold")
    parser.add_argument(
        "--modes", choices=["both", "rag", "baseline"], default="both",
        help="generation only: skip the no-RAG baseline (it does not depend on the selection rule) to save quota",
    )
    args = parser.parse_args()

    selection = "threshold" if args.no_rerank else args.selection
    # Must happen before the services are constructed.
    if selection == "threshold":
        settings.RERANK_ENABLED = False
    elif selection == "combined":
        settings.RERANK_REQUIRE_SIMILARITY = COMBINED_MIN_SIMILARITY
    logging.basicConfig(level=logging.WARNING)

    variant = "" if selection == "rerank" else selection
    if args.suite == "retrieval":
        asyncio.run(retrieval.run(args.case_set, variant=variant))
    else:
        if args.modes == "baseline":
            variant = "baseline"
        asyncio.run(generation.run(args.case_set, variant=variant, modes=args.modes))


if __name__ == "__main__":
    main()
