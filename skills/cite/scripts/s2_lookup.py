# /// script
# requires-python = ">=3.11"
# dependencies = ["requests"]
# ///
"""Semantic Scholar title lookup — returns BibTeX via /paper/search/match.

Usage:
    uv run s2_lookup.py "Title One" "Title Two" [--key API_KEY]

Output: JSON array to stdout. Each element has:
    - query, status ("success" | "error")
    - On success: title, year, authors, citation_count, bibtex, paper_id, match_score
    - On error: error (message string)
"""

import argparse
import json
import sys
import time

import requests

S2_BASE = "https://api.semanticscholar.org/graph/v1"
FIELDS = "paperId,title,year,authors,citationCount,externalIds,citationStyles"
REQUEST_DELAY = 1


def lookup(title: str, api_key: str | None = None) -> dict:
    sanitized = title.replace("-", " ")
    params = {"query": sanitized, "fields": FIELDS}
    headers = {"x-api-key": api_key} if api_key else {}

    try:
        resp = requests.get(
            f"{S2_BASE}/paper/search/match",
            params=params,
            headers=headers,
            timeout=15,
        )
    except requests.RequestException as exc:
        return {"query": title, "status": "error", "error": f"Connection error: {exc}"}

    if resp.status_code == 404:
        return {"query": title, "status": "error", "error": "No match found (404)"}
    if resp.status_code == 429:
        return {"query": title, "status": "error", "error": "Rate limited (429)"}
    if resp.status_code >= 500:
        return {"query": title, "status": "error", "error": f"Server error ({resp.status_code})"}
    if resp.status_code != 200:
        return {"query": title, "status": "error", "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}

    paper = resp.json()["data"][0]
    authors = [a["name"] for a in paper.get("authors", [])]
    bibtex = (paper.get("citationStyles") or {}).get("bibtex", "")

    return {
        "query": title,
        "status": "success",
        "title": paper.get("title"),
        "year": paper.get("year"),
        "authors": authors,
        "citation_count": paper.get("citationCount"),
        "bibtex": bibtex,
        "paper_id": paper.get("paperId"),
        "match_score": paper.get("matchScore"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Semantic Scholar title → BibTeX lookup")
    parser.add_argument("titles", nargs="+", help="Paper title(s) to look up")
    parser.add_argument("--key", default=None, help="Semantic Scholar API key")
    args = parser.parse_args()

    results = []
    for i, title in enumerate(args.titles):
        results.append(lookup(title, api_key=args.key))
        if i < len(args.titles) - 1:
            time.sleep(REQUEST_DELAY)

    json.dump(results, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
