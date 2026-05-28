#!/usr/bin/env python3
"""Generate /jobs/{slug}/ats-checklist.html pages from role JSON batches.

Inputs:  /tmp/role-data-batch-{1..5}.json
Outputs: /tmp/ats-checker-live/jobs/{slug}/ats-checklist.html  (50 pages)
         /tmp/ats-checker-live/jobs/index.html                  (hub)
         /tmp/ats-checker-live/jobs_urls.txt                    (for IndexNow)
"""
import json
import os
import re
import sys
from html import escape
from pathlib import Path

REPO = Path("/tmp/ats-checker-live")
BATCH_FILES = [Path(f"/tmp/role-data-batch-{i}.json") for i in range(1, 6)]
JOBS_DIR = REPO / "jobs"
SITE_BASE = "https://hugounoclaw.github.io/ats-checker"

# Slugs that have an existing /keywords-by-role/{slug}.html page (so we can cross-link).
EXISTING_KW_SLUGS = {
    "accountant", "administrative-assistant", "business-analyst", "content-writer",
    "customer-success", "data-analyst", "devops-engineer", "electrical-engineer",
    "financial-analyst", "graphic-designer", "hr-generalist", "marketing-manager",
    "mechanical-engineer", "nurse-rn", "operations-manager", "paralegal",
    "product-manager", "project-manager", "real-estate-agent", "recruiter",
    "registered-nurse", "sales-representative", "social-media-manager",
    "software-engineer", "supply-chain-analyst", "teacher-k12", "ux-designer",
    "warehouse-supervisor",
}

CSS = """
:root{--bg:#0d1117;--panel:#161b22;--panel2:#1c2230;--line:#2a313c;--txt:#e6edf3;--muted:#9aa7b5;--accent:#1f6feb;--accent2:#58a6ff;--good:#2ea043;--warn:#d29922;--bad:#da3633;--radius:14px}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:820px;margin:0 auto;padding:28px 20px 60px}
nav.bc{font-size:.85rem;color:var(--muted);margin-bottom:18px}
nav.bc a{color:var(--accent2);text-decoration:none}
h1{font-size:1.9rem;line-height:1.25;margin:.2em 0 .3em}
h2{font-size:1.3rem;margin:1.8em 0 .5em}
h3{font-size:1.05rem;margin:1.2em 0 .4em}
.meta{color:var(--muted);font-size:.92rem;margin-bottom:24px}
p,li{color:#dbe6f3}
a{color:var(--accent2)}
ol.checklist{padding-left:22px}
ol.checklist li{margin:14px 0;padding-left:6px}
ol.checklist li b{color:#fff;display:block;margin-bottom:2px}
.chips{display:flex;flex-wrap:wrap;gap:7px;margin:14px 0 24px}
.chips span{background:var(--panel2);border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:.88rem;color:#c9d6e5}
.rej{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}
.rej b{color:#ff8480;display:block;margin-bottom:4px}
.rej .fix{color:#9aa7b4;font-size:.92rem}
.rej .fix b{color:#4ac26b;display:inline;margin-right:6px}
ul.bullets{padding-left:0;list-style:none}
ul.bullets li{background:var(--panel);border-left:3px solid var(--good);padding:10px 14px;margin:10px 0;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.92rem;color:#dbe6f3;border-radius:6px}
.tool{background:linear-gradient(135deg,#13233f,#1b2b4a);border:1px solid #2c4673;border-radius:var(--radius);padding:22px;margin:28px 0;text-align:center}
.tool h3{margin:.2em 0;font-size:1.2rem}
.btn{display:inline-block;background:var(--accent);color:#fff;text-decoration:none;padding:12px 22px;font-weight:700;border-radius:10px;margin-top:10px}
.btn:hover{background:#388bfd}
details{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin:10px 0}
summary{cursor:pointer;font-weight:600;color:#fff}
details p{margin:10px 0 0}
.cta{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:20px;margin:28px 0}
footer{margin-top:48px;border-top:1px solid var(--line);padding-top:20px;color:var(--muted);font-size:.85rem;text-align:center}
footer a{color:var(--accent2)}
@media(max-width:560px){h1{font-size:1.5rem}.wrap{padding:20px 16px 40px}}
"""

