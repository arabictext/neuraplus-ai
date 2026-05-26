#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  NeuraPulse — Enterprise Injection CLEANUP v1.0                 ║
║  Safely removes ALL damage from neurapulse_enterprise.py and    ║
║  neurapulse_card_injector.py without touching:                  ║
║    ✅ SEO / metadata / sitemap systems                           ║
║    ✅ Existing images / image scripts                            ║
║    ✅ Existing blog content                                      ║
║    ✅ Routes / pages / real components                           ║
║    ✅ Legitimate styling                                         ║
║                                                                  ║
║  DROP IN REPO ROOT → python neurapulse_cleanup.py               ║
║  Use --dry-run to preview without writing                        ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os, re, shutil, sys, datetime
from pathlib import Path

# ═══════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════
DRY_RUN  = "--dry-run" in sys.argv
VERBOSE  = "--verbose" in sys.argv or "-v" in sys.argv
ROOT     = Path(".").resolve()
NOW      = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP   = ROOT / f"_cleanup_backup_{NOW}"

SKIP_DIRS  = {".git", "node_modules", "_cleanup_backup_"}
SKIP_FILES = {
    "neurapulse_enterprise.py",
    "neurapulse_card_injector.py",
    "master_inject.py",
    "seo_engine.py",
    "safe_footer_inject.py",
    "fix_footer_social.py",
    "add_guide_nav.py",
    "neurapulse_cleanup.py",   # this script
}

log_lines   = []
stats       = dict(scanned=0, cleaned=0, unchanged=0, backed_up=0, errors=0)


def log(msg, force=False):
    print(msg)
    log_lines.append(msg)


def vlog(msg):
    if VERBOSE:
        print(msg)
    log_lines.append(msg)


# ═══════════════════════════════════════════════════
#  1.  EXACT INJECTION MARKERS TO STRIP
#      (everything between start and end comment,
#       inclusive, is removed)
# ═══════════════════════════════════════════════════
BLOCK_MARKERS = [
    # nav injection
    ("<!-- NP:NAV -->",         "<!-- /NP:NAV -->"),
    # footer injection
    ("<!-- NP:FOOTER -->",      "<!-- /NP:FOOTER -->"),
    # engagement bar / reading-progress
    ("<!-- NP:ENGAGE -->",      "<!-- /NP:ENGAGE -->"),
    # analytics block
    ("<!-- NP:ANALYTICS -->",   "<!-- /NP:ANALYTICS -->"),
    # GEO/AEO meta block
    ("<!-- NP:GEO -->",         "<!-- /NP:GEO -->"),
    # meta/schema block
    ("<!-- np:meta -->",        "<!-- /np:meta -->"),
    # blog card injector markers
    ("<!-- NP:BLOG-CARDS-START -->", "<!-- NP:BLOG-CARDS-END -->"),
    # guide card injector markers
    ("<!-- NP:GUIDE-CARDS-START -->", "<!-- NP:GUIDE-CARDS-END -->"),
]


# ═══════════════════════════════════════════════════
#  2.  LONE CLOSING MARKERS  (no matching open left)
#      strip if orphaned open wasn't removed above
# ═══════════════════════════════════════════════════
LONE_MARKERS = [
    "<!-- /NP:NAV -->",
    "<!-- /NP:FOOTER -->",
    "<!-- /NP:ENGAGE -->",
    "<!-- /NP:ANALYTICS -->",
    "<!-- /NP:GEO -->",
    "<!-- /np:meta -->",
    "<!-- NP:BLOG-CARDS-START -->",
    "<!-- NP:BLOG-CARDS-END -->",
    "<!-- NP:GUIDE-CARDS-START -->",
    "<!-- NP:GUIDE-CARDS-END -->",
]


# ═══════════════════════════════════════════════════
#  3.  DUPLICATE <style id="np-*"> BLOCKS
#      The enterprise script injects a <style id="np-footer-css">
#      AND the pages already had one — result: two copies.
#      We keep the FIRST occurrence and remove duplicates.
# ═══════════════════════════════════════════════════
DUPLICATE_STYLE_IDS = [
    "np-nav-css",
    "np-footer-css",
    "np-engage-css",
]


