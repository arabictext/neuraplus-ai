import requests
from datetime import datetime

SITE = "neuraplus-ai.github.io"
IMAGES = [
    "groq-ai-vs-gemini-latency",
    "perplexity-ai-vs-google-search",
    "claude-ai-robot-automation-2026"
]

print(f"🔍 Image Check - {datetime.now()}")
print("=" * 50)

for img in IMAGES:
    query = f"site:{SITE} {img.replace('-', ' ')}"
    url = f"https://www.google.com/search?tbm=isch&q={query}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    
    if SITE in r.text:
        print(f"✅ {img}: INDEXED")
    else:
        print(f"⏳ {img}: Not yet")
