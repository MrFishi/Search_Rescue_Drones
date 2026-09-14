---
name: find-refs
description: "Find supporting references for a claim, paragraph, or section and propose exactly where to place citations. Checks references.bib and the Zotero library first, then searches the literature for genuine gaps. Never invents a citation, DOI, or cite key. Use whenever a draft has claims needing support or the author asks for more references."
---

# Find References & Citation Placement

## Purpose

Turn "this claim needs backing" into a concrete citation plan: which existing source
to cite and where, or — for real gaps — which new source to add. Supports the
author's revision loop; pairs with `evaluate`, which flags where citations are missing.

## When to use

- After `evaluate` flags missing-citation spots.
- The author wants to strengthen a section's literature grounding.
- A specific claim needs a source and the author isn't sure one exists in the library.

## Inputs

- The claim, paragraph, or section needing support.
- `thesis/references.bib` (the Better BibTeX auto-export — the only source of valid keys).
- The Zotero library, if a Zotero MCP is connected, for searching beyond the bib.

## Procedure

1. **Search `references.bib` first.** For each claim, find whether an existing entry
   already supports it. If so, propose the exact `\cite{key}` and the precise sentence
   it attaches to.
2. **For claims with no matching entry,** search the literature — the Zotero library
   via MCP if available, otherwise the web. Prefer peer-reviewed and primary sources
   (journal papers, conference proceedings, standards, dataset papers) over blogs,
   forums, or SEO content. For this project, weight sources on aerial/SAR detection,
   occlusion, small-object detection, edge inference, and open-vocabulary/VLM detection.
3. **Assess fit honestly.** Only propose a source if it actually says what the claim
   needs. If you can't confirm that, say so rather than citing it speculatively.
4. **Output a placement table** (see format below).
5. **For anything not yet in the bib,** give full reference details (authors, title,
   venue, year, DOI) so the author can add it via Zotero, which regenerates
   `references.bib`. Mark it "needs adding" — do not write the bib entry or invent a key.

## Output format

A table with columns: *claim/sentence → suggested source → in references.bib? (key or
"needs adding") → proposed `\cite` placement*. Follow with a short list of full
reference details for every "needs adding" item.

## Hard rules

- **Never fabricate a reference, DOI, author list, or cite key.** This is the single
  most important rule; a hallucinated citation in a thesis is a serious integrity failure.
- **Only emit `\cite` keys that exist in `references.bib`.** For new sources, output
  "needs adding" plus the real details, never a guessed key.
- **Do not over-cite.** One strong source beats three weak ones. Explicitly flag
  claims that are fine as the author's own reasoning and need no citation.
- Respect citation norms: a method choice cites the method's originating paper; a
  claim about prior empirical results cites those results; a dataset use cites the
  dataset paper.
- **Citation style is IEEE** (numbered, `[1]`, in order of first appearance — not
  author-year). When proposing placement, give the in-text form as `[cite:key]` for
  the author to number once `\bibliographystyle{ieeetr}` (or equivalent) resolves
  order; don't assume or assign a fixed number yourself, since it depends on final
  document order.
