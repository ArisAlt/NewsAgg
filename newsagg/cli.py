"""Command line interface for NewsAgg."""

from __future__ import annotations

import argparse

from . import (
    __version__,
    PACKAGE_PATH,
    AGGREGATOR_PATH,
    AGGREGATOR_VERSION,
    BLOG_TEMPLATE_PATH,
    BLOG_TEMPLATE_VERSION,
    CLI_PATH,
    CLI_VERSION,
    WEBAPP_PATH,
    WEBAPP_VERSION,
    aggregate,
)

import os

FILE_PATH = os.path.abspath(__file__)
FILE_VERSION = CLI_VERSION


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate popular Greek news")
    parser.add_argument(
        "-n", "--top", type=int, default=10, help="number of items per source"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=(
            f"NewsAgg {__version__} "
            f"(package: {PACKAGE_PATH}, "
            f"CLI: {CLI_PATH} v{CLI_VERSION}, "
            f"webapp: {WEBAPP_PATH} v{WEBAPP_VERSION}, "
            f"aggregator: {AGGREGATOR_PATH} v{AGGREGATOR_VERSION}, "
            f"template: {BLOG_TEMPLATE_PATH} v{BLOG_TEMPLATE_VERSION})"
        ),
    )
    args = parser.parse_args()

    news = aggregate(args.top)
    for idx, item in enumerate(news, start=1):
        print(f"{idx}. [{item['source']}] {item['title']} - {item['link']}")
        if item.get("preview"):
            print(f"    {item['preview']}")


if __name__ == "__main__":
    main()
