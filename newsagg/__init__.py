"""NewsAgg package initialization."""

import os

__version__ = "0.7.1"
PACKAGE_PATH = os.path.dirname(os.path.abspath(__file__))

BLOG_TEMPLATE_PATH = os.path.join(PACKAGE_PATH, "templates", "blog.html")
BLOG_TEMPLATE_VERSION = "2.0"

CLI_PATH = os.path.join(PACKAGE_PATH, "cli.py")
CLI_VERSION = __version__

WEBAPP_PATH = os.path.join(PACKAGE_PATH, "webapp.py")
WEBAPP_VERSION = __version__

from .aggregator import (
    aggregate,
    FILE_PATH as AGGREGATOR_PATH,
    FILE_VERSION as AGGREGATOR_VERSION,
)

__all__ = [
    "aggregate",
    "__version__",
    "PACKAGE_PATH",
    "AGGREGATOR_PATH",
    "AGGREGATOR_VERSION",
    "BLOG_TEMPLATE_PATH",
    "BLOG_TEMPLATE_VERSION",
    "CLI_PATH",
    "CLI_VERSION",
    "WEBAPP_PATH",
    "WEBAPP_VERSION",
]
