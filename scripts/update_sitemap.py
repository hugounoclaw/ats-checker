#!/usr/bin/env python3
"""Append /jobs/ hub + 50 /jobs/{slug}/ats-checklist.html entries to sitemap.xml.

Idempotent — strips any prior /jobs/ entries before re-adding.
"""
import re
from pathlib import Path

REPO = Path("/tmp/ats-checker-live")
SITEMAP = REPO / "sitemap.xml"
URL_LIST = Path("/tmp/ats-checker-live/jobs_urls.txt")
DATE = "2026-05-29"


def main():
    text = SITEMAP.read_text()

    # Strip any existing /jobs/ entries (idempotent re-runs).
    text = re.sub(
        r"  <url><loc>https://hugounoclaw\.github\.io/ats-checker/jobs/[^<]*</loc>[^<]*<lastmod>[^<]*</lastmod>[^<]*<changefreq>[^<]*</changefreq>[^<]*<priority>[^<]*</priority></url>\n?",
        "",
        text,
    )

    urls = [u.strip() for u in URL_LIST.read_text().splitlines() if u.strip()]

    new_lines = []
    for u in urls:
        # hub gets slightly higher priority than per-role pages
        if u.endswith("/jobs/"):
            pri = "0.85"
            cf = "weekly"
        else:
            pri = "0.75"
            cf = "monthly"
        new_lines.append(
            f"  <url><loc>{u}</loc><lastmod>{DATE}</lastmod><changefreq>{cf}</changefreq><priority>{pri}</priority></url>"
        )

    # Insert before </urlset>
    block = "\n".join(new_lines) + "\n"
    text = text.replace("</urlset>", block + "</urlset>")

    SITEMAP.write_text(text)
    print(f"✓ Sitemap: added {len(urls)} /jobs/* entries")


if __name__ == "__main__":
    main()
