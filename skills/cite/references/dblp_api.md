# DBLP Search API Reference

> Main server: `https://dblp.org`
> Mirror: `https://dblp.uni-trier.de`
> License: CC0 1.0 (public domain)

DBLP is a curated computer science bibliography with high-quality, human-verified
metadata. It covers conferences, journals, and repositories in CS and related fields.

## Important Caveats

- The API is described by DBLP as **"work-in-progress that may change"**.
- The main server (`dblp.org`) experiences periodic instability (500 errors).
  Always implement mirror fallback to `dblp.uni-trier.de`.
- `format=bib` on the search endpoint does **NOT** work (returns 500).
  BibTeX must be fetched separately via `/rec/{key}.bib`.

---

## Search Endpoints

| Service | URL |
|---------|-----|
| Publications | `/search/publ/api` |
| Authors | `/search/author/api` |
| Venues | `/search/venue/api` |

### Publication Search — `GET /search/publ/api`

```
GET https://dblp.org/search/publ/api?q=Attention+Is+All+You+Need&format=json&h=100
```

**Query Parameters:**

| Param | Type | Default | Max | Description |
|-------|------|---------|-----|-------------|
| `q` | string | (required) | — | Search query |
| `format` | string | `xml` | — | Response format: `xml`, `json`, `jsonp` |
| `h` | int | 30 | 1000 | Maximum number of hits returned |
| `f` | int | 0 | — | First hit offset (0-indexed, for pagination) |
| `c` | int | 10 | 1000 | Maximum completion terms returned |

### Query Syntax

| Feature | Syntax | Example | Notes |
|---------|--------|---------|-------|
| Prefix match | (default) | `sig` matches "SIGIR", "signal" | All terms prefix-matched |
| Exact word | `term$` | `graph$` matches "graph" not "graphics" | Append `$` |
| Boolean AND | space | `codd model` | Both terms required |
| Boolean OR | `\|` | `graph\|network` | Either term |
| Hyphen adjacency | `-` | `hans-peter` | Adjacent words only |
| Phrase search | — | — | **Disabled** |
| Boolean NOT | — | — | **Disabled** |

- All matching is **case-insensitive** and **diacritics-insensitive**.
- The rightmost term gets prefix completion suggestions.

### JSON Response Structure

```json
{
  "result": {
    "query": "Attention* Is All* You* Need*",
    "status": {"@code": "200", "text": "OK"},
    "time": {"@unit": "msecs", "text": "26.84"},
    "completions": {
      "@total": "1", "@computed": "1", "@sent": "1",
      "c": {"@sc": "105", "@dc": "103", "@oc": "105", "@id": "65005050", "text": "need"}
    },
    "hits": {
      "@total": "103",
      "@computed": "100",
      "@sent": "3",
      "@first": "0",
      "hit": [
        {
          "@score": "9",
          "@id": "2445555",
          "info": {
            "authors": {
              "author": [
                {"@pid": "167/1261-9", "text": "Xiaopeng Zhang 0009"},
                {"@pid": "17/8386", "text": "Haoyu Yang"}
              ]
            },
            "title": "Attentional Transfer is All You Need...",
            "venue": "DAC",
            "pages": "169-174",
            "year": "2021",
            "type": "Conference and Workshop Papers",
            "access": "closed",
            "key": "conf/dac/ZhangYY21",
            "doi": "10.1109/DAC18074.2021.9586227",
            "ee": "https://doi.org/10.1109/DAC18074.2021.9586227",
            "url": "https://dblp.org/rec/conf/dac/ZhangYY21"
          }
        }
      ]
    }
  }
}
```

### Hit `info` fields

| Field | Description |
|-------|-------------|
| `authors.author[]` | Array of `{@pid, text}` objects |
| `title` | Publication title (may end with `.`) |
| `venue` | Abbreviated venue name |
| `pages` | Page range |
| `year` | Publication year (string) |
| `type` | `"Conference and Workshop Papers"`, `"Journal Articles"`, etc. |
| `access` | `"open"` or `"closed"` |
| **`key`** | **DBLP record key — used to fetch BibTeX** |
| `doi` | DOI (if available) |
| `ee` | Electronic edition URL |
| `url` | DBLP record page URL |

**Note on `author` field:** When a single author, it may be a dict instead of array.
Always normalize: `if isinstance(authors, dict): authors = [authors]`.

---

## Fetching BibTeX — `GET /rec/{key}.bib`

BibTeX is fetched separately using the `key` from search results.

```
GET https://dblp.org/rec/conf/nips/VaswaniSPUJGKP17.bib
GET https://dblp.org/rec/conf/nips/VaswaniSPUJGKP17.bib?param=1
```

### Format Variants

| `param` | Name | Description |
|---------|------|-------------|
| (omitted) | **Standard** | Full details: editors, complete booktitle, url, timestamp, biburl, bibsource |
| `1` | **Condensed** | Abbreviated venue, minimal fields, no editors |
| `2` | **Crossref** | Uses BibTeX `crossref` field; venue in separate `@proceedings` entry |

### Example: Standard (default)

