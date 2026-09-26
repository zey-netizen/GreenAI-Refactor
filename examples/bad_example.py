"""Example of API-heavy code - everything below can be plain code."""
import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_KEY"])
model = genai.GenerativeModel("gemini-pro")


def extract_emails(text: str) -> list[str]:
    # Wasteful API call - regex would do the same job
    prompt = "Extract all email addresses from this text: " + text
    resp = model.generate_content(prompt)
    return resp.text.split(",")


def to_json(data: dict) -> str:
    # Wasteful API call - json.dumps is enough
    prompt = "Format this data as JSON: " + str(data)
    return model.generate_content(prompt).text


def count_words(text: str) -> int:
    # Wasteful API call - len(text.split()) is enough
    prompt = "Count words in this text: " + text
    return int(model.generate_content(prompt).text.strip())
