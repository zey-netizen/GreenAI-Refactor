"""Formatter output: console berwarna + json."""

import json
from .detector import ScanResult

try:
    from colorama import Fore, Style, init as _cinit
    _cinit(autoreset=True)
    C = {"red": Fore.RED, "yellow": Fore.YELLOW, "green": Fore.GREEN,
         "cyan": Fore.CYAN, "bold": Style.BRIGHT, "reset": Style.RESET_ALL}
except ImportError:
    C = {k: "" for k in ("red", "yellow", "green", "cyan", "bold", "reset")}


def print_console(result: ScanResult):
    if not result.findings:
        print(f"{C['green']}✅ Tidak ada panggilan AI yang terdeteksi. Bersih!")
        return

    print(f"\n{C['bold']}🌱 GreenAI-Refactor — Hasil Scan{C['reset']}\n")
    current_file = None
    for f in result.findings:
        if f.file != current_file:
            current_file = f.file
            print(f"\n{C['bold']}📄 {f.file}{C['reset']}")
        if f.replaceable:
            print(f"  {C['yellow']}⚠️  Line {f.line}  [{f.provider}]{C['reset']}"
                  f"  ← bisa diganti kode biasa")
            print(f"      Kategori : {C['cyan']}{f.kategori}{C['reset']}")
            print(f"      Saran    : {C['green']}{f.saran}{C['reset']}")
        else:
            print(f"  {C['red']}●  Line {f.line}  [{f.provider}]{C['reset']}"
                  f"  (perlu review manual)")

    print(f"\n{C['bold']}Ringkasan:{C['reset']}")
    print(f"  Total file backend discan : {result.total_files}")
    print(f"  File berisi AI call       : {result.scanned_files}")
    print(f"  Total AI call             : {len(result.findings)}")
    print(f"  {C['green']}Bisa diganti kode biasa  : {result.replaceable_count}{C['reset']}")
    if result.findings:
        pct = 100 * result.replaceable_count / len(result.findings)
        print(f"  {C['green']}Potensi hemat             : {pct:.1f}% panggilan AI{C['reset']}")


def to_json(result: ScanResult) -> str:
    return json.dumps(
        {
            "summary": {
                "total_files": result.total_files,
                "files_with_ai": result.scanned_files,
                "total_ai_calls": len(result.findings),
                "replaceable": result.replaceable_count,
            },
            "findings": [
                {
                    "file": f.file, "line": f.line, "provider": f.provider,
                    "snippet": f.snippet, "kategori": f.kategori,
                    "saran": f.saran, "replaceable": f.replaceable,
                }
                for f in result.findings
            ],
        },
        indent=2, ensure_ascii=False,
    )
