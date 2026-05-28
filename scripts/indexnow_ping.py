#!/usr/bin/env python3
"""Submit /jobs/* URLs to IndexNow."""
import json
import urllib.request
import urllib.error
from pathlib import Path

KEY = "8fcd04f329f24ed421abd525983c516c"
URL_LIST = Path("/tmp/ats-checker-live/jobs_urls.txt")


def main():
    urls = [u.strip() for u in URL_LIST.read_text().splitlines() if u.strip()]
    body = {
        "host": "hugounoclaw.github.io",
        "key": KEY,
        "keyLocation": f"https://hugounoclaw.github.io/ats-checker/{KEY}.txt",
        "urlList": urls,
    }
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            print(f"✓ IndexNow status={resp.status} urls={len(urls)}")
            body = resp.read().decode(errors="replace")
            if body:
                print(f"  body: {body[:300]}")
    except urllib.error.HTTPError as e:
        print(f"✗ IndexNow HTTP {e.code}: {e.read().decode(errors='replace')[:300]}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