BANNER = '''<div style="background:linear-gradient(90deg,#1f6feb,#3a9d4d);color:#fff;text-align:center;padding:8px 12px;font:600 .92rem -apple-system,sans-serif;border-bottom:1px solid rgba(255,255,255,.2)">
💚 This is free + open source. <a href="https://hugoclaw.gumroad.com/l/ats-quick-fixes" target="_blank" rel="noopener" style="color:#fff;text-decoration:underline">Tip $1–3 on Gumroad (PWYW)</a> · <a href="https://github.com/hugounoclaw/ats-checker" target="_blank" rel="noopener" style="color:#fff;text-decoration:underline">⭐ Star repo</a>
</div>'''

ICON = "<link rel=\"icon\" href=\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%232ea043'/%3E%3Cpath d='M9 16.5l4.5 4.5L23 11' fill='none' stroke='white' stroke-width='3.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E\">"

DATE = "2026-05-29"


def slugify_check(s):
    if not re.match(r'^[a-z0-9\-]+$', s):
        raise ValueError(f"bad slug: {s!r}")


def render_intro(intro):
    """Split intro text into <p> blocks. Accept either string with \n\n or list."""
    if isinstance(intro, list):
        paras = [p.strip() for p in intro if p.strip()]
    else:
        paras = [p.strip() for p in intro.split("\n\n") if p.strip()]
    return "\n".join(f"<p>{escape(p)}</p>" for p in paras)


def render_checklist(items):
    out = []
    for it in items:
        title = escape(it["title"])
        detail = escape(it["detail"])
        out.append(f"  <li><b>{title}</b>{detail}</li>")
    return "\n".join(out)


def render_chips(keywords):
    return "".join(f"<span>{escape(k)}</span>" for k in keywords)


def render_rejections(items):
    out = []
    for it in items:
        reason = escape(it["reason"])
        fix = escape(it["fix"])
        out.append(f'<div class="rej"><b>✗ {reason}</b><div class="fix"><b>Fix:</b>{fix}</div></div>')
    return "\n".join(out)


def render_bullets(bullets):
    return "\n".join(f"  <li>{escape(b)}</li>" for b in bullets)


def render_faq(faq):
    out = []
    for qa in faq:
        q = escape(qa["q"])
        a = escape(qa["a"])
        out.append(f"<details><summary>{q}</summary><p>{a}</p></details>")
    return "\n".join(out)


def build_faq_jsonld(faq):
    entities = []
    for qa in faq:
        entities.append({
            "@type": "Question",
            "name": qa["q"],
            "acceptedAnswer": {"@type": "Answer", "text": qa["a"]},
        })
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities,
    }, separators=(",", ":"))


def build_article_jsonld(slug, role, meta_description):
    url = f"{SITE_BASE}/jobs/{slug}/ats-checklist.html"
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": f"{role} ATS Resume Checklist (2026) — 12 Things to Check Before You Apply",
        "description": meta_description,
        "author": {"@type": "Organization", "name": "Free ATS Resume Checker"},
        "datePublished": DATE,
        "dateModified": DATE,
        "mainEntityOfPage": url,
    }, separators=(",", ":"))


def derive_meta_description(role, role_plural, keywords):
    """Auto-derive meta description — role + first 3 keywords + tail."""
    kw_sample = ", ".join(keywords[:3]) if len(keywords) >= 3 else ", ".join(keywords)
    return (f"The 12 ATS resume checks {role_plural} need to pass in 2026: "
            f"section formatting, {kw_sample} keyword targeting, role-specific "
            f"failure modes, and three example bullets to copy. Free 30-second checker.")


def derive_tagline(role, role_plural):
    return (f"12 ATS-resume checks {role_plural} need to pass in 2026, the keywords "
            f"recruiters scan for, and three role-specific resume bullets to copy.")


