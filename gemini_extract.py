"""Extract structured road-closure events from multilingual news/social text.
Uses the Gemini API if GEMINI_API_KEY is set; otherwise falls back to a keyword rule so the demo still runs.
Set GEMINI_MODEL to override the default model alias.
"""
import json, os, re

PROMPT = """You extract road disruption events from news text (English, Hindi, Assamese or Bengali).
Return ONLY JSON with keys: road, location, status (closed|partially_open|open|unknown),
cause (landslide|flooding|protest_blockade|accident|construction|other|unknown),
expected_reopen (string or null), language. Do not guess missing fields; use unknown/null.
TEXT: {text}"""

KEYWORDS = {"landslide": ["landslide", "भूस्खलन", "ভূমিধস"], "flooding": ["flood", "बाढ़", "বন্যা"],
            "protest_blockade": ["blockade", "bandh", "ब्लॉकेड", "অবরোধ"], "accident": ["accident", "दुर्घटना"]}

def _fallback(text):
    cause = next((c for c, ks in KEYWORDS.items() if any(k in text.lower() for k in ks)), "unknown")
    closed = bool(re.search(r"closed|blocked|बंद|বন্ধ|ठप", text, re.I))
    return {"road": None, "location": None, "status": "closed" if closed else "unknown",
            "cause": cause, "expected_reopen": None, "language": "unknown", "source": "rule_fallback"}

def extract_event(text: str) -> dict:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return _fallback(text)
    try:
        from google import genai
        client = genai.Client(api_key=key)
        resp = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
            contents=PROMPT.format(text=text),
            config={"response_mime_type": "application/json"})
        out = json.loads(resp.text)
        out["source"] = "gemini"
        return out
    except Exception as e:  # never crash the product on an LLM failure
        out = _fallback(text)
        out["error"] = str(e)[:120]
        return out

SAMPLES = [
    "NH-37 near Noney remains closed after a landslide on Tuesday night; officials expect reopening by Thursday.",
    "भारी बारिश के कारण गुवाहाटी-शिलांग मार्ग पर भूस्खलन, यातायात आंशिक रूप से बहाल।",
    "Bandh called by a local group; vehicles stranded near Kohima, no timeline for reopening.",
]
if __name__ == "__main__":
    for s in SAMPLES:
        print(s[:60], "->", extract_event(s))