# ═══════════════════════════════════════════════════
#  4.  DUPLICATE STRUCTURAL ELEMENTS
#      The enterprise script may have injected a second
#      <nav id="np-nav">…</nav> or a second
#      <footer id="np-footer">…</footer>.
#      We keep the FIRST occurrence only.
# ═══════════════════════════════════════════════════
DEDUP_ELEMENTS = [
    # (opening_tag_regex,  closing_tag,  description)
    (r'<nav\s[^>]*id="np-nav"',       "</nav>",    "duplicate #np-nav"),
    (r'<footer\s[^>]*id="np-footer"', "</footer>", "duplicate #np-footer"),
    (r'<div\s[^>]*id="np-mob"',       "</div>",    "duplicate #np-mob mobile menu"),
    (r'<div\s[^>]*id="np-rbar"',      "</div>",    "duplicate #np-rbar progress bar"),
    (r'<div\s[^>]*id="np-btn"',       None,        "duplicate np chat button"),
    (r'<div\s[^>]*id="np-win"',       "</div>",    "duplicate np chat window"),
]


# ═══════════════════════════════════════════════════
#  5.  INJECTED <script> BLOCKS (unique fingerprints)
#      These are the verbatim JS functions injected by
#      enterprise.  We match by their unique function names.
# ═══════════════════════════════════════════════════
INJECTED_SCRIPT_FINGERPRINTS = [
    # hamburger JS (enterprise injects it standalone too)
    r'function\s+npMenu\s*\(btn\)',
    # reading-progress bar (engage)
    r'document\.getElementById\(["\']np-rfill["\']\)',
    # outbound link tracking (analytics)
    r"outbound_click",
    # scroll depth tracking (analytics)
    r"scroll_depth",
    # time-on-page tracking (analytics)
    r"time_on_page",
    # np chat widget
    r'function\s+npOpen\s*\(\)',
    r'function\s+npSend\s*\(\)',
]


# ═══════════════════════════════════════════════════
#  6.  ENTERPRISE-INJECTED CSS THAT LEAKS GLOBALLY
#      These are inline <style> blocks whose ENTIRE content
#      was generated by the enterprise script (identified by
#      their unique opening rule).  We remove the whole tag.
# ═══════════════════════════════════════════════════
ENTERPRISE_STYLE_FINGERPRINTS = [
    # reading progress bar style block
    r"#np-rbar\s*\{",
    r"#np-rfill\s*\{",
    # chat widget style
    r"@keyframes\s+npb\s*\{",
]


# ═══════════════════════════════════════════════════
#  7.  ENTERPRISE-ONLY STRUCTURAL CHUNKS
#      Large fixed strings the enterprise script adds.
#      If the marker-based removal above misses them, these
#      regex patterns catch the raw HTML.
# ═══════════════════════════════════════════════════
STRUCTURAL_PATTERNS = [
    # floating chat button div  (#np-btn / #np-win)
    r'<div\s+id="np-btn"[\s\S]*?</div>\s*<div\s+id="np-win"[\s\S]*?</div>',
    # reading progress bar div
    r'<div\s+id="np-rbar"[^>]*>\s*<div\s+id="np-rfill"[^>]*>\s*</div>\s*</div>',
]


# ═══════════════════════════════════════════════════
#  HELPER: strip balanced tag from nth occurrence
# ═══════════════════════════════════════════════════
def strip_balanced_duplicates(html, open_re, close_tag, description):
    """
    Find ALL occurrences of `open_re … close_tag`.
    Keep the FIRST, remove subsequent ones.
    Returns (new_html, count_removed).
    """
    if close_tag is None:
        # self-contained single tag (e.g. <div id="np-btn" …/> or until next >)
        pat = re.compile(open_re + r'[^>]*>', re.IGNORECASE | re.DOTALL)
        spans = [m.span() for m in pat.finditer(html)]
        if len(spans) <= 1:
            return html, 0
        # remove all after first
        removed = 0
        for start, end in reversed(spans[1:]):
            html = html[:start] + html[end:]
            removed += 1
        return html, removed

    # Build pattern that matches open_re … close_tag (non-greedy via search loop)
    open_pat = re.compile(open_re, re.IGNORECASE | re.DOTALL)
    matches = list(open_pat.finditer(html))
    if len(matches) <= 1:
        return html, 0

    # find full extents by scanning for matching close
    regions = []
    for m in matches:
        start = m.start()
        end_pos = html.find(close_tag, m.end())
        if end_pos == -1:
            continue
        end_pos += len(close_tag)
        regions.append((start, end_pos))

    # remove all but first (iterate in reverse to preserve indices)
    removed = 0
    for start, end in reversed(regions[1:]):
        html = html[:start] + html[end:]
        removed += 1
    return html, removed


