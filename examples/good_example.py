"""Clean version - no AI API, same results, free and instant."""
import json
import re


def extract_emails(text: str) -> list[str]:
    return re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text)


def to_json(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def count_words(text: str) -> int:
    return len(text.split())