def maybe_kw_link(slug):
    if slug in EXISTING_KW_SLUGS:
        return f' · <a href="../../keywords-by-role/{slug}.html">Full keyword list for this role →</a>'
    return ""


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{icon}
<title>{title}</title>
<meta name="description" content="{meta_description}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#0d1117">
<meta property="og:type" content="article">
<meta property="og:title" content="{role} ATS Resume Checklist (2026)">
<meta property="og:description" content="{og_description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{site_base}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{site_base}/og.png">
<script type="application/ld+json">{article_jsonld}</script>
<script type="application/ld+json">{faq_jsonld}</script>
<style>{css}</style>
</head>
<body>
{banner}
<div class="wrap">
<nav class="bc"><a href="../../">ATS Resume Checker</a> › <a href="../">Jobs</a> › {role}</nav>
<h1>{role} ATS Resume Checklist (2026)</h1>
<p class="meta">{tagline}</p>

{intro_html}

<h2>The 12-point ATS checklist for {role_plural}</h2>
<ol class="checklist">
{checklist_html}
</ol>

<h2>Role-specific keywords ATS scans for</h2>
<p>These terms recur across current 2026 {role} job descriptions on Indeed, LinkedIn, and Greenhouse. Weave the genuine ones (those you have actually used) into your experience bullets — keywords in narrative context outrank keyword dumps in a Skills section.</p>
<div class="chips">{chips_html}</div>

<h2>Common ATS rejection reasons for {role_plural}</h2>
{rejections_html}

<h2>Three example resume bullets for a {role}</h2>
<p>Patterns a strong {role} bullet should hit: action verb at the start, role-specific noun in the middle, measurable number at the end. Adapt these to your real work; do not copy verbatim.</p>
<ul class="bullets">
{bullets_html}
</ul>

<div class="tool">
  <h3>Check your {role} resume in 30 seconds — free</h3>
  <p>Instant 0–100 ATS score + keyword match against any job description + prioritized fixes. Runs in your browser; nothing uploaded.</p>
  <a class="btn" href="../../?from=jobs-{slug}">Run my resume free →</a>
</div>

<h2>FAQ — {role} ATS questions</h2>
{faq_html}

<div class="cta">
<p><strong>Want done-for-you templates?</strong> The <a href="https://hugoclaw.gumroad.com/l/ats-kit?from=jobs-{slug}" target="_blank" rel="noopener">ATS Resume Kit</a> ($12, pay what feels fair from $3) ships ATS-safe .docx + Google Docs templates, a 150+ industry-keyword cheat-sheet, and a cover-letter prompt pack you can use the same day.</p>
<p><strong>Or grab the free 1-page checklist:</strong> <a href="https://hugoclaw.gumroad.com/l/ats-quick-fixes?from=jobs-{slug}" target="_blank" rel="noopener">ATS Quick Fixes Checklist</a> (free PDF).</p>
</div>

<p style="text-align:center;font-size:.92rem;color:#9aa7b5;margin:24px 0"><a href="../../keyword-extractor.html">🔑 JD Keyword Extractor</a> · <a href="../../guides/how-ats-works.html">How ATS Works</a> · <a href="../../best-ats-resume-checkers.html">Compare 6 ATS checkers</a>{maybe_kw}</p>

<p style="text-align:center;color:#9aa7b5;font-size:.9rem;margin:18px 0">⭐ Free + open source. <a href="https://github.com/hugounoclaw/ats-checker" target="_blank" rel="noopener">Star the repo on GitHub</a> so more {role_plural} can find this.</p>

