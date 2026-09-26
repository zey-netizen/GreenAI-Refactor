"""Patterns for detecting AI API calls and prompts
that could be replaced with plain deterministic code."""

import re

# -----------------------------------------------------------------
# 0. Setup patterns — SDK configuration lines, NOT actual AI calls.
#    These are skipped during detection.
# -----------------------------------------------------------------
SETUP_PATTERNS = [
    r"genai\.configure\s*\(",
    r"GenerativeModel\s*\(",
    r"openai\.api_key\s*=",
    r"client\s*=\s*OpenAI\s*\(",
    r"client\s*=\s*Anthropic\s*\(",
    r"anthropic\.api_key\s*=",
    r"cohere\.Client\s*\(",
    r"^import\s+google\.generativeai",
    r"^from\s+google\s+import\s+generativeai",
    r"^import\s+openai",
    r"^from\s+openai\s+import",
    r"^import\s+anthropic",
    r"^from\s+anthropic\s+import",
]

# -----------------------------------------------------------------
# 1. Detection patterns for AI provider SDKs / HTTP calls
# -----------------------------------------------------------------
AI_CALL_PATTERNS = [
    # Python SDKs (actual calls only, not setup)
    (r"\b\w+\.generate_content\s*\(",            "Gemini API"),
    (r"\b\w+\.generate_content_async\s*\(",      "Gemini API"),
    (r"\bopenai\.(ChatCompletion|Completion)\b", "OpenAI SDK"),
    (r"\bclient\.chat\.completions\.create\b",   "OpenAI API"),
    (r"\bclient\.messages\.create\b",            "Anthropic API"),
    (r"\bollama\.(chat|generate)\b",             "Ollama"),

    # Direct REST endpoints
    (r"generativelanguage\.googleapis\.com",     "Gemini REST"),
    (r"api\.openai\.com",                        "OpenAI REST"),
    (r"api\.anthropic\.com",                     "Anthropic REST"),
    (r"api\.cohere\.ai",                         "Cohere REST"),
]

# -----------------------------------------------------------------
# 2. "Wasteful" prompt patterns — replaceable with plain code.
#    Format: (regex in prompt, category, suggested replacement)
# -----------------------------------------------------------------
REPLACEABLE_PROMPTS = [
    (r"\b(extract|ambil|tarik)\b.*\b(email|e-mail)\b",
     "Email extraction", "re.findall(r'[\\w\\.-]+@[\\w\\.-]+', text)"),
    (r"\b(extract|ambil|tarik)\b.*\b(phone|telepon|nomor hp)\b",
     "Phone number extraction", "re.findall(r'(\\+?\\d[\\d\\s\\-]{7,}\\d)', text)"),
    (r"\b(extract|ambil|tarik)\b.*\b(url|link)\b",
     "URL extraction", "re.findall(r'https?://[^\\s]+', text)"),
    (r"\b(format|ubah|konversi)\b.*\b(json)\b",
     "JSON formatting", "json.dumps(data, indent=2, ensure_ascii=False)"),
    (r"\b(format|ubah|konversi)\b.*\b(csv)\b",
     "CSV formatting", "csv.writer / pandas.DataFrame.to_csv()"),
    (r"\b(uppercase|huruf besar|lowercase|huruf kecil)\b",
     "Case conversion", "text.upper() / text.lower()"),
    (r"\b(validate|validasi|cek)\b.*\b(email)\b",
     "Email validation", "re.match(r'^[^@]+@[^@]+\\.[^@]+$', email)"),
    (r"\b(validate|validasi|cek)\b.*\b(url)\b",
     "URL validation", "urllib.parse.urlparse(url).scheme in ('http','https')"),
    (r"\b(slug|slugify)\b",
     "Slug generation", "re.sub(r'[^a-z0-9]+','-', text.lower()).strip('-')"),

    # Word / character counting — support both EN and ID word orders
    (r"\bcount\b.*\bwords?\b",
     "Word counting", "len(text.split())"),
    (r"\bcount\b.*\b(characters?|chars?|letters?)\b",
     "Character counting", "len(text)"),
    (r"\b(hitung|jumlah)\b.*\b(kata|word)\b",
     "Word counting", "len(text.split())"),
    (r"\b(hitung|jumlah)\b.*\b(karakter|char)\b",
     "Character counting", "len(text)"),
    (r"\b(word|kata)\s*(count|counts|counting)\b",
     "Word counting", "len(text.split())"),
    (r"\b(character|char)\s*(count|counts|counting)\b",
     "Character counting", "len(text)"),

    (r"\b(sort|urutkan|urut)\b",
     "Sorting data", "sorted(items) / sorted(items, key=lambda x: x['field'])"),
    (r"\b(trim|hapus)\b.*\b(whitespace|spasi)\b",
     "Whitespace trimming", "text.strip() / re.sub(r'\\s+', ' ', text)"),
    (r"\b(parse|ekstrak)\b.*\b(tanggal|date)\b",
     "Date parsing", "datetime.strptime(s, '%Y-%m-%d') / dateutil.parser.parse(s)"),
    (r"\b(convert|konversi)\b.*\b(base64)\b",
     "Base64 encode/decode", "base64.b64encode(data) / base64.b64decode(data)"),
    (r"\b(classify|klasifikasi|sentimen)\b.*\b(positive|negative|positif|negatif)\b",
     "Simple sentiment", "Use a lexicon (VADER / small dictionary) — not an LLM"),
    (r"\b(generate|buat)\b.*\b(uuid|id unik)\b",
     "UUID generation", "uuid.uuid4()"),
    (r"\b(hash|hashkan)\b",
     "Hashing", "hashlib.sha256(text.encode()).hexdigest()"),
]

# -----------------------------------------------------------------
# 3. Backend file extensions to scan
# -----------------------------------------------------------------
BACKEND_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".go", ".java", ".rb", ".php", ".rs",
}


def find_ai_calls(source: str):
    """Return a list of (line_no, snippet, provider) for every AI call."""
    hits = []
    for i, line in enumerate(source.splitlines(), start=1):
        # Skip SDK setup / configuration / import lines
        if any(re.search(p, line) for p in SETUP_PATTERNS):
            continue
        for pattern, provider in AI_CALL_PATTERNS:
            if re.search(pattern, line):
                hits.append((i, line.strip(), provider))
                break
    return hits


def classify_prompt(prompt_text: str):
    """Return (category, suggestion) if the prompt is 'wasteful', else None."""
    low = prompt_text.lower()
    for pattern, category, suggestion in REPLACEABLE_PROMPTS:
        if re.search(pattern, low):
            return category, suggestion
    return None
