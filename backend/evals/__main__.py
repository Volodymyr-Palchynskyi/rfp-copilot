import argparse
import asyncio
import logging

from evals import generation, retrieval


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m evals")
    parser.add_argument("suite", choices=["retrieval", "generation"])
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING)

    suite = retrieval if args.suite == "retrieval" else generation
    asyncio.run(suite.run())


if __name__ == "__main__":
    main()
