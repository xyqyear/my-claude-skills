# Semantic Scholar Academic Graph (S2AG) API Reference

> Base URL: `https://api.semanticscholar.org/graph/v1`
> Corpus: 214M papers, 2.49B citations, 79M authors

## Authentication

| Header | Value |
|--------|-------|
| `x-api-key` | Your API key (case-sensitive) |

Get a free key at <https://www.semanticscholar.org/product/api> (delivered by email).

### Rate Limits

| Tier | Limit |
|------|-------|
| Unauthenticated | 1 req/s shared across ALL anonymous users |
| Authenticated | 1 req/s per key (elevated limits available on request) |

- `429` = rate limited, slow down
- `403` = incorrect API key
- Implement exponential backoff for `5xx` errors

---

## Paper Endpoints

### 1. Title Match — `GET /paper/search/match`

Returns the **single best-matching paper** for a given title. This is the
recommended endpoint for "title → BibTeX" workflows.

```
GET /graph/v1/paper/search/match?query=Attention+Is+All+You+Need&fields=title,year,authors,citationStyles
```

**Query Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | yes | Plain-text title. Replace hyphens with spaces to avoid tokenization failures. |
| `fields` | string | no | Comma-separated field list (default: `paperId,title`) |
| `year` | string | no | Filter: `"2019"`, `"2016-2020"`, `"2010-"`, `"-2015"` |
| `publicationDateOrYear` | string | no | Date range `YYYY-MM-DD:YYYY-MM-DD` |
| `publicationTypes` | string | no | Comma-separated: `Review`, `JournalArticle`, `Conference`, `Book`, etc. |
| `openAccessPdf` | flag | no | Present = filter for open access only |
| `minCitationCount` | int | no | Minimum citation threshold |
| `venue` | string | no | Comma-separated venue names or ISO4 abbreviations |
| `fieldsOfStudy` | string | no | Comma-separated: `Computer Science`, `Medicine`, `Physics`, etc. |

**Response** (`PaperMatch`):

```json
{
  "data": [
    {
      "paperId": "204e3073870fae3d05bcbc2f6a8e263d9b72e776",
      "title": "Attention is All you Need",
      "matchScore": 132.72,
      "year": 2017,
      "authors": [
        {"authorId": "1234", "name": "Ashish Vaswani"},
        ...
      ],
      "citationStyles": {
        "bibtex": "@Article{Vaswani2017AttentionIA,\n author = {...},\n ...}"
      }
    }
  ]
}
```

- `matchScore`: confidence of the title match (higher = better)
- Returns **404** `{"error": "Title match not found"}` if no confident match

**Known quirk:** Hyphens in the query title cause tokenization misalignment.
Always pre-process: `title.replace("-", " ")`.

---

### 2. Relevance Search — `GET /paper/search`

Returns a paginated, relevance-ranked list of papers.

```
GET /graph/v1/paper/search?query=transformer+attention&fields=title,year,citationStyles&limit=10
```

**Additional parameters** (beyond those in `/search/match`):

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `offset` | int | 0 | Pagination start position |
| `limit` | int | 100 | Results per page (max: 100) |

**Response** (`PaperRelevanceSearchBatch`):

```json
{
  "total": 7148,
  "offset": 0,
  "next": 10,
  "data": [ ... ]
}
```

- `total`: approximate match count
- `next`: offset for next page; **absent when no more results**
- Max 1,000 relevance-ranked results reachable via pagination
- 10 MB response size limit

---

### 3. Paper by ID — `GET /paper/{paper_id}`

Direct lookup by any supported identifier format.

```
GET /graph/v1/paper/ARXIV:1706.03762?fields=title,citationStyles
```

**Supported ID formats:**

| Format | Example |
|--------|---------|
| S2 hash | `649def34f8be52c8b66281af98ae884c09aef38b` |
| `CorpusId:<id>` | `CorpusId:215416146` |
| `DOI:<doi>` | `DOI:10.18653/v1/N18-3011` |
| `ARXIV:<id>` | `ARXIV:1706.03762` |
| `MAG:<id>` | `MAG:112218234` |
| `ACL:<id>` | `ACL:W12-3903` |
| `PMID:<id>` | `PMID:33184234` |
| `PMCID:<id>` | `PMCID:PMC7927074` |
| `URL:<url>` | `URL:https://arxiv.org/abs/2106.15928` |

Supported URL domains: `semanticscholar.org`, `arxiv.org`, `aclweb.org`, `acm.org`, `biorxiv.org`.

---

### 4. Paper Batch — `POST /paper/batch`

Retrieve up to 500 papers in one request.

```
POST /graph/v1/paper/batch?fields=title,citationStyles
Content-Type: application/json

{"ids": ["ARXIV:1706.03762", "DOI:10.18653/v1/N18-3011"]}
```

- `fields` is a **query parameter**, not in the POST body
- Max 500 IDs per request, 10 MB response limit

---

### 5. Bulk Search — `GET /paper/search/bulk`

Non-relevance-ranked search with boolean query syntax. For large-scale data retrieval.

