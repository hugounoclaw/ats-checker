#!/usr/bin/env python3
"""Add a single /jobs/ link to the footer of every existing HTML page.

Idempotent — checks for marker before inserting.
"""
import re
from pathlib import Path

REPO = Path("/tmp/ats-checker-live")
MARKER = "JOBS_HUB_LINK"  # comment marker so we don't double-insert

# Skip pages we're generating ourselves.
SKIP_DIRS = {REPO / "jobs"}


def rel_jobs_link(path: Path) -> str:
    depth = len(path.relative_to(REPO).parts) - 1
    prefix = "../" * depth
    return f"{prefix}jobs/"


def patch(path: Path) -> bool:
    text = path.read_text()
    if MARKER in text:
        return False
    if "</footer>" not in text:
        return False
    link = rel_jobs_link(path)
    insert = (f'  <p style="margin-top:8px;font-size:.82rem"><!-- {MARKER} -->'
              f'<a href="{link}">→ ATS resume checklists by role (50 roles)</a></p>\n')
    new_text = text.replace("</footer>", insert + "</footer>", 1)
    if new_text == text:
        return False
    path.write_text(new_text)
    return True


def main():
    changed = 0
    for html in REPO.rglob("*.html"):
        if any(html.is_relative_to(d) for d in SKIP_DIRS):
            continue
        if patch(html):
            changed += 1
            print(f"+ {html.relative_to(REPO)}")
    print(f"✓ Patched {changed} footers")


if __name__ == "__main__":
    main()