```bibtex
@inproceedings{DBLP:conf/nips/VaswaniSPUJGKP17,
  author       = {Ashish Vaswani and
                  Noam Shazeer and
                  Niki Parmar and
                  Jakob Uszkoreit and
                  Llion Jones and
                  Aidan N. Gomez and
                  Lukasz Kaiser and
                  Illia Polosukhin},
  editor       = {Isabelle Guyon and
                  Ulrike von Luxburg and
                  Samy Bengio and
                  Hanna M. Wallach and
                  Rob Fergus and
                  S. V. N. Vishwanathan and
                  Roman Garnett},
  title        = {Attention is All you Need},
  booktitle    = {Advances in Neural Information Processing Systems 30: Annual Conference
                  on Neural Information Processing Systems 2017, December 4-9, 2017,
                  Long Beach, CA, {USA}},
  pages        = {5998--6008},
  year         = {2017},
  url          = {https://proceedings.neurips.cc/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html},
  timestamp    = {Thu, 21 Jan 2021 15:15:21 +0100},
  biburl       = {https://dblp.org/rec/conf/nips/VaswaniSPUJGKP17.bib},
  bibsource    = {dblp computer science bibliography, https://dblp.org}
}
```

### Example: Condensed (`?param=1`)

```bibtex
@inproceedings{DBLP:conf/nips/VaswaniSPUJGKP17,
  author    = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and
               Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N. and
               Kaiser, Lukasz and Polosukhin, Illia},
  title     = {Attention is All you Need},
  booktitle = {NeurIPS},
  pages     = {5998--6008},
  year      = {2017}
}
```

### Example: Crossref (`?param=2`)

```bibtex
@inproceedings{DBLP:conf/nips/VaswaniSPUJGKP17,
  author       = {Ashish Vaswani and Noam Shazeer and ...},
  title        = {Attention is All you Need},
  booktitle    = {Advances in Neural Information Processing Systems 30: ...},
  pages        = {5998--6008},
  year         = {2017},
  crossref     = {DBLP:conf/nips/2017},
  url          = {https://proceedings.neurips.cc/paper/2017/hash/...},
  ...
}

@proceedings{DBLP:conf/nips/2017,
  title     = {Advances in Neural Information Processing Systems 30: ...},
  publisher = {...},
  year      = {2017},
  isbn      = {...}
}
```

### Citation Key Convention

DBLP keys follow a strict pattern: `DBLP:<type>/<venue>/<AuthorInitialsYear>`

Examples:
- `DBLP:conf/nips/VaswaniSPUJGKP17` (conference)
- `DBLP:journals/corr/VaswaniSPUJGKP17` (arXiv/CoRR)
- `DBLP:journals/tnn/SmithJ23` (journal)

---

## Other Record Endpoints

| URL | Returns |
|-----|---------|
| `/rec/{key}.html` | Human-readable record page |
| `/rec/{key}.bib` | BibTeX |
| `/rec/{key}.xml` | XML metadata |
| `/rec/{key}.json` | JSON metadata |

---

## Rate Limits & Usage Policy

- **No API key required.** Fully open access.
- **No fixed numeric limit** published, but dynamic throttling is enforced.
- **Recommended pacing:** 1-2 seconds between consecutive requests.
- **Exceeding limits:** Returns `429 Too Many Requests` with `Retry-After` header.
- **Bulk data:** For large-scale needs, download the XML dump from
  `https://dblp.org/xml/release/` instead of using the API.
- Crawling is explicitly permitted as long as rate limits are respected.

---

## Title Search Strategy

DBLP's prefix-matching search is problematic for exact title lookup. Common words
like "attention", "all", "you", "need" expand to many prefix matches, pushing the
exact paper far down the ranked results.

### Recommended approach: search + client-side matching

1. Search with `h=100` (or more) to fetch a large result set.
2. Normalize both the target title and each result title (lowercase, strip punctuation).
3. Find the exact match client-side.
4. Fetch BibTeX using the matched `key`.

```python
def normalize(title: str) -> str:
    return " ".join(
        c for c in title.lower().strip().rstrip(".")
        if c.isalnum() or c == " "
    ).split()

# Compare: normalize(target) == normalize(result_title)
```

### Alternative: add author name to query

Adding a distinctive author surname dramatically improves precision:

```
?q=Attention+Is+All+You+Need+vaswani
```

This returns the Vaswani paper as the top result.

---

## Workflow Summary: Title → BibTeX

```
Step 1: Search
  GET /search/publ/api?q={title}&format=json&h=100

Step 2: Find match
  Iterate hits, compare normalized titles, extract `key`

Step 3: Fetch BibTeX
  GET /rec/{key}.bib              (standard)
  GET /rec/{key}.bib?param=1      (condensed)
  GET /rec/{key}.bib?param=2      (crossref)
```

Mirror fallback: if `dblp.org` returns 500, retry with `dblp.uni-trier.de`.

---

## Additional Resources

| Resource | URL |
|----------|-----|
| FAQ | `https://dblp.org/faq/` |
| Search API FAQ | `https://dblp.org/faq/How+to+use+the+dblp+search+API.html` |
| Crawling policy | `https://dblp.org/faq/Am+I+allowed+to+crawl+the+dblp+website.html` |
| XML dump | `https://dblp.org/xml/release/` |
| RDF dump | `https://dblp.org/rdf/` |
| SPARQL endpoint | `https://sparql.dblp.org` |
| Record lookup | `https://dblp.org/lookup/` |