```
GET /graph/v1/paper/search/bulk?query="attention is all you need"&fields=title,year
```

**Boolean query syntax** (different from `/paper/search`):

| Operator | Meaning | Example |
|----------|---------|---------|
| `+` | AND | `attention +transformer` |
| `\|` | OR | `attention \| self-attention` |
| `-` | NOT | `attention -image` |
| `"..."` | Phrase | `"attention is all"` |
| `*` | Prefix wildcard | `transform*` |
| `()` | Grouping | `(attention \| self-attention) +transformer` |
| `~N` | Edit distance | `attenton~1` |

**Pagination** uses continuation `token` (not `offset`):

```json
{
  "total": 50000,
  "token": "CONTINUATION_TOKEN",
  "data": [ ... ]
}
```

- Pass `token` as query param for next batch
- Max 1,000 papers per call, 10M total via continuation
- `sort` param: `"citationCount:desc"`, `"publicationDate:asc"`, etc.

---

### 6. Citations & References

```
GET /graph/v1/paper/{paper_id}/citations?fields=title,authors,year&offset=0&limit=100
GET /graph/v1/paper/{paper_id}/references?fields=title,authors,year&offset=0&limit=100
```

Citation responses include extra fields: `contexts` (text snippets), `intents` (array),
`isInfluential` (boolean).

---

### 7. Other Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/paper/autocomplete?query=att` | GET | Query completion suggestions (100 char max) |
| `/author/{id}` | GET | Author details |
| `/author/search?query=name` | GET | Search authors (max 1,000 results) |
| `/author/batch` | POST | Batch author lookup (max 1,000) |
| `/author/{id}/papers` | GET | Papers by author |
| `/snippet/search?query=...` | GET | ~500-word text excerpts from papers |

---

## Available Paper Fields

Pass these as comma-separated values in the `fields` query parameter.

### Core fields

| Field | Type | Notes |
|-------|------|-------|
| `paperId` | string | Always returned (S2 hash) |
| `corpusId` | int64 | Secondary numerical ID |
| `externalIds` | object | `{DBLP, MAG, ACL, DOI, ArXiv, PubMed, ...}` |
| `url` | string | Semantic Scholar URL |
| `title` | string | Returned by default with `paperId` |
| `abstract` | string | |
| `venue` | string | Publication venue |
| `publicationVenue` | object | `{id, name, type, alternate_names, url}` |
| `year` | int | Publication year |
| `referenceCount` | int | |
| `citationCount` | int | |
| `influentialCitationCount` | int | |
| `isOpenAccess` | bool | |
| `openAccessPdf` | object | `{url, status, license, disclaimer}` |
| `fieldsOfStudy` | array | Field labels |
| `s2FieldsOfStudy` | array | `[{category, source}]` |
| `publicationTypes` | array | |
| `publicationDate` | string | `YYYY-MM-DD` |
| `journal` | object | `{name, volume, pages}` |

### Citation / BibTeX

| Field | Type | Notes |
|-------|------|-------|
| **`citationStyles`** | object | Contains `bibtex` subfield |
| **`citationStyles.bibtex`** | string | Pre-formatted BibTeX string |

### Nested / Expensive fields

| Field | Type | Notes |
|-------|------|-------|
| `authors` | array | `[{authorId, name}]` |
| `authors.url` | | Dot notation for nested author fields |
| `authors.affiliations` | | |
| `authors.hIndex` | | |
| `citations` | array | Papers citing this one |
| `references` | array | Papers cited by this one |
| `embedding.specter_v1` | object | SPECTER v1 vector |
| `embedding.specter_v2` | object | SPECTER v2 vector |
| `tldr` | object | `{model, text}` — auto-generated summary |

---

## Error Responses

| Code | Meaning | Example |
|------|---------|---------|
| 400 | Bad request | `{"error": "Unrecognized or unsupported fields: [xxx]"}` |
| 400 | Response too large | `{"error": "Response would exceed maximum size..."}` |
| 403 | Bad API key | Incorrect `x-api-key` |
| 404 | Not found | `{"error": "Paper not found"}` or `{"error": "Title match not found"}` |
| 429 | Rate limited | Too many requests |

---

## Practical Notes

1. **Title → BibTeX (simplest path):** Use `/paper/search/match` with `fields=citationStyles`.
   One request, one result, BibTeX included.

2. **Hyphen bug:** Always replace `-` with spaces in the query string before sending.

3. **Rate limiting without a key:** The 1 req/s is shared globally across all anonymous
   callers. In practice you will hit 429 frequently. Always get an API key.

4. **BibTeX quality:** The returned BibTeX uses `@Article` entry type regardless of actual
   type. Citation key format: `AuthorYYYYTitleAbbrev` (e.g., `Vaswani2017AttentionIA`).
   Fields included: `author`, `booktitle`/`journal`, `pages`, `title`, `year`.
   DOI and URL are **not** included — retrieve from `externalIds` if needed.

5. **Data freshness:** S2AG crawls and indexes with some delay. Very recently published
   papers may not yet appear. For cutting-edge papers, combine with Crossref or arXiv.
