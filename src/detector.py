"""Core scanner: walks a directory, finds backend files,
and detects AI API calls plus prompts that could be replaced."""

import os
import re
from dataclasses import dataclass, field
from typing import List

from .patterns import BACKEND_EXTENSIONS, find_ai_calls, classify_prompt


@dataclass
class Finding:
    file: str
    line: int
    provider: str
    snippet: str
    category: str = ""
    suggestion: str = ""

    @property
    def replaceable(self) -> bool:
        return bool(self.category)


@dataclass
class ScanResult:
    total_files: int = 0
    scanned_files: int = 0
    findings: List[Finding] = field(default_factory=list)

    @property
    def replaceable_count(self) -> int:
        return sum(1 for f in self.findings if f.replaceable)


# Regex to capture prompt string literals near an AI call
STRING_LITERAL = re.compile(r"""(['"])(?:\\.|(?!\1).){15,}\1""")


def _extract_prompts_near(lines: List[str], center: int, window: int = 3) -> str:
    """Collect string literals within `window` lines of `center`."""
    start = max(0, center - window)
    end = min(len(lines), center + window + 1)
    chunk = "\n".join(lines[start:end])
    return " ".join(m.group(0) for m in STRING_LITERAL.finditer(chunk))


def scan_file(path: str) -> List[Finding]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
    except OSError:
        return []

    lines = source.splitlines()
    findings: List[Finding] = []

    for line_no, snippet, provider in find_ai_calls(source):
        prompt_blob = _extract_prompts_near(lines, line_no - 1)
        classified = classify_prompt(prompt_blob)
        if classified:
            category, suggestion = classified
            findings.append(
                Finding(path, line_no, provider, snippet, category, suggestion)
            )
        else:
            findings.append(Finding(path, line_no, provider, snippet))

    return findings


def scan_directory(root: str) -> ScanResult:
    result = ScanResult()
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip common heavy folders
        dirnames[:] = [
            d for d in dirnames
            if d not in {"node_modules", ".git", "venv", ".venv",
                         "__pycache__", "dist", "build", ".next"}
        ]
        for name in filenames:
            if os.path.splitext(name)[1] not in BACKEND_EXTENSIONS:
                continue
            result.total_files += 1
            file_findings = scan_file(os.path.join(dirpath, name))
            if file_findings:
                result.scanned_files += 1
                result.findings.extend(file_findings)
    return result
