"""
seo_optimizer.py - Automatically does:
  ✅ Title, meta description, keywords
  ✅ Open Graph tags
  ✅ Twitter Card tags
  ✅ JSON-LD Schema
  ✅ Canonical URL
  ✅ robots meta
  ✅ sitemap.xml (auto-generated from all HTML files)
  ✅ robots.txt
  ✅ HTML minification (page speed)
"""

import os
import glob
import json
from datetime import date
from bs4 import BeautifulSoup
try:
    import htmlmin
    HAS_HTMLMIN = True
except ImportError:
    HAS_HTMLMIN = False

# ─── CONFIG ───────────────────────────────────────────────────────────────────
SITE_URL       = "https://neuraplus-ai.github.io"
SITE_NAME      = "NeuraPlusAI"
OG_IMAGE       = f"{SITE_URL}/favicon.svg"
TWITTER_HANDLE = "@neuraplus_ai"
TODAY          = date.today().isoformat()

PAGE_SEO = {
    "index.html": {
        "title": "NeuraPlusAI – Best Claude Prompts & Anthropic Prompt Generator",
        "description": "Discover the most powerful Claude AI prompts and Anthropic prompt generator tools. NeuraPlusAI helps you get the best results from Claude, Groq, and top AI models.",
        "keywords": "claude prompts, anthropic prompt generator, best prompts for claude, claude ai prompts, powerful claude prompts, NeuraPlusAI",
        "schema_type": "WebSite",
        "priority": "1.0",
        "changefreq": "weekly",
    },
    "about.html": {
        "title": "About NeuraPlusAI – Claude Prompts & AI Tools Platform",
        "description": "NeuraPlusAI is your go-to platform for Claude AI prompts, Anthropic tools, and Groq startup resources. Learn about our mission to make AI accessible for everyone.",
        "keywords": "about NeuraPlusAI, claude prompts platform, anthropic tools, groq for startups, AI prompt generator",
        "schema_type": "WebPage",
        "priority": "0.8",
        "changefreq": "monthly",
    },
    "contact.html": {
        "title": "Contact NeuraPlusAI – Claude Prompts & AI Tools Support",
        "description": "Get in touch with NeuraPlusAI for help with Claude prompts, Anthropic prompt generator tools, or any AI-related questions. We are here to help.",
        "keywords": "contact NeuraPlusAI, claude prompts support, anthropic help, AI tools support",
        "schema_type": "WebPage",
        "priority": "0.7",
        "changefreq": "monthly",
    },
    "blog.html": {
        "title": "NeuraPlusAI Blog – Claude Prompts, Groq, Anthropic & AI News",
        "description": "Read the latest articles on Claude AI prompts, Anthropic prompt generator tips, Groq vs Google TPU comparisons, and the best AI tools for developers and startups.",
        "keywords": "claude prompts blog, anthropic prompt generator tips, groq lpu vs google tpu, best ollama model for coding, AI news, NeuraPlusAI blog",
        "schema_type": "WebPage",
        "priority": "0.9",
        "changefreq": "weekly",
    },
    "privacy-policy.html": {
        "title": "Privacy Policy – NeuraPlusAI",
        "description": "Read NeuraPlusAI's privacy policy to understand how we collect, use, and protect your data while using our Claude prompts and AI tools platform.",
        "keywords": "NeuraPlusAI privacy policy, data protection, AI tools privacy",
        "schema_type": "WebPage",
        "priority": "0.5",
        "changefreq": "yearly",
    },
}
BLOG_DEFAULT = {
    "title": "NeuraPlusAI Blog Post – AI Insights",
    "description": "Read this insightful article on artificial intelligence from the NeuraPlusAI blog.",
    "keywords": "AI blog, artificial intelligence, NeuraPlusAI",
    "schema_type": "BlogPosting",
    "priority": "0.7",
    "changefreq": "monthly",
}
# ──────────────────────────────────────────────────────────────────────────────


def get_page_url(filepath):
    rel = filepath.replace("\\", "/").lstrip("./")
    if rel == "index.html":
        return SITE_URL + "/"
    return f"{SITE_URL}/{rel}"


def set_meta(head, soup, attrs, value):
    existing = head.find("meta", attrs=attrs)
    if existing:
        existing["content"] = value
    else:
        tag = soup.new_tag("meta")
        for k, v in attrs.items():
            tag[k] = v
        tag["content"] = value
        head.append(tag)


def set_link(head, soup, rel_value, attr, value):
    existing = head.find("link", rel=rel_value)
    if existing:
        existing[attr] = value
    else:
        tag = soup.new_tag("link")
        tag["rel"] = rel_value
        tag[attr] = value
        head.append(tag)


def build_schema(schema_type, title, description, url):
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


