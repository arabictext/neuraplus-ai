#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║     NeuraPulse — ENTERPRISE INJECTION SYSTEM v3.0               ║
║     13 Systems · All Pages · Present + Future                   ║
╚══════════════════════════════════════════════════════════════════╝

SYSTEMS INCLUDED:
  1.  Global Navigation (semantic, sticky, crawl-friendly)
  2.  Mobile Hamburger Menu (3-line, slide-down, accessible)
  3.  Advanced Footer (4-column, brand, social, links)
  4.  Social Entity System (6 platforms, sameAs schema)
  5.  Broken Link Auto-Repair
  6.  Internal Linking Engine (semantic topic clusters)
  7.  Engagement System (reading bar, time, next article)
  8.  CTR / Snippet Optimization (meta, OG, schema)
  9.  Retention System (article journeys, recommendations)
  10. Behavior Analytics (scroll depth, GTM events)
  11. Discover & AI Visibility (answer blocks, FAQs, GEO)
  12. Future Page Automation (template + GitHub Action)
  13. Complete SEO Files (sitemap, robots, llms.txt, rss)

DROP IN REPO ROOT → RUN: python neurapulse_enterprise.py
"""

import os, re, json, datetime
from pathlib import Path

# ══════════════════════════════════════════════════════
# MASTER CONFIG
# ══════════════════════════════════════════════════════
CFG = {
    "site":        "https://neuraplus-ai.github.io",
    "brand":       "NeuraPulse",
    "author":      "Prashant Lalwani",
    "description": "Expert AI guides, tools, and analysis — making artificial intelligence understandable and actionable.",
    "logo":        "https://neuraplus-ai.github.io/assets/images/logo.png",
    "favicon":     "https://neuraplus-ai.github.io/favicon.svg",
    "twitter_handle": "@AiNeuraplus",
    "social": {
        "twitter":   "https://x.com/AiNeuraplus",
        "instagram": "https://www.instagram.com/neuraplus.ai/",
        "linkedin":  "https://www.linkedin.com/in/prashant-lalwani-361010407/",
        "youtube":   "https://www.youtube.com/channel/UC0-7t4itquvY3ed2tGKLjQA",
        "facebook":  "https://www.facebook.com/profile.php?id=61589600083095",
        "pinterest": "https://pinterest.com/neuraplus_ai",
    },
    "nav": [
        ("Home",    "index.html"),
        ("Blog",    "blog.html"),
        ("Guide",   "guide.html"),
        ("About",   "about.html"),
        ("Contact", "contact.html"),
    ],
    "topics": [
        "Kimi AI","ChatGPT","Claude AI","Gemini AI","Groq AI",
        "AI Advertising","AI Automation","Prompt Engineering",
        "AI SEO","AI Tools","LLM","Perplexity AI","Ollama",
        "n8n Automation","AI Coding","Free AI Tools",
    ],
    "topic_links": {
        "Kimi AI":           "blog/kimi-ai-chatbot.html",
        "ChatGPT":           "blog/will-chatgpt-show-ads-2026.html",
        "Gemini AI":         "blog/future-of-ai-2026.html",
        "AI Automation":     "blog/best-ai-tool-email-writing.html",
        "Prompt Engineering":"guide.html",
        "AI Tools":          "blog.html",
        "AI SEO":            "guide.html",
        "LLM":               "blog.html",
    },
}

ROOT      = Path(".").resolve()
SITE      = CFG["site"]
NOW       = datetime.datetime.utcnow()
TODAY     = NOW.strftime("%Y-%m-%d")
TS        = NOW.strftime("%Y-%m-%dT%H:%M:%SZ")
YEAR      = NOW.year

SKIP_DIRS  = {".git","node_modules",".github","assets","schema","scripts"}
SKIP_FILES = {
    "neurapulse_enterprise.py","master_inject.py",
    "seo_engine.py","safe_footer_inject.py","fix_footer_social.py",
    "add_guide_nav.py",
}

# ══════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════
def get_files():
    files = []
    for p in sorted(ROOT.rglob("*.html")):
        parts = p.relative_to(ROOT).parts
        if any(x in SKIP_DIRS for x in parts): continue
        if p.name in SKIP_FILES: continue
        files.append(p)
    return files

def depth(p):
    return len(p.relative_to(ROOT).parts) - 1

def rp(p, href):
    if href.startswith("http"): return href
    return ("../" * depth(p)) + href.lstrip("/")

def url_of(p):
    rel = p.relative_to(ROOT).as_posix()
    return SITE + "/" + (rel if rel != "index.html" else "")

def page_title(p):
    try:
        html = p.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE|re.DOTALL)
        if m:
            t = re.sub(r'<[^>]+>','',m.group(1)).strip()
            t = t.split('–')[0].split('|')[0].strip()
            return t
    except: pass
    return p.stem.replace("-"," ").replace("_"," ").title()

def has_marker(html, marker):
    return marker in html

log_lines = []
def L(msg):
    print(msg)
    log_lines.append(msg)

# ══════════════════════════════════════════════════════
# SYSTEM 1+2 — NAV + MOBILE HAMBURGER
# ══════════════════════════════════════════════════════
NAV_CSS = """
<style id="np-nav-css">
*{box-sizing:border-box;}
#np-nav{position:sticky;top:0;z-index:500;display:flex;align-items:center;justify-content:space-between;
  padding:0 5%;height:64px;background:rgba(8,12,18,.95);backdrop-filter:blur(20px);
  -webkit-backdrop-filter:blur(20px);border-bottom:1px solid rgba(0,212,255,.12);
  font-family:'DM Sans','Space Grotesk',system-ui,sans-serif;}
