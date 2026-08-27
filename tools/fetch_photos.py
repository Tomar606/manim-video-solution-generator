"""Find real photographs that are actually licensed for a commercial reel.

    python tools/fetch_photos.py <subjects.json> <out_dir>

WHY NOT JUST GENERATE EVERYTHING
--------------------------------
For most topics a generated image is the only option. For corrosion it is the
worse one: rust pitting, the spangle crystals on galvanised sheet and the
specific look of chrome plating are textures image models smooth away, and the
student has seen the real thing. A photograph teaches here.

WHY NOT JUST DOWNLOAD ANYTHING
------------------------------
These reels are distributed commercially. An image lifted off a search page is
someone's copyright and the licence is usually "no". So this searches Wikimedia
Commons, reads each file's machine-readable licence, and KEEPS ONLY the licences
that permit commercial use and modification. Everything else is discarded, even
if it is the better picture.

Attribution is not optional for CC-BY and CC-BY-SA: the author, the licence and
the file page are written to credits.json beside the images, so the credit can
be put on the end card or in the description. Public-domain and CC0 files need
no credit but are recorded anyway, so the sourcing can be audited later.

Anything this cannot find, generate instead — that is the fallback, not the
default.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
UA = "arivihan-edu-pipeline/1.0 (educational video sourcing; contact via repo)"

# Licences that allow commercial use AND modification (we crop and letterbox).
# Deliberately does NOT include the NC or ND variants: "educational" is not a
# get-out, the videos are sold.
OK_LICENCES = {
    "public domain", "cc0", "cc pd", "no restrictions",
    "cc by 1.0", "cc by 2.0", "cc by 2.5", "cc by 3.0", "cc by 4.0",
    "cc by-sa 1.0", "cc by-sa 2.0", "cc by-sa 2.5", "cc by-sa 3.0",
    "cc by-sa 4.0", "cc-by-sa-3.0", "cc-by-sa-4.0", "cc-by-4.0",
}
NEEDS_CREDIT = ("by",)          # CC-BY / CC-BY-SA must name the author


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def _clean(html: str | None) -> str:
    """extmetadata values arrive as HTML fragments."""
    if not html:
        return ""
    import re
    return re.sub(r"<[^>]+>", "", html).strip()


def search(query: str, limit: int = 6) -> list[dict]:
    q = urllib.parse.urlencode({
        "action": "query", "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}", "gsrnamespace": "6",
        "gsrlimit": str(limit * 3), "prop": "imageinfo",
        "iiprop": "url|extmetadata|size", "iiurlwidth": "1600",
        "format": "json",
    })
    data = json.loads(_get(f"{API}?{q}"))
    out = []
    for page in (data.get("query", {}).get("pages", {}) or {}).values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {})
        lic = _clean(meta.get("LicenseShortName", {}).get("value")).lower()
        if lic not in OK_LICENCES:
            continue
        if info.get("width", 0) < 800:          # too small to fill the band
            continue
        out.append({
            "title": page["title"],
            "url": info.get("thumburl") or info.get("url"),
            "page": info.get("descriptionurl", ""),
            "licence": _clean(meta.get("LicenseShortName", {}).get("value")),
            "author": _clean(meta.get("Artist", {}).get("value")) or "unknown",
            "credit_required": any(k in lic for k in NEEDS_CREDIT),
        })
        if len(out) >= limit:
            break
    return out


def run(subjects: list[dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    credits: dict[str, list[dict]] = {}
    for s in subjects:
        slug, query = s["slug"], s["query"]
        try:
            hits = search(query, s.get("limit", 4))
        except Exception as e:                          # noqa: BLE001
            print(f"  ! {slug}: search failed ({type(e).__name__}) — generate this one")
            continue
        if not hits:
            print(f"  ! {slug}: nothing freely licensed — generate this one")
            continue
        kept = []
        for i, h in enumerate(hits, 1):
            dest = out_dir / f"{slug}-{i}.jpg"
            try:
                dest.write_bytes(_get(h["url"]))
            except Exception as e:                      # noqa: BLE001
                print(f"    ! {slug}-{i} download failed ({type(e).__name__})")
                continue
            kept.append(dict(h, file=dest.name))
            time.sleep(0.4)                             # be polite to Commons
        credits[slug] = kept
        need = sum(1 for k in kept if k["credit_required"])
        print(f"  {slug}: {len(kept)} candidate(s), {need} need a credit line")
    (out_dir / "credits.json").write_text(
        json.dumps(credits, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\ncredits -> {out_dir / 'credits.json'}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    run(json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2]))
