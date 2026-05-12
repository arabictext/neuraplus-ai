#!/usr/bin/env python3
"""
Blog Image Generator v4
========================
- Scans blog/ folder for ALL .html posts
- Skips any post that already has an image in assets/images/blog/
- On re-run: only processes remaining posts (safe to run multiple times)
- Commits every 10 images so work is saved even if job times out
"""

import os, re, time, urllib.request, urllib.parse, hashlib, subprocess
from pathlib import Path

BLOG_DIR    = "blog"
IMAGES_DIR  = "assets/images/blog"
SITE_URL    = "https://neuraplus-ai.github.io"
IMAGE_WIDTH  = 1200
IMAGE_HEIGHT = 630
DELAY        = 4   # seconds between API calls
COMMIT_EVERY = 10  # save progress every N images (so timeout doesn't lose work)

SKIP_NAMES = ["index", "404", "about", "contact", "privacy", "sitemap", "terms"]


def get_all_posts():
    blog_path = Path(BLOG_DIR)
    posts = []
    for f in sorted(blog_path.glob("*.html")):
        if any(f.stem.lower().startswith(s) for s in SKIP_NAMES):
            continue
        posts.append(f)
    return posts


def already_has_image(slug):
    """Check if image file already exists and is valid."""
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        p = Path(IMAGES_DIR) / f"{slug}{ext}"
        if p.exists() and p.stat().st_size > 8000:
            return True
    return False


def get_title(content, slug):
    m = re.search(r"<title>([^<]+)</title>", content, re.I)
    if m:
        t = m.group(1)
        t = re.sub(r"\s*[–—|-]\s*(NeuraPlusAI|NeuraPulse).*$", "", t, flags=re.I)
        return t.strip()
    return slug.replace("-", " ").title()


def build_prompt(title, content):
    text = (title + " " + content[:300]).lower()

    topics = [
        (["python","javascript","code","programming","developer","api","prompt","claude","gpt","llm","anthropic"],
         "developer laptop with code on screen, dark IDE, programming workspace, tech desk setup"),
        (["groq","lpu","gpu","chip","hardware","inference","latency","benchmark"],
         "AI semiconductor chip circuit board, fast computing hardware, data center technology"),
        (["ai","artificial intelligence","machine learning","neural","deep learning","automation"],
         "abstract AI neural network, glowing data streams, futuristic technology, blue purple gradient"),
        (["seo","google","search","ranking","keyword","traffic","marketing","blog"],
         "SEO analytics dashboard, search ranking chart going up, digital marketing concept"),
        (["n8n","zapier","workflow","automate","automation","pipeline","integration"],
         "automation workflow diagram, connected app nodes, no-code visual workflow builder"),
        (["perplexity","search engine","research","citation","academic"],
         "AI search interface, research papers, citations, modern search dashboard"),
        (["ollama","local","private","offline","self-hosted","open source model"],
         "local AI running on laptop, private offline computing, terminal command line"),
        (["elevenlabs","voice","speech","audio","tts","clone","podcast"],
         "voice AI audio waveform, microphone, sound studio, speech technology"),
        (["deepl","translate","translation","language","multilingual"],
         "language translation concept, globe with text, multilingual documents"),
        (["coreweave","aws","cloud","gpu","kubernetes","deploy","server"],
         "cloud computing server room, GPU clusters, modern data center infrastructure"),
        (["finance","money","invest","crypto","bitcoin","budget","revenue"],
         "financial technology concept, charts and graphs, modern fintech dashboard"),
        (["startup","business","entrepreneur","saas","growth","strategy"],
         "modern startup concept, growth chart trending up, professional business environment"),
    ]

    style = "professional editorial blog header, modern clean design, vibrant colors"
    for keywords, visual in topics:
        if any(k in text for k in keywords):
            style = visual
            break

    return (
        f"{style}, topic: {title[:70]}, "
        f"wide 1200x630 banner, high quality sharp image, "
        f"no text, no watermark, no logo, no people holding papers"
    )[:480]


