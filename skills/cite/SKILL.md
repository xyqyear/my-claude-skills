---
name: cite
description: Find academic paper citations and BibTeX entries by title. Use when users need to look up papers, generate BibTeX citations, or find references for academic writing.
user-invokable: true
---

# Academic Citation Finder

Look up academic papers by title and return BibTeX citations.

## Input

Parse paper title(s) from `$ARGUMENTS` or conversation context. Accept:
- A single title: `/cite Attention Is All You Need`
- Multiple titles separated by newlines or semicolons
- A list provided in conversation

## Workflow

### 1. Check for Semantic Scholar API key

Look back in conversation for a user-provided S2 API key. If found, pass it via `--key`. If not found, proceed without one (unauthenticated requests are slower but functional).

### 2. Run Semantic Scholar lookup

Run the S2 script with all titles at once:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/s2_lookup.py "Title One" "Title Two" --key API_KEY
```

Omit `--key` if no API key is available.

Parse the JSON array output. Each element has `status: "success"` or `status: "error"`.

### 3. Fall back to DBLP for failures

Collect any titles where S2 returned `status: "error"`. If there are failures, run them through DBLP:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/dblp_lookup.py "Failed Title One" "Failed Title Two"
```

Optional flags: `--bib-format standard|condensed|crossref`.

Parse the JSON array output.

### 4. Verify results

After each lookup, compare the returned title against the intended paper. The APIs sometimes return a different paper with a similar title (e.g., "Multimodal Attention Is All You Need" instead of "Attention Is All You Need"). If the returned paper is not the intended one, retry the query by appending disambiguating information such as the first author's surname or the publication year:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/s2_lookup.py "Attention Is All You Need Vaswani 2017"
```

### 5. Present results

For each title, present:

1. **BibTeX block** in a fenced code block with `bibtex` language tag
2. **Metadata summary**: title, authors (first 3 + "et al." if more), year, citation count (S2 only), source (Semantic Scholar or DBLP)
3. **Match confidence**: for DBLP results, note if `match_type` is `"best_available"` rather than `"exact"` — warn the user to verify

For any titles that failed both sources, list them clearly and suggest:
- Check spelling / try alternate title forms
- The paper may be too recent, non-CS (DBLP), or not yet indexed

If the user provided a single title and it succeeded, present just the BibTeX block and a one-line metadata summary.

## Notes

- DBLP only covers computer science. For other fields, S2 is the only option.
- S2 BibTeX always uses `@Article` entry type regardless of actual publication type. DBLP BibTeX is more accurate in entry types.
- If the user asks for a specific BibTeX format from DBLP (condensed, crossref), pass `--bib-format` accordingly.
- Reference docs are available at `${CLAUDE_PLUGIN_ROOT}/references/` if you need to troubleshoot API issues.
