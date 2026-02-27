# /// script
# requires-python = ">=3.11"
# dependencies = ["requests"]
# ///
"""DBLP title lookup — search + client-side match + fetch BibTeX.

Usage:
    uv run dblp_lookup.py "Title One" "Title Two" [--max-hits 200] [--bib-format standard|condensed|crossref]

Output: JSON array to stdout. Each element has:
    - query, status ("success" | "error")
    - On success: title, year, authors, venue, bibtex, dblp_key, match_type
    - On error: error (message string)
"""

import argparse
import json
import re
import sys
import time
import unicodedata

import requests

DBLP_SERVERS = [
    "https://dblp.org",
    "https://dblp.uni-trier.de",
]

BIB_PARAM = {"standard": None, "condensed": 1, "crossref": 2}

REQUEST_DELAY = 1


def _dblp_get(path: str, params: dict | None = None, **kwargs) -> requests.Response:
    last_exc = None
    for base in DBLP_SERVERS:
        url = f"{base}{path}"
        try:
            resp = requests.get(url, params=params, timeout=15, **kwargs)
            if resp.status_code != 500:
                return resp
        except requests.RequestException as exc:
            last_exc = exc
    if last_exc:
        raise last_exc
    raise RuntimeError("All DBLP mirrors returned 500")


def normalize_title(title: str) -> str:
    title = unicodedata.normalize("NFKD", title)
    title = title.lower()
    title = re.sub(r"[^a-z0-9\s]", "", title)
    return " ".join(title.split())


def search_publications(query: str, max_hits: int = 200) -> list[dict]:
    params = {"q": query, "format": "json", "h": max_hits, "f": 0}
    resp = _dblp_get("/search/publ/api", params=params)
    resp.raise_for_status()

    result = resp.json().get("result", {})
    hits = result.get("hits", {}).get("hit", [])
    if isinstance(hits, dict):
        hits = [hits]

    papers = []
    for hit in hits:
        info = hit.get("info", {})
        authors_raw = info.get("authors", {}).get("author", [])
        if isinstance(authors_raw, dict):
            authors_raw = [authors_raw]

        papers.append({
            "score": hit.get("@score"),
            "key": info.get("key"),
            "title": info.get("title"),
            "venue": info.get("venue"),
            "year": info.get("year"),
            "type": info.get("type"),
            "doi": info.get("doi"),
            "authors": [a.get("text", "") for a in authors_raw],
        })
    return papers


def find_best_match(papers: list[dict], target_title: str) -> tuple[dict | None, str]:
    norm_target = normalize_title(target_title)
    for p in papers:
        raw = p.get("title", "")
        if normalize_title(raw) == norm_target:
            return p, "exact"
    return (papers[0] if papers else None), "best_available"


def fetch_bibtex(key: str, bib_format: str = "standard") -> str:
    path = f"/rec/{key}.bib"
    param = BIB_PARAM.get(bib_format)
    params = {"param": param} if param is not None else None
    resp = _dblp_get(path, params=params)
    resp.raise_for_status()
    return resp.text


def lookup(title: str, max_hits: int = 200, bib_format: str = "standard") -> dict:
    try:
        papers = search_publications(title, max_hits=max_hits)
    except Exception as exc:
        return {"query": title, "status": "error", "error": f"Search failed: {exc}"}

    if not papers:
        return {"query": title, "status": "error", "error": "No results found"}

    match, match_type = find_best_match(papers, title)
    if match is None:
        return {"query": title, "status": "error", "error": "No results found"}

    key = match.get("key")
    if not key:
        return {"query": title, "status": "error", "error": "Result has no DBLP key"}

    time.sleep(REQUEST_DELAY)

    try:
        bibtex = fetch_bibtex(key, bib_format=bib_format)
    except Exception as exc:
        return {"query": title, "status": "error", "error": f"BibTeX fetch failed: {exc}"}

    return {
        "query": title,
        "status": "success",
        "title": match.get("title"),
        "year": match.get("year"),
        "authors": match.get("authors", []),
        "venue": match.get("venue"),
        "bibtex": bibtex.strip(),
        "dblp_key": key,
        "match_type": match_type,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="DBLP title → BibTeX lookup")
    parser.add_argument("titles", nargs="+", help="Paper title(s) to look up")
    parser.add_argument("--max-hits", type=int, default=200, help="Max search hits (default: 200)")
    parser.add_argument("--bib-format", choices=["standard", "condensed", "crossref"], default="standard",
                        help="BibTeX format variant (default: standard)")
    args = parser.parse_args()

    results = []
    for i, title in enumerate(args.titles):
        results.append(lookup(title, max_hits=args.max_hits, bib_format=args.bib_format))
        if i < len(args.titles) - 1:
            time.sleep(REQUEST_DELAY)

    json.dump(results, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
