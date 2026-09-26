import re

AI_CALL_PATTERNS = [
    (r"\bgenai\.GenerativeModel\b",              "Gemini SDK"),
    (r"\bgoogle\.generativeai\b",                "Gemini SDK"),
    (r"\bmodel\.generate_content\s*\(",          "Gemini API"),
    (r"\bopenai\.(ChatCompletion|Completion)\b", "OpenAI SDK"),
    (r"\bOpenAI\s*\(",                           "OpenAI SDK"),
    (r"\bclient\.chat\.completions\.create\b",   "OpenAI API"),
    (r"\banthropic\.Anthropic\b",                "Anthropic SDK"),
    (r"\bclient\.messages\.create\b",            "Anthropic API"),
    (r"\bcohere\.Client\b",                      "Cohere SDK"),
    (r"\bollama\.(chat|generate)\b",             "Ollama"),
    (r"generativelanguage\.googleapis\.com",     "Gemini REST"),
    (r"api\.openai\.com",                        "OpenAI REST"),
    (r"api\.anthropic\.com",                     "Anthropic REST"),
    (r"api\.cohere\.ai",                         "Cohere REST"),
]

REPLACEABLE_PROMPTS = [
    (r"\b(extract|ambil|tarik)\b.*\b(email|e-mail)\b",
     "Ekstraksi email", "re.findall(r'[\\w\\.-]+@[\\w\\.-]+', text)"),
    (r"\b(extract|ambil|tarik)\b.*\b(phone|telepon|nomor hp)\b",
     "Ekstraksi nomor telepon", "re.findall(r'(\\+?\\d[\\d\\s\\-]{7,}\\d)', text)"),
    (r"\b(extract|ambil|tarik)\b.*\b(url|link)\b",
     "Ekstraksi URL", "re.findall(r'https?://[^\\s]+', text)"),
    (r"\b(format|ubah|konversi)\b.*\b(json)\b",
     "Format ke JSON", "json.dumps(data, indent=2, ensure_ascii=False)"),
    (r"\b(format|ubah|konversi)\b.*\b(csv)\b",
     "Format ke CSV", "csv.writer / pandas.DataFrame.to_csv()"),
    (r"\b(uppercase|huruf besar|lowercase|huruf kecil)\b",
     "Ubah case teks", "text.upper() / text.lower()"),
    (r"\b(validate|validasi|cek)\b.*\b(email)\b",
     "Validasi email", "re.match(r'^[^@]+@[^@]+\\.[^@]+$', email)"),
    (r"\b(validate|validasi|cek)\b.*\b(url)\b",
     "Validasi URL", "urllib.parse.urlparse(url).scheme in ('http','https')"),
    (r"\b(slug|slugify)\b",
     "Buat slug", "re.sub(r'[^a-z0-9]+','-', text.lower()).strip('-')"),
    (r"\b(hitung|count|jumlah)\b.*\b(kata|word|karakter|char)\b",
     "Hitung kata/karakter", "len(text.split()) / len(text)"),
    (r"\b(sort|urutkan|urut)\b",
     "Urutkan data", "sorted(items) / sorted(items, key=lambda x: x['field'])"),
    (r"\b(trim|hapus)\b.*\b(whitespace|spasi)\b",
     "Trim whitespace", "text.strip() / re.sub(r'\\s+', ' ', text)"),
    (r"\b(parse|ekstrak)\b.*\b(tanggal|date)\b",
     "Parse tanggal", "datetime.strptime(s, '%Y-%m-%d') / dateutil.parser.parse(s)"),
    (r"\b(convert|konversi)\b.*\b(base64)\b",
     "Encode/decode base64", "base64.b64encode(data) / base64.b64decode(data)"),
    (r"\b(classify|klasifikasi|sentimen)\b.*\b(positive|negative|positif|negatif)\b",
     "Sentimen sederhana", "Gunakan lexicon (VADER / kamus kecil) — bukan LLM"),
    (r"\b(generate|buat)\b.*\b(uuid|id unik)\b",
     "Generate UUID", "uuid.uuid4()"),
    (r"\b(hash|hashkan)\b",
     "Hashing", "hashlib.sha256(text.encode()).hexdigest()"),
]

BACKEND_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".go", ".java", ".rb", ".php", ".rs",
}


def find_ai_calls(source: str):
    """Return list of (line_no, snippet, provider) untuk setiap AI call."""
    hits = []
    for i, line in enumerate(source.splitlines(), start=1):
        for pattern, provider in AI_CALL_PATTERNS:
            if re.search(pattern, line):
                hits.append((i, line.strip(), provider))
                break
    return hits


def classify_prompt(prompt_text: str):
    """Return (kategori, saran) kalau prompt termasuk 'sia-sia', else None."""
    low = prompt_text.lower()
    for pattern, kategori, saran in REPLACEABLE_PROMPTS:
        if re.search(pattern, low):
            return kategori, saran
    return None
