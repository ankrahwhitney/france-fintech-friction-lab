from __future__ import annotations

import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
URL_PATTERN = re.compile(r"\[[^]]+\]\((https?://[^)]+)\)")
USER_AGENT = "france-fintech-friction-lab-link-check/1.0"


def _public_urls() -> list[str]:
    urls = {
        match
        for document in DOCUMENTS
        for match in URL_PATTERN.findall(document.read_text(encoding="utf-8"))
    }
    return sorted(urls)


def _check(url: str, attempts: int = 3) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Range": "bytes=0-1023"},
        method="GET",
    )
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.status >= 400:
                    raise RuntimeError(f"HTTP {response.status}")
                return
        except (OSError, RuntimeError, urllib.error.URLError) as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(2**attempt)
    raise RuntimeError(f"{url}: {last_error}")


def main() -> int:
    failures: list[str] = []
    urls = _public_urls()
    for url in urls:
        try:
            _check(url)
            print(f"OK  {url}")
        except RuntimeError as error:
            failures.append(str(error))
            print(f"FAIL  {error}", file=sys.stderr)
    if failures:
        print(f"\n{len(failures)} of {len(urls)} external links failed.", file=sys.stderr)
        return 1
    print(f"\nChecked {len(urls)} external links.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
