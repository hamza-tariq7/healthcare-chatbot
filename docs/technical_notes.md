> Historical context: this document describes the original recorded analysis. The current notebook contains code corrections; see [revision notes](revision_notes.md). Published benchmark figures have not been replaced by a rerun.

# Implementation and evaluation context

## Project-reported outcomes

The original presentation reports query resolution under ten seconds, compared with a 15–45-minute manual workflow; under 2% hallucination for the retrieval-assisted mode; 10–15% hallucination on unblocked LLM-only queries; and approximately 40–50% abstention on ambiguous queries. The project owner states that these were tested project results.

Those figures are included in the README as project-reported outcomes, attributed to the presentation. This portfolio update did not reproduce that benchmark. The attachments do not include a full graded response file, timing logs, ground-truth annotations, or denominators for each reported percentage. The supplied notebook's auto-score summary is a separate artifact whose scoring rules are described below.

## Implemented answer paths

| Component | Supplied implementation |
| --- | --- |
| Structured sources | Four synthetic CSV tables |
| Document retrieval | TF-IDF vectors and cosine similarity over PDF text chunks |
| Mode 0 | Raw operational rows or PDF excerpts |
| Mode 1 | Deterministic retrieval, stock ranking, and templated answers with citations |
| Mode 2 | Qwen2.5-1.5B-Instruct, with an operational-query guard before generation |

The presentation's RAG label describes the retrieval-assisted concept. The supplied Mode 1 function does not call the Qwen generator. The model loaded by code is 1.5B rather than the 7B model stated in a slide. The separate reference demo uses dense embeddings and FAISS, but those are not the hospital notebook's retriever.

## Data scale and schema

The saved load output records 8,000 drug catalog entries, 200,000 inventory lots, 80 locations, and 8,000 cost-contract rows. Catalog entries represent combinations of ingredients, strengths, packaging, and routes rather than 8,000 unique active ingredients. The 80 locations belong to three simulated facilities. Vendor labels, prices, product attributes, and stock quantities are simulated.

The saved document build reports 6,383 passages. PDF text is grouped by page and assigned document, page, and chunk identifiers. Although the chunk function accepts overlap=150, its start-index expression advances to the prior end, so it does not actually retain overlapping text. The corpus PDFs were not supplied and this index was not regenerated.

## Evaluation design

Thirty prompts are divided equally into NORMAL, AMBIGUOUS, and ADVERSARIAL categories. The loop makes six calls per prompt, producing 180 logged runs:

| Mode | Calls per prompt | Parameters used by the called function |
| --- | ---: | --- |
| 0 | 2 | k=3 and k=8 |
| 1 | 2 | Same function call twice; recorded temperature labels are not passed |
| 2 | 2 | Recorded labels 0.0 and 0.7 are not passed; generation uses fixed temperature 0.2 with sampling |

The original slide gives k=2 and k=5, whereas the supplied evaluation code uses k=3 and k=8 for Mode 0. Mode 1 separately uses internal retrieval counts for Orange Book and ASHP passages.

The supplied auto_score function sets correctness to 0.5 by default, sets hallucination to 1 for Mode 2 based on its mode label, and changes some fields for adversarial errors. It does not compare responses with ground-truth answers. Its displayed means therefore describe those assigned rules, not independently measured answer accuracy or hallucination. Do not substitute them for the separate rates reported in the presentation.

## Evidence gates and product research

The source's AB gate checks whether an ingredient name and an AB token appear in the same retrieved passage. It does not join structured FDA product-level equivalence codes. Finding the same ingredient or an AB token is not enough to verify a specific product pair. For the underlying distinction, see the [FDA Orange Book Preface](https://www.fda.gov/drugs/development-approval-process-drugs/orange-book-preface).

The optional strength handling ranks by closeness rather than enforcing an exact clinically equivalent match. Stock totals use status exclusions for expired, recalled, and quarantined records, but do not revalidate dates or units at answer time. Synthetic quantity units can vary within a drug's lots. Treat these as prototype logic rather than medication substitution or dispensing instructions.

## Implementation details for a future revision

- Some attribute branches look for refrigerated/controlled column names that differ from the generator's refrigerated_flag and controlled_flag.
- Cost formatting looks for contract_price/uom, while the supplied generator uses unit_cost and no uom field.
- Cost questions without an explicit drug ID can return the first contract rows rather than matching a named ingredient.
- Authentication, role-based access, ERP/WMS integration, and patient-data processing are not implemented by the supplied notebook.
- Retrieval relevance, refusals, and evidence support require answer-level review rather than assuming direct retrieval prevents every error.

## Portfolio edits and provenance

The portfolio notebook's Markdown is revised for clear scope and naming. All code cells are retained. One saved output cell containing erroneous generated medication suggestions is replaced with an explanatory note; the original output remains in archive/hospital_chatbot_original.ipynb as a failure-analysis artifact. Other saved outputs remain unchanged.

The source dataset notebook and separate reference demo are copied without modification under descriptive filenames. The standalone generator adds CLI options, a configurable output path, and a fixed simulation date. Original sources have not been assigned a new blanket license.
