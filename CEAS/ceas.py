#!/usr/bin/env python3
"""Unified ceas entry point supporting wig and bigwig formats.

Like :mod:`CEAS.sitepro`, this module delegates execution to legacy
implementations depending on the ``-f/--format`` option while passing
through any additional arguments.
"""
from __future__ import annotations

import argparse
import sys

from . import ceas_bigwig as _bigwig
from . import ceas_wig as _wig


def main(argv: list[str] | None = None) -> None:
    """Entry point for ceas with format selection."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "-f",
        "--format",
        default="bigwig",
        choices=["bigwig", "wig"],
        help="Input format: 'bigwig' (default) or 'wig'.",
    )
    fmt, rest = parser.parse_known_args(argv)

    sys.argv = [sys.argv[0]] + rest

    if fmt.format == "wig":
        _wig.main()
    else:
        _bigwig.main()


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
