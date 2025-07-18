"""NewsAgg package initialization."""

import os

__version__ = "0.5.0"
PACKAGE_PATH = os.path.dirname(os.path.abspath(__file__))

BLOG_TEMPLATE_PATH = os.path.join(PACKAGE_PATH, "templates", "blog.html")

from .aggregator import aggregate, FILE_PATH as AGGREGATOR_PATH

__all__ = [
    "aggregate",
    "__version__",
    "PACKAGE_PATH",
    "AGGREGATOR_PATH",
    "BLOG_TEMPLATE_PATH",
]
