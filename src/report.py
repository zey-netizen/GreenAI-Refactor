"""Output formatters: colored console output + JSON."""

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
        print(f"{C['green']}OK - No AI calls detected. Clean!")
        return

    print(f"\n{C['bold']}GreenAI-Refactor - Scan Results{C['reset']}\n")
    current_file = None
    for f in result.findings:
        if f.file != current_file:
            current_file = f.file
            print(f"\n{C['bold']}{f.file}{C['reset']}")
        if f.replaceable:
            print(f"  {C['yellow']}[!] Line {f.line}  [{f.provider}]{C['reset']}"
                  f"  <- replaceable with plain code")
            print(f"      Category   : {C['cyan']}{f.category}{C['reset']}")
            print(f"      Suggestion : {C['green']}{f.suggestion}{C['reset']}")
        else:
            print(f"  {C['red']}[ ] Line {f.line}  [{f.provider}]{C['reset']}"
                  f"  (manual review needed)")

    print(f"\n{C['bold']}Summary:{C['reset']}")
    print(f"  Total backend files scanned : {result.total_files}")
    print(f"  Files with AI calls         : {result.scanned_files}")
    print(f"  Total AI calls              : {len(result.findings)}")
    print(f"  {C['green']}Replaceable with plain code : {result.replaceable_count}{C['reset']}")
    if result.findings:
        pct = 100 * result.replaceable_count / len(result.findings)
        print(f"  {C['green']}Potential savings           : {pct:.1f}% of AI calls{C['reset']}")


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
                    "snippet": f.snippet, "category": f.category,
                    "suggestion": f.suggestion, "replaceable": f.replaceable,
                }
                for f in result.findings
            ],
        },
        indent=2, ensure_ascii=False,
    )
