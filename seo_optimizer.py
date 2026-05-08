"""
seo_optimizer.py
Automatically adds/fixes:
  - <title>
  - <meta name="description">
  - <meta name="keywords">
  - Open Graph tags (og:title, og:description, og:url, og:image, og:type)
  - Twitter Card tags
  - JSON-LD Schema (WebSite / WebPage / BlogPosting)
  - Canonical URL
  - robots meta
  - charset + viewport (if missing)
"""

import os
import glob
import re
from bs4 import BeautifulSoup

# ─── CONFIG ───────────────────────────────────────────────────────────────────
SITE_URL    = "https://neuraplus-ai.github.io"
SITE_NAME   = "NeuraPlusAI"
OG_IMAGE    = f"{SITE_URL}/favicon.svg"   # change to a real 1200x630 image if you have one
TWITTER_HANDLE = "@neuraplus_ai"          # change or remove if not applicable

# Per-page SEO data — add your pages here
PAGE_SEO = {
    "index.html": {
        "title": "NeuraPlusAI – AI-Powered Tools for Everyone",
        "description": "NeuraPlusAI offers cutting-edge artificial intelligence tools to boost productivity, creativity, and automation for individuals and businesses.",
        "keywords": "AI tools, artificial intelligence, automation, productivity, NeuraPlusAI",
        "schema_type": "WebSite",
    },
    "about.html": {
        "title": "About NeuraPlusAI – Our Mission & Team",
        "description": "Learn about NeuraPlusAI's mission to democratize artificial intelligence and the passionate team behind our AI-powered platform.",
        "keywords": "about NeuraPlusAI, AI mission, AI team, artificial intelligence company",
        "schema_type": "WebPage",
    },
    "contact.html": {
        "title": "Contact NeuraPlusAI – Get in Touch",
        "description": "Have questions or feedback? Contact the NeuraPlusAI team. We'd love to hear from you and help you with your AI journey.",
        "keywords": "contact NeuraPlusAI, AI support, get in touch, AI help",
        "schema_type": "WebPage",
    },
    "blog.html": {
        "title": "NeuraPlusAI Blog – AI News, Tips & Insights",
        "description": "Explore the NeuraPlusAI blog for the latest articles on artificial intelligence, machine learning trends, tutorials, and industry insights.",
        "keywords": "AI blog, artificial intelligence news, machine learning tips, NeuraPlusAI blog",
        "schema_type": "WebPage",
    },
    "privacy-policy.html": {
        "title": "Privacy Policy – NeuraPlusAI",
        "description": "Read NeuraPlusAI's privacy policy to understand how we collect, use, and protect your personal information.",
        "keywords": "privacy policy, NeuraPlusAI privacy, data protection, user data",
        "schema_type": "WebPage",
    },
}

# Default fallback for blog posts
BLOG_DEFAULT = {
    "title": "NeuraPlusAI Blog Post – AI Insights",
    "description": "Read this insightful article on artificial intelligence from the NeuraPlusAI blog.",
    "keywords": "AI blog, artificial intelligence, NeuraPlusAI",
    "schema_type": "BlogPosting",
}
# ──────────────────────────────────────────────────────────────────────────────


def get_page_url(filepath: str) -> str:
    """Convert file path to full URL."""
    rel = filepath.replace("\\", "/")
    if rel.startswith("./"):
        rel = rel[2:]
    if rel == "index.html":
        return SITE_URL + "/"
    return f"{SITE_URL}/{rel}"


def extract_h1(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    return h1.get_text(strip=True) if h1 else ""


def build_schema(schema_type: str, title: str, description: str, url: str, soup: BeautifulSoup) -> dict:
    base = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": title,
        "description": description,
        "url": url,
    }
    if schema_type == "WebSite":
        base["potentialAction"] = {
            "@type": "SearchAction",
            "target": f"{SITE_URL}/?s={{search_term_string}}",
            "query-input": "required name=search_term_string"
        }
    if schema_type == "BlogPosting":
        base["headline"] = title
        base["author"] = {"@type": "Organization", "name": SITE_NAME}
        base["publisher"] = {
            "@type": "Organization",
            "name": SITE_NAME,
            "logo": {"@type": "ImageObject", "url": OG_IMAGE}
        }
    return base