<footer>
<p><a href="../">← All 50 roles</a> · <a href="../../">Free ATS Checker</a> · <a href="../../guides/">All guides</a> · <a href="https://github.com/hugounoclaw/ats-checker" target="_blank" rel="noopener">⭐ Star repo</a></p>
</footer>
</div>
</body>
</html>
"""


def render_page(role):
    slug = role["slug"]
    slugify_check(slug)
    role_display = role["role"]
    role_plural = role["role_plural"]
    keywords = role["keywords"]
    meta_description = derive_meta_description(role_display, role_plural, keywords)
    og_description = (f"12 ATS checks {role_plural} need to pass in 2026 + keywords "
                      f"recruiters scan for + 3 example bullets. Free.")
    canonical = f"{SITE_BASE}/jobs/{slug}/ats-checklist.html"
    return PAGE_TEMPLATE.format(
        icon=ICON,
        title=f"{role_display} ATS Resume Checklist (2026) — 12 Things to Check Before You Apply",
        meta_description=escape(meta_description, quote=True),
        canonical=canonical,
        role=escape(role_display),
        role_plural=escape(role_plural),
        og_description=escape(og_description, quote=True),
        site_base=SITE_BASE,
        article_jsonld=build_article_jsonld(slug, role_display, meta_description),
        faq_jsonld=build_faq_jsonld(role["faq"]),
        css=CSS,
        banner=BANNER,
        tagline=derive_tagline(role_display, role_plural),
        intro_html=render_intro(role["intro"]),
        checklist_html=render_checklist(role["checklist"]),
        chips_html=render_chips(keywords),
        rejections_html=render_rejections(role["rejection_reasons"]),
        bullets_html=render_bullets(role["example_bullets"]),
        faq_html=render_faq(role["faq"]),
        slug=slug,
        maybe_kw=maybe_kw_link(slug),
    )


HUB_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{icon}
<title>ATS Resume Checklists by Job Role (2026) — 50 Roles</title>
<meta name="description" content="ATS resume checklists organized by job role. 12 role-specific checks, keywords ATS scans for, common rejection reasons, and example bullets — for 50 roles across tech, healthcare, trades, finance, and more.">
<link rel="canonical" href="{site_base}/jobs/">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#0d1117">
<meta property="og:type" content="website">
<meta property="og:title" content="ATS Resume Checklists by Job Role (2026) — 50 Roles">
<meta property="og:description" content="50 role-specific ATS checklists. Free. Tech, healthcare, trades, finance, ops.">
<meta property="og:url" content="{site_base}/jobs/">
<meta property="og:image" content="{site_base}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{site_base}/og.png">
<style>{css}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;margin:24px 0}}
.role{{display:block;background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px;text-decoration:none;transition:.15s}}
.role:hover{{border-color:var(--accent);transform:translateY(-2px)}}
.role h3{{margin:0;font-size:1.02rem;color:#fff}}
.role p{{margin:4px 0 0;color:var(--muted);font-size:.82rem}}
.cat{{margin-top:28px;color:var(--muted);font-size:.85rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em}}
</style>
</head>
<body>
{banner}
<div class="wrap">
<nav class="bc"><a href="../">ATS Resume Checker</a> › Jobs</nav>
<h1>ATS Resume Checklists by Job Role</h1>
<p class="meta">12-point ATS checklists, role-specific keywords, rejection reasons, and example bullets — for 50 job roles. Each list is researched per-role, not template-swapped.</p>

<div class="tool">
  <h3>Want one number first? Run your resume through the free checker</h3>
  <p>0–100 ATS score + keyword match in 30 seconds. Runs in your browser; nothing uploaded.</p>
  <a class="btn" href="../">Free ATS Checker →</a>
</div>

{categories_html}

<footer>
<p><a href="../">Free ATS Checker</a> · <a href="../guides/">Guides</a> · <a href="../keywords-by-role/">Keywords by role</a> · <a href="https://github.com/hugounoclaw/ats-checker" target="_blank" rel="noopener">⭐ Star the repo</a></p>
</footer>
</div>
</body>
</html>
"""

