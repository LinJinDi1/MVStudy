"""Compatibility import for callers of the standalone prototype."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "backend"))
from mvstudy.domains.review import review_source

__all__ = ["review_source"]
