#!/usr/bin/env python3
"""Compatibility entry point for the canonical Markdown DOCX export."""

from __future__ import annotations

import runpy
from pathlib import Path
import sys


if __name__ == "__main__":
    exporter = Path(__file__).with_name("build_submission_exports.py")
    sys.argv = [str(exporter), "--format", "docx"]
    runpy.run_path(str(exporter), run_name="__main__")
