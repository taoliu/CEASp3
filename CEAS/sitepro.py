#!/usr/bin/env python3
"""Unified sitepro entry point supporting wig and bigwig formats.

This module dispatches to the legacy implementations based on the
``-f/--format`` option. All remaining arguments are passed through to the
selected backend.
"""
from __future__ import annotations

import argparse
import sys

from . import sitepro_bigwig as _bigwig
from . import sitepro_wig as _wig

# Re-export dump for external use and tests
from .sitepro_bigwig import dump  # noqa: F401


def main(argv: list[str] | None = None) -> None:
    """Entry point for sitepro.

    Parameters
    ----------
    argv:
        Optional list of arguments to parse.  If ``None`` (default), ``sys.argv``
        is used.
    """
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

    # Replace sys.argv so that downstream option parsers see the remaining args
    sys.argv = [sys.argv[0]] + rest

    if fmt.format == "wig":
        _wig.main()
    else:
        _bigwig.main()


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
