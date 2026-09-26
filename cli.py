#!/usr/bin/env python3
"""GreenAI-Refactor CLI.

Contoh:
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
        description="Deteksi panggilan AI API yang bisa diganti kode biasa.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_scan = sub.add_parser("scan", help="Scan folder project")
    p_scan.add_argument("path", help="Path folder yang akan discan")
    p_scan.add_argument("--format", choices=["console", "json"],
                        default="console", help="Format output")
    p_scan.add_argument("--out", help="Simpan hasil ke file (opsional)")

    args = parser.parse_args()

    if args.cmd == "scan":
        path = Path(args.path).resolve()
        if not path.exists():
            print(f"❌ Path tidak ditemukan: {path}", file=sys.stderr)
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
