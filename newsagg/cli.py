"""Command line interface for NewsAgg."""

from __future__ import annotations

import argparse

from . import (
    __version__,
    PACKAGE_PATH,
    AGGREGATOR_PATH,
    BLOG_TEMPLATE_PATH,
    aggregate,
)


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
            f"(package: {PACKAGE_PATH}, aggregator: {AGGREGATOR_PATH}, "
            f"template: {BLOG_TEMPLATE_PATH})"
        ),
    )
    args = parser.parse_args()

    news = aggregate(args.top)
    for idx, item in enumerate(news, start=1):
        print(f"{idx}. [{item['source']}] {item['title']} - {item['link']}")


if __name__ == "__main__":
    main()