def inject_seo(filepath, seo):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    soup = BeautifulSoup(content, "lxml")
    head = soup.find("head")
    if not head:
        print(f"  ⚠️  No <head> in {filepath}, skipping.")
        return

    title_text  = seo["title"]
    desc_text   = seo["description"]
    kw_text     = seo["keywords"]
    page_url    = get_page_url(filepath)
    schema_type = seo.get("schema_type", "WebPage")

    # charset
    if not head.find("meta", charset=True):
        ct = soup.new_tag("meta")
        ct["charset"] = "UTF-8"
        head.insert(0, ct)

    # viewport
    if not head.find("meta", attrs={"name": "viewport"}):
        vp = soup.new_tag("meta")
        vp["name"] = "viewport"
        vp["content"] = "width=device-width, initial-scale=1.0"
        head.append(vp)

    # <title>
    t = head.find("title")
    if t:
        t.string = title_text
    else:
        t = soup.new_tag("title")
        t.string = title_text
        head.append(t)

    # basic meta
    set_meta(head, soup, {"name": "description"}, desc_text)
    set_meta(head, soup, {"name": "keywords"},    kw_text)
    set_meta(head, soup, {"name": "robots"},      "index, follow")
    set_link(head, soup, "canonical",             "href", page_url)

    # Open Graph
    set_meta(head, soup, {"property": "og:type"},         "website")
    set_meta(head, soup, {"property": "og:site_name"},    SITE_NAME)
    set_meta(head, soup, {"property": "og:title"},        title_text)
    set_meta(head, soup, {"property": "og:description"},  desc_text)
    set_meta(head, soup, {"property": "og:url"},          page_url)
    set_meta(head, soup, {"property": "og:image"},        OG_IMAGE)
    set_meta(head, soup, {"property": "og:image:width"},  "1200")
    set_meta(head, soup, {"property": "og:image:height"}, "630")

    # Twitter Card
    set_meta(head, soup, {"name": "twitter:card"},        "summary_large_image")
    set_meta(head, soup, {"name": "twitter:title"},       title_text)
    set_meta(head, soup, {"name": "twitter:description"}, desc_text)
    set_meta(head, soup, {"name": "twitter:image"},       OG_IMAGE)
    set_meta(head, soup, {"name": "twitter:site"},        TWITTER_HANDLE)

    # JSON-LD Schema
    for old in head.find_all("script", attrs={"type": "application/ld+json"}):
        old.decompose()
    schema_tag = soup.new_tag("script")
    schema_tag["type"] = "application/ld+json"
    schema_tag.string = json.dumps(
        build_schema(schema_type, title_text, desc_text, page_url),
        indent=2
    )
    head.append(schema_tag)

    final = str(soup)

    # Minify HTML
    if HAS_HTMLMIN:
        try:
            final = htmlmin.minify(final, remove_comments=True, remove_empty_space=True)
        except Exception:
            pass

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(final)

    print(f"  ✅ {filepath}")


def generate_robots_txt():
    """Auto-generate robots.txt"""
    content = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    with open("robots.txt", "w") as f:
        f.write(content)
    print("  ✅ robots.txt generated")


def generate_sitemap(html_files, seo_map):
    """Auto-generate sitemap.xml from all HTML files"""
    urls = []
    for filepath in sorted(html_files):
        filename = os.path.basename(filepath)
        page_url = get_page_url(filepath)
        seo = seo_map.get(filename, {})
        priority   = seo.get("priority", "0.6")
        changefreq = seo.get("changefreq", "monthly")

        urls.append(f"""  <url>
    <loc>{page_url}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{changefreq}</changefreq>
    <priority>{priority}</priority>
  </url>""")

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

{chr(10).join(urls)}

</urlset>"""

    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"  ✅ sitemap.xml generated with {len(urls)} URLs")


def main():
    html_files = list(set(
        glob.glob("**/*.html", recursive=True) +
        glob.glob("*.html")
    ))
    html_files = [f for f in html_files if "google" not in f.lower()]

    print(f"\n🔍 Found {len(html_files)} HTML files\n")

    # Build full SEO map including blog posts
    seo_map = {}
    for filepath in html_files:
        filename = os.path.basename(filepath)
        if filename in PAGE_SEO:
            seo_map[filename] = PAGE_SEO[filename]
        elif "blog" in filepath.lower():
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
            temp = BeautifulSoup(raw, "lxml")
            h1 = temp.find("h1")
            seo = BLOG_DEFAULT.copy()
            if h1:
                h1_text = h1.get_text(strip=True)
                seo["title"]       = f"{h1_text} – NeuraPlusAI Blog"
                seo["description"] = f"Read '{h1_text}' on the NeuraPlusAI blog."
            seo_map[filename] = seo
        else:
            name = filename.replace(".html", "").replace("-", " ").title()
            seo_map[filename] = {
                "title":       f"{name} – NeuraPlusAI",
                "description": f"NeuraPlusAI – {name} page.",
                "keywords":    f"NeuraPlusAI, {name}",
                "schema_type": "WebPage",
                "priority":    "0.6",
                "changefreq":  "monthly",
            }

    # 1. SEO inject all HTML files
    print("📝 Injecting SEO tags...")
    for filepath in sorted(html_files):
        filename = os.path.basename(filepath)
        inject_seo(filepath, seo_map[filename])

    # 2. Auto-generate sitemap.xml
    print("\n🗺️  Generating sitemap.xml...")
    generate_sitemap(html_files, seo_map)

    # 3. Auto-generate robots.txt
    print("\n🤖 Generating robots.txt...")
    generate_robots_txt()

    print("\n🎉 Everything done automatically!\n")
    print("  ✅ SEO tags (title, meta, OG, Twitter, Schema)")
    print("  ✅ sitemap.xml")
    print("  ✅ robots.txt")
    print("  ✅ HTML minified for speed")


if __name__ == "__main__":
    main()
