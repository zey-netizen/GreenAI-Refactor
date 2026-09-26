#!/usr/bin/env python3
"""GreenAI-Refactor CLI.

Examples:
    python cli.py scan ./my-project
    python cli.py scan . --format json --out reports/scan.json
"""

import argparse
import sys
from pathlib import Path

from src.detector import scan_directory
from src import report


def main():
    parser = argparse.ArgumentParser(
        prog="greenai",
        description="Detect AI API calls that could be replaced with plain code.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_scan = sub.add_parser("scan", help="Scan a project directory")
    p_scan.add_argument("path", help="Path to the directory to scan")
    p_scan.add_argument("--format", choices=["console", "json"],
                        default="console", help="Output format")
    p_scan.add_argument("--out", help="Save output to a file (optional)")

    args = parser.parse_args()

    if args.cmd == "scan":
        path = Path(args.path).resolve()
        if not path.exists():
            print(f"Error: path not found: {path}", file=sys.stderr)
            sys.exit(1)

        result = scan_directory(str(path))

        if args.format == "console":
            report.print_console(result)
        elif args.format == "json":
            out = report.to_json(result)
            print(out)
            if args.out:
                Path(args.out).parent.mkdir(parents=True, exist_ok=True)
                Path(args.out).write_text(out, encoding="utf-8")


if __name__ == "__main__":
    main()