# Grouping for the hub (purely visual)
HUB_CATEGORIES = [
    ("Tech & Engineering", [
        "software-engineer", "devops-engineer", "aws-cloud-engineer",
        "site-reliability-engineer", "solutions-architect", "machine-learning-engineer",
        "data-engineer", "qa-engineer", "cybersecurity-analyst", "ux-designer",
        "electrical-engineer", "mechanical-engineer",
    ]),
    ("Data, Product & Marketing", [
        "data-analyst", "business-analyst", "product-manager", "project-manager",
        "graphic-designer", "content-writer", "social-media-manager",
        "marketing-manager", "supply-chain-analyst", "customer-success",
    ]),
    ("Operations, HR, Sales, Education & Legal", [
        "operations-manager", "hr-generalist", "recruiter", "sales-representative",
        "real-estate-agent", "administrative-assistant", "warehouse-supervisor",
        "teacher-k12", "school-counselor", "paralegal",
    ]),
    ("Healthcare", [
        "registered-nurse", "pharmacy-technician", "phlebotomist",
        "medical-assistant", "physical-therapist", "dental-hygienist",
        "radiologic-technologist",
    ]),
    ("Trades", [
        "diesel-mechanic", "hvac-technician", "electrician", "welder",
    ]),
    ("Finance, Tax & Compliance", [
        "accountant", "financial-analyst", "tax-accountant", "financial-advisor",
        "compliance-officer", "risk-analyst", "internal-auditor",
    ]),
]


def render_hub(role_by_slug):
    chunks = []
    for cat_name, slugs in HUB_CATEGORIES:
        cards = []
        for slug in slugs:
            r = role_by_slug.get(slug)
            if not r:
                continue
            cards.append(
                f'<a class="role" href="{slug}/ats-checklist.html"><h3>{escape(r["role"])}</h3>'
                f'<p>12-point ATS checklist · {len(r["keywords"])} keywords · {len(r["faq"])} FAQs</p></a>'
            )
        chunks.append(f'<div class="cat">{escape(cat_name)}</div>\n<div class="grid">\n' + "\n".join(cards) + "\n</div>")
    return HUB_TEMPLATE.format(
        icon=ICON,
        site_base=SITE_BASE,
        css=CSS,
        banner=BANNER,
        categories_html="\n".join(chunks),
    )


def main():
    # Load all batches.
    all_roles = []
    for bf in BATCH_FILES:
        if not bf.exists():
            print(f"MISSING: {bf}", file=sys.stderr)
            sys.exit(2)
        data = json.loads(bf.read_text())
        if not isinstance(data, list):
            print(f"BAD FORMAT: {bf}", file=sys.stderr)
            sys.exit(2)
        all_roles.extend(data)

    if len(all_roles) != 50:
        print(f"WARNING: got {len(all_roles)} roles (expected 50)", file=sys.stderr)

    # Index by slug.
    role_by_slug = {r["slug"]: r for r in all_roles}

    # Render each page.
    urls = []
    for role in all_roles:
        slug = role["slug"]
        out_dir = JOBS_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        page = render_page(role)
        (out_dir / "ats-checklist.html").write_text(page)
        urls.append(f"{SITE_BASE}/jobs/{slug}/ats-checklist.html")

    # Hub page.
    (JOBS_DIR / "index.html").write_text(render_hub(role_by_slug))
    urls.insert(0, f"{SITE_BASE}/jobs/")

    # URL list for IndexNow.
    Path("/tmp/ats-checker-live/jobs_urls.txt").write_text("\n".join(urls) + "\n")

    # Word-count check (warn-only).
    wc_results = []
    for role in all_roles:
        page = render_page(role)
        text = re.sub(r"<[^>]+>", " ", page)
        text = re.sub(r"\s+", " ", text)
        words = len(text.split())
        wc_results.append((role["slug"], words))

    print(f"✓ Wrote {len(all_roles)} role pages + hub")
    print(f"✓ URL list: /tmp/ats-checker-live/jobs_urls.txt ({len(urls)} URLs)")
    print(f"  word-count range: {min(w for _, w in wc_results)} – {max(w for _, w in wc_results)}")
    print(f"  median: {sorted(w for _, w in wc_results)[len(wc_results)//2]}")
    short = [(s, w) for s, w in wc_results if w < 600]
    if short:
        print(f"  ⚠ {len(short)} pages under 600 words:")
        for s, w in short[:10]:
            print(f"     {s}: {w}")


if __name__ == "__main__":
    main()