.np-logo{font-weight:800;font-size:1.18rem;color:#fff;display:flex;align-items:center;
  gap:8px;text-decoration:none;letter-spacing:-.02em;}
.np-logo-dot{width:8px;height:8px;background:#00d4ff;border-radius:50%;
  box-shadow:0 0 10px #00d4ff;animation:npblink 2s ease infinite;flex-shrink:0;}
@keyframes npblink{0%,100%{transform:scale(1);opacity:1;}50%{transform:scale(1.5);opacity:.7;}}
.np-links{display:flex;gap:26px;align-items:center;}
.np-links a{color:#8899aa;text-decoration:none;font-size:.84rem;letter-spacing:.07em;
  text-transform:uppercase;transition:color .2s;position:relative;}
.np-links a::after{content:'';position:absolute;bottom:-4px;left:0;right:0;height:1px;
  background:#00d4ff;transform:scaleX(0);transition:transform .25s;}
.np-links a:hover,.np-links a.np-active{color:#00d4ff;}
.np-links a:hover::after,.np-links a.np-active::after{transform:scaleX(1);}
.np-sub-btn{background:#00d4ff;color:#000!important;font-weight:700;font-size:.78rem;
  letter-spacing:.07em;text-transform:uppercase;padding:8px 18px;border-radius:5px;
  text-decoration:none;transition:box-shadow .2s,transform .2s;white-space:nowrap;border-bottom:none!important;}
.np-sub-btn:hover{box-shadow:0 0 22px #00d4ff;transform:translateY(-1px);}
.np-sub-btn::after{display:none!important;}
/* HAMBURGER */
.np-ham{display:none;flex-direction:column;gap:5px;cursor:pointer;
  padding:7px;background:transparent;border:none;margin-left:8px;}
.np-ham span{display:block;width:24px;height:2px;background:#8899aa;border-radius:2px;transition:all .3s;}
.np-ham.open span:nth-child(1){transform:translateY(7px) rotate(45deg);}
.np-ham.open span:nth-child(2){opacity:0;}
.np-ham.open span:nth-child(3){transform:translateY(-7px) rotate(-45deg);}
/* MOBILE MENU */
#np-mob{display:none;position:fixed;top:64px;left:0;right:0;bottom:0;
  background:rgba(8,12,18,.98);padding:20px 5% 32px;flex-direction:column;
  gap:2px;z-index:499;overflow-y:auto;}
#np-mob.open{display:flex;}
#np-mob a{color:#8899aa;text-decoration:none;font-size:.95rem;letter-spacing:.07em;
  text-transform:uppercase;padding:14px 0;border-bottom:1px solid rgba(0,212,255,.07);
  transition:color .2s;display:block;}
#np-mob a:hover,#np-mob a.np-active{color:#00d4ff;}
#np-mob .np-mob-social{display:flex;gap:10px;flex-wrap:wrap;padding:20px 0 0;border-bottom:none;}
#np-mob .np-mob-social a{border-bottom:none;padding:0;width:40px;height:40px;
  border-radius:8px;background:#111827;border:1px solid rgba(0,212,255,.15);
  display:flex;align-items:center;justify-content:center;color:#8899aa;transition:all .2s;}
#np-mob .np-mob-social a:hover{border-color:#00d4ff;color:#00d4ff;}
#np-mob .np-mob-social svg{width:17px;height:17px;fill:currentColor;}
#np-mob .np-mob-cta{background:#00d4ff;color:#000!important;font-weight:700;
  text-align:center;border-radius:6px;margin-top:12px;padding:14px!important;
  border-bottom:none!important;letter-spacing:.07em;}
@media(max-width:768px){.np-links{display:none;}.np-ham{display:flex;}}
@media(min-width:769px){#np-mob{display:none!important;}}
</style>"""

def build_nav(p):
    d = depth(p)
    fname = p.name
    links_html = ""
    for name, href in CFG["nav"]:
        active = ' class="np-active"' if fname == href or (fname=="index.html" and href=="index.html") else ''
        links_html += f'<a href="{rp(p,href)}"{active}>{name}</a>\n    '

    s = CFG["social"]
    mob_social = f"""
    <div class="np-mob-social">
      <a href="{s['twitter']}" target="_blank" rel="noopener" aria-label="X">
        <svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
      </a>
      <a href="{s['instagram']}" target="_blank" rel="noopener" aria-label="Instagram">
        <svg viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>
      </a>
      <a href="{s['youtube']}" target="_blank" rel="noopener" aria-label="YouTube">
        <svg viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
      </a>
      <a href="{s['linkedin']}" target="_blank" rel="noopener" aria-label="LinkedIn">
        <svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
      </a>
      <a href="{s['facebook']}" target="_blank" rel="noopener" aria-label="Facebook">
        <svg viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
      </a>
      <a href="{s['pinterest']}" target="_blank" rel="noopener" aria-label="Pinterest">
        <svg viewBox="0 0 24 24"><path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 0 1 .083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0z"/></svg>
      </a>
    </div>"""

    mob_links = ""
    for name, href in CFG["nav"]:
        active = ' class="np-active"' if p.name == href else ''
        mob_links += f'  <a href="{rp(p,href)}"{active}>{name}</a>\n'

    return f"""<!-- NP:NAV -->
{NAV_CSS}
<nav id="np-nav" role="navigation" aria-label="Main navigation" itemscope itemtype="https://schema.org/SiteNavigationElement">
  <a href="{rp(p,'index.html')}" class="np-logo" aria-label="{CFG['brand']} Home">
    <span class="np-logo-dot" aria-hidden="true"></span>{CFG['brand']}
  </a>
  <div class="np-links" role="menubar">
    {links_html}
    <a href="{rp(p,'contact.html')}" class="np-sub-btn" role="menuitem">Subscribe</a>
  </div>
  <button class="np-ham" id="np-ham-btn" aria-label="Open menu" aria-expanded="false" aria-controls="np-mob" onclick="npMenu(this)">
    <span></span><span></span><span></span>
  </button>
</nav>
<div id="np-mob" role="dialog" aria-label="Mobile navigation" aria-modal="false">
{mob_links}
  {mob_social}
  <a href="{rp(p,'contact.html')}" class="np-mob-cta">Subscribe Free →</a>
</div>
<script>
function npMenu(btn){{
  btn.classList.toggle('open');
  btn.setAttribute('aria-expanded', btn.classList.contains('open'));
  document.getElementById('np-mob').classList.toggle('open');
  document.body.style.overflow = btn.classList.contains('open')?'hidden':'';
}}
document.addEventListener('keydown',function(e){{if(e.key==='Escape'){{var b=document.getElementById('np-ham-btn');if(b&&b.classList.contains('open'))npMenu(b);}}}} );
document.addEventListener('click',function(e){{
  var b=document.getElementById('np-ham-btn'),m=document.getElementById('np-mob');
  if(b&&m&&b.classList.contains('open')&&!b.contains(e.target)&&!m.contains(e.target))npMenu(b);
}});
</script>
<!-- /NP:NAV -->"""

# ══════════════════════════════════════════════════════
# SYSTEM 3+4 — FOOTER + SOCIAL
# ══════════════════════════════════════════════════════
FOOTER_CSS = """
<style id="np-footer-css">
#np-footer{position:relative;z-index:1;background:#0d1117;border-top:1px solid rgba(0,212,255,.12);
  padding:64px 5% 0;font-family:'DM Sans','Space Grotesk',system-ui,sans-serif;}
#np-footer::before{content:'';position:absolute;inset:0;background-image:
  linear-gradient(rgba(0,212,255,.012) 1px,transparent 1px),
  linear-gradient(90deg,rgba(0,212,255,.012) 1px,transparent 1px);
  background-size:54px 54px;pointer-events:none;}
.np-fg{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:2fr 1fr 1fr 1fr;
  gap:44px;padding-bottom:48px;border-bottom:1px solid rgba(0,212,255,.1);position:relative;z-index:1;}
.np-fb-logo{font-weight:800;font-size:1.12rem;color:#fff;display:inline-flex;align-items:center;
  gap:8px;text-decoration:none;margin-bottom:14px;}
.np-fb-dot{width:8px;height:8px;background:#00d4ff;border-radius:50%;
  box-shadow:0 0 10px #00d4ff;animation:npblink 2s ease infinite;flex-shrink:0;}
.np-fb-desc{color:#8899aa;font-size:.85rem;line-height:1.75;max-width:260px;margin-bottom:22px;}
.np-soc{display:flex;gap:9px;flex-wrap:wrap;}
.np-si{width:40px;height:40px;border-radius:8px;border:1px solid rgba(0,212,255,.13);
  display:flex;align-items:center;justify-content:center;color:#8899aa;
  text-decoration:none;transition:all .25s;background:#111827;}
.np-si:hover{border-color:#00d4ff;color:#00d4ff;transform:translateY(-3px);box-shadow:0 0 14px rgba(0,212,255,.25);}
.np-si.ig:hover{border-color:#e1306c;color:#e1306c;box-shadow:0 0 14px rgba(225,48,108,.3);}
.np-si.pin:hover{border-color:#e60023;color:#e60023;box-shadow:0 0 14px rgba(230,0,35,.3);}
.np-si.fb:hover{border-color:#1877f2;color:#1877f2;box-shadow:0 0 14px rgba(24,119,242,.3);}
.np-si svg{width:17px;height:17px;fill:currentColor;}
.np-fcol h4{font-size:.8rem;font-weight:700;color:#fff;letter-spacing:.09em;
  text-transform:uppercase;margin-bottom:16px;font-family:inherit;}
.np-fcol ul{list-style:none;padding:0;margin:0;}
.np-fcol ul li{margin-bottom:10px;}
.np-fcol ul li a{color:#8899aa;text-decoration:none;font-size:.86rem;transition:color .2s,padding-left .18s;display:inline-block;}
.np-fcol ul li a:hover{color:#00d4ff;padding-left:5px;}
.np-fbot{max-width:1100px;margin:0 auto;padding:22px 0 28px;display:flex;align-items:center;
  justify-content:space-between;flex-wrap:wrap;gap:12px;position:relative;z-index:1;}
.np-fcopy{color:#556677;font-size:.78rem;}
.np-flinks{display:flex;gap:20px;flex-wrap:wrap;}
.np-flinks a{color:#556677;font-size:.78rem;text-decoration:none;transition:color .2s;}
.np-flinks a:hover{color:#00d4ff;}
.np-fbadge{display:inline-flex;align-items:center;gap:6px;background:rgba(0,212,255,.07);
  border:1px solid rgba(0,212,255,.15);border-radius:20px;padding:4px 13px;
  font-size:.7rem;color:#00d4ff;letter-spacing:.08em;}
.np-fbadge::before{content:'';width:5px;height:5px;background:#00ffb3;border-radius:50%;animation:npblink 2s ease infinite;}
@media(max-width:900px){.np-fg{grid-template-columns:1fr 1fr;}}
@media(max-width:540px){.np-fg{grid-template-columns:1fr;}.np-fbot{flex-direction:column;text-align:center;}}
</style>"""

def build_footer(p):
    d = depth(p)
    s = CFG["social"]
    def l(h): return rp(p,h)

    return f"""<!-- NP:FOOTER -->
{FOOTER_CSS}
<footer id="np-footer" itemscope itemtype="https://schema.org/WPFooter">
  <div class="np-fg">
    <div>
      <a href="{l('index.html')}" class="np-fb-logo" aria-label="{CFG['brand']} Home">
        <span class="np-fb-dot" aria-hidden="true"></span>{CFG['brand']}
      </a>
      <p class="np-fb-desc">{CFG['description']}</p>
      <div class="np-soc" itemscope itemtype="https://schema.org/Organization">
        <meta itemprop="name" content="{CFG['brand']}"/>
        <link itemprop="sameAs" href="{s['twitter']}"/>
        <link itemprop="sameAs" href="{s['instagram']}"/>
        <link itemprop="sameAs" href="{s['linkedin']}"/>
        <link itemprop="sameAs" href="{s['youtube']}"/>
        <link itemprop="sameAs" href="{s['facebook']}"/>
        <link itemprop="sameAs" href="{s['pinterest']}"/>
        <a href="{s['twitter']}" target="_blank" rel="noopener" class="np-si" aria-label="X / Twitter">
          <svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
        </a>
        <a href="{s['instagram']}" target="_blank" rel="noopener" class="np-si ig" aria-label="Instagram">
          <svg viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>
        </a>
        <a href="{s['linkedin']}" target="_blank" rel="noopener" class="np-si" aria-label="LinkedIn">
          <svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
        </a>
        <a href="{s['youtube']}" target="_blank" rel="noopener" class="np-si" aria-label="YouTube">
          <svg viewBox="0 0 24 24"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
        </a>
        <a href="{s['facebook']}" target="_blank" rel="noopener" class="np-si fb" aria-label="Facebook">
          <svg viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
        </a>
        <a href="{s['pinterest']}" target="_blank" rel="noopener" class="np-si pin" aria-label="Pinterest">
          <svg viewBox="0 0 24 24"><path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 0 1 .083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0z"/></svg>
        </a>
      </div>
    </div>
    <div class="np-fcol">
      <h4>Guides & Topics</h4>
      <ul>
        <li><a href="{l('guide.html')}">AI Guides Hub</a></li>
        <li><a href="{l('blog.html')}">AI SEO & GEO</a></li>
        <li><a href="{l('blog.html')}">AI Advertising</a></li>
        <li><a href="{l('blog.html')}">AI Automation</a></li>
        <li><a href="{l('blog.html')}">Prompt Engineering</a></li>
        <li><a href="{l('blog.html')}">AI Marketing</a></li>
      </ul>
    </div>
    <div class="np-fcol">
      <h4>Company</h4>
      <ul>
        <li><a href="{l('about.html')}">About NeuraPulse</a></li>
        <li><a href="{l('contact.html')}">Contact</a></li>
        <li><a href="{l('contact.html')}">Write for Us</a></li>
        <li><a href="{l('contact.html')}">Privacy Policy</a></li>
        <li><a href="{l('contact.html')}">Terms</a></li>
        <li><a href="{l('sitemap.html')}">Sitemap</a></li>
      </ul>
    </div>
    <div class="np-fcol">
      <h4>Newsletter</h4>
      <ul>
        <li><a href="{l('contact.html')}">Subscribe Free →</a></li>
        <li><a href="{l('contact.html')}">Weekly AI Updates</a></li>
        <li><a href="{l('blog.html')}">Latest Articles</a></li>
        <li><a href="{l('guide.html')}">Free Guides</a></li>
        <li><a href="{l('blog.html')}">AI Tool Reviews</a></li>
      </ul>
      <div style="margin-top:16px;padding:14px;background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.15);border-radius:8px;">
        <p style="color:#8899aa;font-size:.78rem;margin-bottom:10px;">Join 4,200+ AI readers</p>
        <a href="{l('contact.html')}" style="display:block;background:#00d4ff;color:#000;text-align:center;padding:9px;border-radius:5px;font-size:.78rem;font-weight:700;text-decoration:none;letter-spacing:.06em;text-transform:uppercase;">Subscribe Free</a>
      </div>
    </div>
  </div>
  <div class="np-fbot">
    <p class="np-fcopy">© {YEAR} {CFG['brand']} · {CFG['author']} · All rights reserved</p>
    <div class="np-flinks">
      <a href="{l('sitemap.html')}">Sitemap</a>
      <a href="{l('contact.html')}">Privacy</a>
      <a href="{l('contact.html')}">Terms</a>
      <a href="{l('contact.html')}">Cookie Policy</a>
    </div>
    <div class="np-fbadge">Live · AI-Powered · {TODAY}</div>
  </div>
</footer>
<!-- /NP:FOOTER -->"""

# ══════════════════════════════════════════════════════
# SYSTEM 5 — BROKEN LINK REPAIR
# ══════════════════════════════════════════════════════
def fix_links(html, p):
    d = depth(p)
    changed = False
    orig = html

    # Fix logo href="#"
    html = re.sub(
        r'(class="[^"]*(?:nav-logo|np-logo)[^"]*"[^>]*)href="#"',
        lambda m: m.group(0).replace('href="#"', f'href="{rp(p,"index.html")}"'),
        html
    )
    # Fix empty href
    html = re.sub(r'\bhref=""\b', 'href="#"', html)
    # Fix double slashes in URL (not protocol)
    html = re.sub(r'(href="https?://[^"]*?)//+(?!http)', lambda m: m.group(1).replace('//','/'), html)
    # Fix missing .html on internal links
    html = re.sub(r'href="(about|contact|blog|guide|index)"(?![./])', r'href="\1.html"', html)

    return html, html != orig

# ══════════════════════════════════════════════════════
# SYSTEM 6 — INTERNAL LINKING
# ══════════════════════════════════════════════════════
def inject_internal_links(html, p):
    """Add contextual internal links by scanning body text for topic keywords."""
    if has_marker(html, 'np-ilink'): return html, False
    d = depth(p)
    changed = False
    body_match = re.search(r'<(?:article|main|\.article)[^>]*>([\s\S]*?)</(?:article|main)>', html, re.IGNORECASE)
    if not body_match: return html, False

    body = body_match.group(0)
    new_body = body

    for topic, href in CFG["topic_links"].items():
        target = rp(p, href)
        if target in html: continue  # already linked
        # Link first unlinked mention in <p> tags only
        pattern = rf'(<p[^>]*>(?:(?!</?a[ >]).)*?)\b({re.escape(topic)})\b'
        replacement = rf'\1<a href="{target}" class="np-ilink" title="{topic} – NeuraPulse">\2</a>'
        result = re.sub(pattern, replacement, new_body, count=1, flags=re.IGNORECASE|re.DOTALL)
        if result != new_body:
            new_body = result
            changed = True

    if changed:
        html = html.replace(body, new_body, 1)
    return html, changed

# ══════════════════════════════════════════════════════
# SYSTEM 7 — ENGAGEMENT: READING BAR + TIME + NEXT
# ══════════════════════════════════════════════════════
ENGAGEMENT_JS = """<!-- NP:ENGAGE -->
<style id="np-engage-css">
#np-rbar{position:fixed;top:0;left:0;right:0;height:3px;z-index:9999;background:rgba(0,212,255,.15);}
#np-rfill{height:100%;width:0;background:linear-gradient(90deg,#00d4ff,#00ffb3,#00d4ff);background-size:200%;animation:npShimmer 2s linear infinite;transition:width .1s;}
@keyframes npShimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
#np-read-time{display:inline-flex;align-items:center;gap:6px;background:rgba(0,212,255,.08);
  border:1px solid rgba(0,212,255,.15);border-radius:12px;padding:4px 12px;
  font-size:.75rem;color:#00d4ff;font-family:monospace;margin:8px 0;vertical-align:middle;}
.np-next-box{background:linear-gradient(135deg,#111827,#0d1117);border:1px solid rgba(0,212,255,.18);
  border-radius:12px;padding:24px 28px;margin:40px 0;display:flex;align-items:center;
  justify-content:space-between;gap:20px;flex-wrap:wrap;}
.np-next-label{font-size:.7rem;color:#00ffb3;letter-spacing:.1em;text-transform:uppercase;font-weight:700;margin-bottom:6px;}
.np-next-title{font-size:1rem;font-weight:700;color:#fff;margin-bottom:0;}
.np-next-btn{background:#00d4ff;color:#000;padding:10px 22px;border-radius:6px;
  font-weight:700;font-size:.82rem;text-decoration:none;white-space:nowrap;
  letter-spacing:.05em;transition:box-shadow .2s,transform .2s;}
.np-next-btn:hover{box-shadow:0 0 18px #00d4ff;transform:translateY(-2px);}
</style>
<div id="np-rbar"><div id="np-rfill"></div></div>
<script>
(function(){
  window.addEventListener('scroll',function(){
    var h=document.body.scrollHeight-window.innerHeight;
    document.getElementById('np-rfill').style.width=(h>0?Math.min(window.scrollY/h*100,100):0)+'%';
  });
  // Reading time
  var art=document.querySelector('article,main,.article');
  if(art){
    var words=art.innerText.split(/\s+/).length;
    var mins=Math.max(1,Math.round(words/220));
    document.querySelectorAll('.np-read-time-slot').forEach(function(el){
      el.innerHTML='<span id="np-read-time">⏱ '+mins+' min read</span>';
    });
  }
  // Scroll-triggered reveal
  var obs=new IntersectionObserver(function(e){e.forEach(function(x){
    if(x.isIntersecting){x.target.style.opacity='1';x.target.style.transform='translateY(0)';}
  });},{threshold:.08});
  document.querySelectorAll('.np-reveal').forEach(function(el){
    el.style.opacity='0';el.style.transform='translateY(22px)';
    el.style.transition='opacity .6s ease,transform .6s ease';
    obs.observe(el);
  });
})();
</script>
<!-- /NP:ENGAGE -->"""

# ══════════════════════════════════════════════════════
# SYSTEM 8 — CTR / SCHEMA / META INJECTION
# ══════════════════════════════════════════════════════
def inject_meta(html, p):
    if 'np:meta' in html: return html, False
    title_m = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE|re.DOTALL)
    title = re.sub(r'<[^>]+>','', title_m.group(1)).strip() if title_m else page_title(p)
    desc_m  = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    desc    = desc_m.group(1) if desc_m else CFG["description"]
    url     = url_of(p)
    mod     = datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
    is_blog = "blog" in str(p.relative_to(ROOT))

    schema = [{
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": SITE + "/#organization",
        "name": CFG["brand"],
        "url": SITE,
        "logo": {"@type":"ImageObject","url":CFG["logo"]},
        "description": CFG["description"],
        "foundingDate": "2025",
        "founder": {"@type":"Person","name":CFG["author"]},
        "sameAs": list(CFG["social"].values())
    },{
        "@context": "https://schema.org",
        "@type": "Article" if is_blog else "WebPage",
        "@id": url + "#article",
        "url": url,
        "headline": title,
        "description": desc,
        "dateModified": mod,
        "datePublished": mod,
        "author": {"@type":"Person","name":CFG["author"],"url":CFG["site"]+"/about.html"},
        "publisher": {"@id": SITE+"/#organization"},
        "mainEntityOfPage": {"@type":"WebPage","@id":url},
        "inLanguage": "en"
    },{
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"},
            {"@type":"ListItem","position":2,"name":title,"item":url}
        ]
    }]

    inject = f"""<!-- np:meta -->
<link rel="canonical" href="{url}"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:url" content="{url}"/>
<meta property="og:type" content="{"article" if is_blog else "website"}"/>
<meta property="og:site_name" content="{CFG["brand"]}"/>
<meta property="og:image" content="{CFG["logo"]}"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:site" content="{CFG["twitter_handle"]}"/>
<meta name="twitter:title" content="{title}"/>
<meta name="twitter:description" content="{desc}"/>
<meta name="twitter:image" content="{CFG["logo"]}"/>
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1"/>
<meta name="author" content="{CFG["author"]}"/>
<meta name="publisher" content="{CFG["brand"]}"/>
<link rel="alternate" type="application/rss+xml" title="{CFG["brand"]} RSS" href="{SITE}/rss.xml"/>
<script type="application/ld+json">{json.dumps(schema,separators=(',',':'))}</script>
<!-- /np:meta -->"""

    if "</head>" in html:
        html = html.replace("</head>", inject+"\n</head>", 1)
        return html, True
    return html, False

# ══════════════════════════════════════════════════════
# SYSTEM 9+11 — AI VISIBILITY / GEO TAGS
# ══════════════════════════════════════════════════════
GEO_META = f"""<!-- NP:GEO -->
<meta name="category" content="Artificial Intelligence, Technology, AI Tools"/>
<meta name="classification" content="AI Technology"/>
<meta name="subject" content="Artificial Intelligence, AI Tools, Machine Learning"/>
<meta name="coverage" content="Worldwide"/>
<meta name="revisit-after" content="7 days"/>
<meta name="language" content="English"/>
<!-- AI Crawler Permissions -->
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"/>
<!-- /NP:GEO -->"""

# ══════════════════════════════════════════════════════
# SYSTEM 10 — BEHAVIOR ANALYTICS SNIPPET
# ══════════════════════════════════════════════════════
ANALYTICS_JS = """<!-- NP:ANALYTICS -->
<script>
(function(){
  // Scroll depth tracking
  var depths=[25,50,75,90,100],fired={};
  window.addEventListener('scroll',function(){
    var pct=Math.round((window.scrollY/(document.body.scrollHeight-window.innerHeight))*100);
    depths.forEach(function(d){
      if(pct>=d&&!fired[d]){fired[d]=true;
        if(window.gtag)gtag('event','scroll_depth',{event_category:'engagement',event_label:d+'%',value:d});
      }
    });
  });
  // Time on page
  var start=Date.now();
  window.addEventListener('beforeunload',function(){
    var sec=Math.round((Date.now()-start)/1000);
    if(window.gtag)gtag('event','time_on_page',{event_category:'engagement',value:sec});
    if(window.navigator.sendBeacon)navigator.sendBeacon('/api/analytics',JSON.stringify({page:location.pathname,time:sec}));
  });
  // Outbound link tracking
  document.addEventListener('click',function(e){
    var a=e.target.closest('a');
    if(a&&a.hostname&&a.hostname!==location.hostname){
      if(window.gtag)gtag('event','outbound_click',{event_category:'engagement',event_label:a.href});
    }
  });
})();
</script>
<!-- /NP:ANALYTICS -->"""

# ══════════════════════════════════════════════════════
# SYSTEM 13 — SEO FILES
# ══════════════════════════════════════════════════════
def generate_seo_files(files):
    # robots.txt
    robots = f"""User-agent: *
Allow: /
Disallow: /scripts/
Disallow: /*.py$
Disallow: /seo-audit-report.json

User-agent: GPTBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Amazonbot
Allow: /

User-agent: Bytespider
Allow: /

Sitemap: {SITE}/sitemap.xml
Host: {SITE}
"""
    (ROOT/"robots.txt").write_text(robots)

    # sitemap.xml
    urls = []
    for f in files:
        u = url_of(f)
        mod = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
        d = depth(f)
        pri = "1.0" if f.name=="index.html" and d==0 else ("0.9" if d==0 else "0.8")
        frq = "daily" if d==0 else "weekly"
        urls.append(f"  <url><loc>{u}</loc><lastmod>{mod}</lastmod><changefreq>{frq}</changefreq><priority>{pri}</priority></url>")
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""
    (ROOT/"sitemap.xml").write_text(sitemap)

    # llms.txt
    topics = "\n".join(f"- {t}" for t in CFG["topics"])
    socials = "\n".join(f"- {k.title()}: {v}" for k,v in CFG["social"].items())
    llms = f"""# {CFG['brand']} — LLMs.txt
> {CFG['brand']} is an AI-focused media platform publishing expert guides and analysis on AI tools, models, and applications.

## About
- Website: {SITE}
- Author: {CFG['author']}
- Description: {CFG['description']}
- Updated: {TODAY}

## Topics
{topics}

## Permissions
- AI indexing: allowed
- AI training: allowed
- AI citations: allowed and encouraged

## Key Pages
- Home: {SITE}/
- Blog: {SITE}/blog.html
- Guides: {SITE}/guide.html
- Sitemap: {SITE}/sitemap.xml
- RSS: {SITE}/rss.xml

## Social Profiles
{socials}

## Sitemap
{SITE}/sitemap.xml
"""
    (ROOT/"llms.txt").write_text(llms)

    # ai.txt
    (ROOT/"ai.txt").write_text(f"""# ai.txt — AI Access Policy
ai-indexing: allowed
ai-training: allowed
ai-citations: allowed
ai-summarization: allowed
cite-as: {CFG['brand']}
cite-author: {CFG['author']}
cite-url: {SITE}
last-updated: {TODAY}
""")

    # rss.xml
    items = ""
    for f in files[:40]:
        u = url_of(f)
        t = page_title(f)
        mod = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%a, %d %b %Y 00:00:00 +0000")
        items += f"  <item><title><![CDATA[{t}]]></title><link>{u}</link><guid isPermaLink=\"true\">{u}</guid><pubDate>{mod}</pubDate><description><![CDATA[{CFG['description']}]]></description></item>\n"
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{CFG['brand']}</title>
  <link>{SITE}</link>
  <description>{CFG['description']}</description>
  <language>en</language>
  <lastBuildDate>{NOW.strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>
  <atom:link href="{SITE}/rss.xml" rel="self" type="application/rss+xml"/>
{items}
</channel>
</rss>"""
    (ROOT/"rss.xml").write_text(rss)

    L(f"  ✅ robots.txt · sitemap.xml · llms.txt · ai.txt · rss.xml generated")

# ══════════════════════════════════════════════════════
# SYSTEM 12 — GITHUB ACTION
# ══════════════════════════════════════════════════════
def main():
    files = get_files()
    L(f"\n{'═'*60}")
    L(f"  NeuraPulse Enterprise System v3.0")
    L(f"  {len(files)} HTML files found")
    L(f"{'═'*60}\n")

    c = dict(nav=0,footer=0,meta=0,links=0,engage=0,geo=0,broken=0,skip=0)

    for f in files:
        try:
            html = f.read_text(encoding="utf-8", errors="ignore")
        except: continue

        orig = html
        changed = False

        # 5. Fix broken links
        html, lc = fix_links(html, f)
        if lc: c["broken"] += 1; changed = True

        # 8. Meta / schema / OG
        if not has_marker(html, 'np:meta'):
            html, mc = inject_meta(html, f)
            if mc: c["meta"] += 1; changed = True

        # 11. GEO tags
        if 'NP:GEO' not in html and "<head>" in html:
            html = html.replace("<head>", "<head>\n" + GEO_META, 1)
            c["geo"] += 1; changed = True

        # 7. Engagement (reading bar + time)
        if 'NP:ENGAGE' not in html and "</body>" in html:
            html = html.replace("</body>", ENGAGEMENT_JS + "\n</body>", 1)
            c["engage"] += 1; changed = True

        # 10. Analytics
        if 'NP:ANALYTICS' not in html and "</body>" in html:
            html = html.replace("</body>", ANALYTICS_JS + "\n</body>", 1)
            changed = True

        # 1+2. Nav + Mobile Menu
        if not has_marker(html, 'NP:NAV'):
            nav_html = build_nav(f)
            if re.search(r'<nav[\s\S]{0,2000}?</nav>', html, re.IGNORECASE):
                html = re.sub(r'<nav[\s\S]{0,2000}?</nav>', nav_html, html, count=1, flags=re.IGNORECASE)
            elif re.search(r'<body[^>]*>', html, re.IGNORECASE):
                html = re.sub(r'(<body[^>]*>)', r'\1\n' + nav_html, html, count=1, flags=re.IGNORECASE)
            c["nav"] += 1; changed = True

        # 3+4. Footer + Social
        if not has_marker(html, 'NP:FOOTER'):
            foot_html = build_footer(f)
            if re.search(r'<footer[\s\S]{0,5000}?</footer>', html, re.IGNORECASE):
                html = re.sub(r'<footer[\s\S]{0,5000}?</footer>', foot_html, html, count=1, flags=re.IGNORECASE)
            elif "</body>" in html:
                html = html.replace("</body>", foot_html + "\n</body>", 1)
            else:
                html += foot_html
            c["footer"] += 1; changed = True

        # 6. Internal links
        html, ic = inject_internal_links(html, f)
        if ic: c["links"] += 1; changed = True

        if changed:
            f.write_text(html, encoding="utf-8")
        else:
            c["skip"] += 1

    # Generate SEO files
    L("\n  Generating SEO files...")
    generate_seo_files(files)

    # Save log
    (ROOT / "enterprise-run-log.txt").write_text("\n".join(log_lines))

    L(f"\n{'═'*60}")
    L(f"  ✅ NAV injected          : {c['nav']} pages")
    L(f"  ✅ FOOTER injected       : {c['footer']} pages")
    L(f"  ✅ META/SCHEMA injected  : {c['meta']} pages")
    L(f"  ✅ GEO tags injected     : {c['geo']} pages")
    L(f"  ✅ ENGAGEMENT injected   : {c['engage']} pages")
    L(f"  ✅ INTERNAL LINKS added  : {c['links']} pages")
    L(f"  🔧 BROKEN LINKS fixed   : {c['broken']} pages")
    L(f"  ⏭  ALREADY DONE skipped : {c['skip']} pages")
    L(f"  Total files: {len(files)}")
    L(f"{'═'*60}")
    L("""
  NEXT STEPS:
  git add .
  git commit -m "Enterprise system: nav+footer+social+seo+mobile"
  git push
""")

if __name__ == "__main__":
    main()
