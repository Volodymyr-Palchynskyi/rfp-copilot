import argparse
import asyncio
import logging

from evals import generation, retrieval


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m evals")
    parser.add_argument("suite", choices=["retrieval", "generation"])
    parser.add_argument("--set", dest="case_set", choices=["main", "heldout"], default="main")
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING)

    suite = retrieval if args.suite == "retrieval" else generation
    asyncio.run(suite.run(args.case_set))


if __name__ == "__main__":
    main()
