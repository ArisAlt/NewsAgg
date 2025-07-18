"""NewsAgg package initialization."""

import os

__version__ = "0.4.0"
PACKAGE_PATH = os.path.dirname(os.path.abspath(__file__))

from .aggregator import aggregate, FILE_PATH as AGGREGATOR_PATH

__all__ = ["aggregate", "__version__", "PACKAGE_PATH", "AGGREGATOR_PATH"]