def download_image(slug, prompt):
    save_path = Path(IMAGES_DIR) / f"{slug}.jpg"
    Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)

    encoded = urllib.parse.quote(prompt)
    seed = int(hashlib.md5(slug.encode()).hexdigest()[:8], 16) % 99999
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}"
        f"&seed={seed}&nologo=true&enhance=true&model=flux"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NeuraPlusAI/4.0"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = resp.read()
        if len(data) < 8000:
            print(f"   ⚠️  Too small ({len(data)}B)")
            return False
        save_path.write_bytes(data)
        print(f"   ✅ {len(data)//1024}KB → {save_path}")
        return True
    except Exception as e:
        print(f"   ❌ {e}")
        return False


def inject_into_post(filepath, slug, title):
    img_web = f"/{IMAGES_DIR}/{slug}.jpg"
    img_abs = f"{SITE_URL}{img_web}"

    content = filepath.read_text(encoding="utf-8", errors="ignore")

    # Update og:image
    if "meta-og:image" in content:
        content = re.sub(r"(meta-og:image:\s*).*", f"\\1{img_abs}", content)
    # Update twitter:image
    if "meta-twitter:image" in content:
        content = re.sub(r"(meta-twitter:image:\s*).*", f"\\1{img_abs}", content)

    # Inject hero image if not already present
    if img_web not in content:
        alt = title
        hero = (
            f'\n<img src="{img_web}" alt="{alt}" title="{alt}" '
            f'class="blog-hero-image" width="1200" height="630" loading="lazy" '
            f'style="width:100%;max-width:1200px;height:auto;'
            f'border-radius:8px;margin:0 auto 2rem;display:block;" />\n'
        )
        h1 = re.search(r"(<h1[^>]*>.*?</h1>)", content, re.I | re.S)
        if h1:
            content = content[:h1.end()] + hero + content[h1.end():]
        else:
            art = re.search(r"(<(?:article|main|body)[^>]*>)", content, re.I)
            if art:
                content = content[:art.end()] + hero + content[art.end():]

    filepath.write_text(content, encoding="utf-8")


def commit_progress(count):
    """Commit every N images so work isn't lost if job times out."""
    try:
        subprocess.run(["git", "add", IMAGES_DIR, BLOG_DIR], check=False)
        result = subprocess.run(
            ["git", "diff", "--staged", "--quiet"], capture_output=True
        )
        if result.returncode != 0:  # there are changes
            subprocess.run([
                "git", "commit", "-m",
                f"🖼️ Progress: saved {count} images [skip ci]"
            ], check=False)
            print(f"   💾 Progress committed ({count} images saved)\n")
    except Exception as e:
        print(f"   ⚠️  Could not commit progress: {e}")


def main():
    run_mode = os.environ.get("RUN_MODE", "remaining")
    posts = get_all_posts()

    if not posts:
        print("⚠️  No posts found in blog/ folder")
        return

    # Filter based on mode
    if run_mode == "remaining":
        todo = [p for p in posts if not already_has_image(p.stem)]
        print(f"📊 Total posts : {len(posts)}")
        print(f"✅ Already done: {len(posts) - len(todo)}")
        print(f"⏳ Remaining   : {len(todo)}")
    else:
        todo = posts
        print(f"📊 Processing all {len(posts)} posts")

    if not todo:
        print("\n🎉 All posts already have images!")
        return

    print(f"🚀 Starting...\n")

    ok = fail = 0

    for i, filepath in enumerate(todo, 1):
        slug = filepath.stem
        print(f"[{i}/{len(todo)}] {slug}")

        content = filepath.read_text(encoding="utf-8", errors="ignore")
        title   = get_title(content, slug)
        prompt  = build_prompt(title, content)

        print(f"   📝 {title}")

        success = download_image(slug, prompt)
        if success:
            inject_into_post(filepath, slug, title)
            ok += 1
        else:
            fail += 1

        # Save progress every COMMIT_EVERY images
        if ok % COMMIT_EVERY == 0 and ok > 0:
            commit_progress(ok)

        time.sleep(DELAY)

    print(f"\n{'='*50}")
    print(f"✅ Generated : {ok}")
    print(f"❌ Failed    : {fail}")
    print(f"{'='*50}")


if __name__ == "__main__":
    # Setup git identity for progress commits
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=False)
    subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], check=False)
    main()
