"""NewsAgg package initialization."""

import os

__version__ = "0.1.0"
PACKAGE_PATH = os.path.dirname(os.path.abspath(__file__))

from .aggregator import aggregate

__all__ = ["aggregate", "__version__", "PACKAGE_PATH"]