def inject_seo(filepath: str, seo: dict) -> bool:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    soup = BeautifulSoup(content, "lxml")
    head = soup.find("head")
    if not head:
        print(f"  ⚠️  No <head> found in {filepath}, skipping.")
        return False

    title_text = seo["title"]
    desc_text  = seo["description"]
    kw_text    = seo["keywords"]
    page_url   = get_page_url(filepath)
    schema_type = seo.get("schema_type", "WebPage")

    def set_tag(tag, attrs, content_attr, value):
        """Find or create a meta/link tag and set its content."""
        existing = head.find(tag, attrs=attrs)
        if existing:
            existing[content_attr] = value
        else:
            new_tag = soup.new_tag(tag, **attrs)
            new_tag[content_attr] = value
            head.append(new_tag)

    # ── charset & viewport ────────────────────────────────────────────────────
    if not head.find("meta", charset=True):
        ct = soup.new_tag("meta", charset="UTF-8")
        head.insert(0, ct)

    if not head.find("meta", attrs={"name": "viewport"}):
        vp = soup.new_tag("meta")
        vp["name"] = "viewport"
        vp["content"] = "width=device-width, initial-scale=1.0"
        head.append(vp)

    # ── <title> ───────────────────────────────────────────────────────────────
    existing_title = head.find("title")
    if existing_title:
        existing_title.string = title_text
    else:
        t = soup.new_tag("title")
        t.string = title_text
        head.append(t)

    # ── basic meta ────────────────────────────────────────────────────────────
    set_tag("meta", {"name": "description"},        "content", desc_text)
    set_tag("meta", {"name": "keywords"},           "content", kw_text)
    set_tag("meta", {"name": "robots"},             "content", "index, follow")
    set_tag("link", {"rel": "canonical"},           "href",    page_url)

    # ── Open Graph ────────────────────────────────────────────────────────────
    set_tag("meta", {"property": "og:type"},        "content", "website")
    set_tag("meta", {"property": "og:site_name"},   "content", SITE_NAME)
    set_tag("meta", {"property": "og:title"},       "content", title_text)
    set_tag("meta", {"property": "og:description"}, "content", desc_text)
    set_tag("meta", {"property": "og:url"},         "content", page_url)
    set_tag("meta", {"property": "og:image"},       "content", OG_IMAGE)
    set_tag("meta", {"property": "og:image:width"}, "content", "1200")
    set_tag("meta", {"property": "og:image:height"},"content", "630")

    # ── Twitter Card ─────────────────────────────────────────────────────────
    set_tag("meta", {"name": "twitter:card"},        "content", "summary_large_image")
    set_tag("meta", {"name": "twitter:title"},       "content", title_text)
    set_tag("meta", {"name": "twitter:description"}, "content", desc_text)
    set_tag("meta", {"name": "twitter:image"},       "content", OG_IMAGE)
    set_tag("meta", {"name": "twitter:site"},        "content", TWITTER_HANDLE)

    # ── JSON-LD Schema ────────────────────────────────────────────────────────
    # Remove old schema if exists
    for old in head.find_all("script", attrs={"type": "application/ld+json"}):
        old.decompose()

    import json
    schema_data = build_schema(schema_type, title_text, desc_text, page_url, soup)
    schema_tag = soup.new_tag("script", type="application/ld+json")
    schema_tag.string = json.dumps(schema_data, indent=2, ensure_ascii=False)
    head.append(schema_tag)

    # ── Write back ────────────────────────────────────────────────────────────
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print(f"  ✅ Optimized: {filepath}")
    return True


def main():
    html_files = glob.glob("**/*.html", recursive=True) + glob.glob("*.html")
    html_files = list(set(html_files))  # deduplicate

    # Exclude Google verification file
    html_files = [f for f in html_files if "google" not in f.lower()]

    print(f"\n🔍 Found {len(html_files)} HTML files to optimize...\n")

    for filepath in sorted(html_files):
        filename = os.path.basename(filepath)
        parent   = os.path.basename(os.path.dirname(filepath))

        # Determine SEO data
        if filename in PAGE_SEO:
            seo = PAGE_SEO[filename]
        elif parent == "blog" or "blog" in filepath:
            # For blog posts, try to extract title from H1
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
            soup_temp = BeautifulSoup(raw, "lxml")
            h1_text = extract_h1(soup_temp)
            seo = BLOG_DEFAULT.copy()
            if h1_text:
                seo["title"]       = f"{h1_text} – NeuraPlusAI Blog"
                seo["description"] = f"Read '{h1_text}' on the NeuraPlusAI blog. Explore AI insights, tutorials and the latest in artificial intelligence."
        else:
            # Generic fallback
            seo = {
                "title": f"{filename.replace('.html','').replace('-',' ').title()} – NeuraPlusAI",
                "description": f"NeuraPlusAI – {filename.replace('.html','').replace('-',' ').title()} page.",
                "keywords": f"NeuraPlusAI, {filename.replace('.html','').replace('-',' ')}",
                "schema_type": "WebPage",
            }

        inject_seo(filepath, seo)

    print("\n🎉 All HTML files SEO-optimized successfully!\n")


if __name__ == "__main__":
    main()
