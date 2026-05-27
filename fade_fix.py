#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║   NeuraPulse — Fade Fix Script                                  ║
║   Fixes black/invisible pages caused by .fade opacity:0 bug    ║
║   DROP IN REPO ROOT AND RUN:  python fade_fix.py               ║
╚══════════════════════════════════════════════════════════════════╝
"""

from pathlib import Path
import re

ROOT = Path(".").resolve()

# Folders to skip
SKIP_DIRS  = {".git", "node_modules", ".github", "assets", "schema", "scripts", "_cleanup_backup"}
# Files to skip
SKIP_FILES = {"seo_engine.py", "fade_fix.py", "neurapulse_cleanup.py"}

# ── THE FIX ──────────────────────────────────────────────────────────────────
# Forces ALL .fade elements to be visible immediately.
# Your JS IntersectionObserver adds .vis on scroll — but if it fails/delays,
# content stays invisible (black page). This CSS overrides that as a fallback.
# ─────────────────────────────────────────────────────────────────────────────
FADE_FIX_CSS = """\
<!-- NP:FADE-FIX -->
<style id="np-fade-fix">
  /* Prevent black pages: force .fade elements visible immediately.
     IntersectionObserver animations still work on top of this. */
  .fade {
    opacity: 1 !important;
    transform: translateY(0) !important;
    transition: none !important;
  }
  .fade.vis {
    opacity: 1 !important;
    transform: translateY(0) !important;
  }
</style>
<!-- /NP:FADE-FIX -->"""


def get_all_html_files():
    files = []
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        # Skip unwanted dirs
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        # Skip unwanted files
        if p.name in SKIP_FILES:
            continue
        files.append(p)
    return files


def fix_file(path):
    try:
        html = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"  [ERROR] Could not read {path}: {e}")
        return "error"

    # Already fixed — skip
    if "NP:FADE-FIX" in html:
        return "already_fixed"

    # No <head> tag — can't inject
    if "</head>" not in html:
        return "no_head"

    # Inject the fix just before </head>
    fixed_html = html.replace("</head>", FADE_FIX_CSS + "\n</head>", 1)

    try:
        path.write_text(fixed_html, encoding="utf-8")
        return "fixed"
    except Exception as e:
        print(f"  [ERROR] Could not write {path}: {e}")
        return "error"


def main():
    print("\n" + "═" * 55)
    print("  NeuraPulse — Fade Fix Script")
    print(f"  Root: {ROOT}")
    print("═" * 55 + "\n")

    files = get_all_html_files()
    print(f"  Found {len(files)} HTML files\n")

    counts = {"fixed": 0, "already_fixed": 0, "no_head": 0, "error": 0}

    for f in files:
        result = fix_file(f)
        counts[result] += 1
        rel = f.relative_to(ROOT)
        if result == "fixed":
            print(f"  ✅  Fixed  → {rel}")
        elif result == "already_fixed":
            print(f"  ⏭️   Skip   → {rel}  (already fixed)")
        elif result == "no_head":
            print(f"  ⚠️   Skip   → {rel}  (no </head> found)")
        elif result == "error":
            print(f"  ❌  Error  → {rel}")

    print("\n" + "═" * 55)
    print(f"  ✅  Fixed          : {counts['fixed']} pages")
    print(f"  ⏭️   Already fixed  : {counts['already_fixed']} pages")
    print(f"  ⚠️   Skipped        : {counts['no_head']} pages (no </head>)")
    print(f"  ❌  Errors         : {counts['error']} pages")
    print("═" * 55)
    print("\n  NEXT STEPS:")
    print("  git add .")
    print("  git commit -m 'fix: resolve black page fade bug on all pages'")
    print("  git push\n")


if __name__ == "__main__":
    main()