# ═══════════════════════════════════════════════════
#  CORE CLEANER
# ═══════════════════════════════════════════════════
def clean_file(path):
    original = path.read_text(encoding="utf-8", errors="ignore")
    html = original
    changes = []

    # ── Step 1: Remove marker-bounded blocks ──────────────
    for start_marker, end_marker in BLOCK_MARKERS:
        if start_marker in html:
            pattern = re.escape(start_marker) + r"[\s\S]*?" + re.escape(end_marker)
            new_html = re.sub(pattern, "", html)
            if new_html != html:
                count = len(re.findall(pattern, html))
                changes.append(f"removed {count}x block: {start_marker[:40]}")
                html = new_html

    # ── Step 2: Remove any lone marker comments left ──────
    for marker in LONE_MARKERS:
        if marker in html:
            html = html.replace(marker, "")
            changes.append(f"removed lone marker: {marker[:50]}")

    # ── Step 3: Remove duplicate <style id="np-*"> ────────
    for style_id in DUPLICATE_STYLE_IDS:
        pattern = re.compile(
            r'<style\s[^>]*id=["\']' + re.escape(style_id) + r'["\'][^>]*>[\s\S]*?</style>',
            re.IGNORECASE
        )
        found = pattern.findall(html)
        if len(found) > 1:
            # keep first, remove rest
            first = True
            def replacer(m):
                nonlocal first
                if first:
                    first = False
                    return m.group(0)
                return ""
            html = pattern.sub(replacer, html)
            changes.append(f"deduped {len(found)-1}x <style id='{style_id}'>")

    # ── Step 4: Remove duplicate structural elements ──────
    for open_re, close_tag, desc in DEDUP_ELEMENTS:
        new_html, removed = strip_balanced_duplicates(html, open_re, close_tag, desc)
        if removed:
            html = new_html
            changes.append(f"removed {removed}x {desc}")

    # ── Step 5: Remove injected standalone <script> blocks ─
    for fingerprint in INJECTED_SCRIPT_FINGERPRINTS:
        # Find <script>…</script> blocks containing this fingerprint
        script_pat = re.compile(r'<script[^>]*>[\s\S]*?' + fingerprint + r'[\s\S]*?</script>', re.IGNORECASE)
        found = script_pat.findall(html)
        if found:
            # Only remove scripts that consist ENTIRELY of enterprise code.
            # Heuristic: if the script ALSO contains legitimate site code keywords,
            # don't remove it blindly.  We check if it contains any of these safe
            # patterns outside the fingerprint.
            SAFE_SIGNALS = ["filt(", "doSub(", "IntersectionObserver", "obs.observe"]
            for block in found:
                has_safe = any(sig in block for sig in SAFE_SIGNALS)
                if not has_safe:
                    html = html.replace(block, "", 1)
                    changes.append(f"removed injected <script> containing: {fingerprint[:40]}")

    # ── Step 6: Remove enterprise-only <style> blocks ─────
    for fingerprint in ENTERPRISE_STYLE_FINGERPRINTS:
        style_pat = re.compile(r'<style[^>]*>[\s\S]*?' + fingerprint + r'[\s\S]*?</style>', re.IGNORECASE)
        for block in style_pat.findall(html):
            html = html.replace(block, "", 1)
            changes.append(f"removed enterprise <style> block: {fingerprint[:40]}")

    # ── Step 7: Remove enterprise structural patterns ─────
    for pat_str in STRUCTURAL_PATTERNS:
        pat = re.compile(pat_str, re.IGNORECASE | re.DOTALL)
        new_html, count = pat.subn("", html)
        if count:
            html = new_html
            changes.append(f"removed structural pattern: {pat_str[:50]}")

    # ── Step 8: Collapse excess blank lines ───────────────
    # Injected blocks often leave 3-5 blank lines behind
    html = re.sub(r'\n{4,}', '\n\n', html)

    return html, changes, html != original


# ═══════════════════════════════════════════════════
#  GET ALL TARGET HTML FILES
# ═══════════════════════════════════════════════════
def get_html_files():
    files = []
    for p in sorted(ROOT.rglob("*.html")):
        rel_parts = p.relative_to(ROOT).parts
        if any(part.startswith("_cleanup_backup_") for part in rel_parts):
            continue
        if any(d in SKIP_DIRS for d in rel_parts):
            continue
        if p.name in SKIP_FILES:
            continue
        files.append(p)
    return files


# ═══════════════════════════════════════════════════
#  BACKUP
# ═══════════════════════════════════════════════════
def backup_files(files):
    log(f"\n  📦 Creating backup → {BACKUP.name}/")
    for f in files:
        rel = f.relative_to(ROOT)
        dest = BACKUP / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
        stats["backed_up"] += 1
    # Also backup the enterprise workflow if it exists
    workflow = ROOT / ".github" / "workflows" / "neurapulse-enterprise.yml"
    if workflow.exists():
        dest = BACKUP / ".github" / "workflows" / "neurapulse-enterprise.yml"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(workflow, dest)
        stats["backed_up"] += 1
    log(f"  ✅ Backed up {stats['backed_up']} files")


# ═══════════════════════════════════════════════════
#  DISABLE ENTERPRISE WORKFLOW
# ═══════════════════════════════════════════════════
def disable_enterprise_workflow():
    yml = ROOT / ".github" / "workflows" / "neurapulse-enterprise.yml"
    if not yml.exists():
        return
    if DRY_RUN:
        log(f"  [dry-run] Would disable: {yml}")
        return
    disabled = yml.with_suffix(".yml.disabled")
    yml.rename(disabled)
    log(f"  🚫 Disabled enterprise workflow → {disabled.name}")


# ═══════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════
def main():
    log("\n" + "═" * 60)
    log("  NeuraPulse Enterprise Cleanup v1.0")
    if DRY_RUN:
        log("  ⚠️  DRY RUN — no files will be modified")
    log("═" * 60 + "\n")

    files = get_html_files()
    log(f"  Found {len(files)} HTML files to scan\n")

    # ── Preview / analysis pass ────────────────────────────
    damaged = []
    for f in files:
        try:
            _, changes, is_dirty = clean_file(f)
            if is_dirty:
                damaged.append((f, changes))
        except Exception as e:
            log(f"  ERROR scanning {f}: {e}")
            stats["errors"] += 1

    log(f"  Damage detected in {len(damaged)} files:\n")
    for f, changes in damaged:
        rel = f.relative_to(ROOT)
        log(f"  📄 {rel}")
        for c in changes:
            log(f"      → {c}")

    if not damaged:
        log("\n  ✅ No enterprise injection damage found. Nothing to do.")
        return

    if DRY_RUN:
        log("\n  [dry-run] Would clean the files listed above.")
        log("  Run without --dry-run to apply changes.")
        return

    # ── Confirm ────────────────────────────────────────────
    print(f"\n  Proceed? This will modify {len(damaged)} files. [y/N] ", end="", flush=True)
    try:
        answer = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = "n"

    if answer != "y":
        log("  Aborted — no files modified.")
        return

    # ── Backup first ───────────────────────────────────────
    backup_files([f for f, _ in damaged])

    # ── Apply cleanup ──────────────────────────────────────
    log("\n  🧹 Applying cleanup...\n")
    for f, _ in damaged:
        try:
            new_html, changes, changed = clean_file(f)
            if changed:
                f.write_text(new_html, encoding="utf-8")
                stats["cleaned"] += 1
                rel = f.relative_to(ROOT)
                log(f"  ✅ Cleaned: {rel} ({len(changes)} fix(es))")
                for c in changes:
                    vlog(f"      → {c}")
            else:
                stats["unchanged"] += 1
        except Exception as e:
            log(f"  ❌ ERROR cleaning {f}: {e}")
            stats["errors"] += 1

    # ── Disable enterprise workflow ────────────────────────
    disable_enterprise_workflow()

    # ── Save log ───────────────────────────────────────────
    log_path = ROOT / f"cleanup-log-{NOW}.txt"
    try:
        log_path.write_text("\n".join(log_lines), encoding="utf-8")
        log(f"\n  📋 Log saved → {log_path.name}")
    except Exception:
        pass

    # ── Summary ────────────────────────────────────────────
    log("\n" + "═" * 60)
    log("  CLEANUP SUMMARY")
    log(f"  Files scanned   : {len(files)}")
    log(f"  Files damaged   : {len(damaged)}")
    log(f"  Files cleaned   : {stats['cleaned']}")
    log(f"  Backup files    : {stats['backed_up']}")
    log(f"  Errors          : {stats['errors']}")
    log("═" * 60)
    log(f"\n  Backup location : {BACKUP}")
    log("  To restore:     cp -r " + str(BACKUP) + "/* .")
    log("\n  NEXT STEPS:")
    log("  1. Review changes: git diff")
    log("  2. Test your site visually")
    log("  3. Commit: git add . && git commit -m 'cleanup: remove enterprise injection'")
    log("  4. Push: git push")
    log("")


if __name__ == "__main__":
    main()
