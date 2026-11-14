# Run the prototype

## 1. Work from the repository root

Clone the existing healthcare-chatbot repository and open Jupyter from its root. If your notebook runtime uses another working directory, set CHATBOT_PROJECT_DIR to the checkout root before running the first setup cell. In Colab, use a checkout in the runtime and set that same variable; mounting Drive is optional if you store the corpus there.

## 2. Generate synthetic records

```bash
python scripts/generate_synthetic_data.py --output data/generated
```

The default configuration creates 8,000 catalog entries, 80 locations, 200,000 lots, and 8,000 contracts. A small example uses:

```bash
python scripts/generate_synthetic_data.py --drugs 40 --locations 8 --lots 200 --output data/generated
```

The standalone generator has configurable counts, seed, output path, and simulation date. It does not connect to a hospital system. Generated data can contain unrealistic combinations and must not be treated as medication instructions.

## 3. Supply the original reference PDFs

Place authorized copies of orange_book.pdf and ashp_guidelines.pdf in corpus/. The original saved excerpts identify the Orange Book's 2025 edition; the exact ASHP title/edition must be confirmed to reproduce that source. These PDFs were not supplied in the attachments and are not redistributed here.

## 4. Run notebook cells in order

Install requirements.txt in your intended runtime. The first setup cell checks file availability and loads data/generated/ when present, otherwise data/. The corpus cell now defines its own PDF formatter, catalog resolver, and overlapping chunker before the answer tests.

The catalog resolver uses supplied names; no RxNorm service is called. Unknown brand names need an appropriate source mapping or a query using an existing catalog name/identifier. Mode 1 formats retrieved data with deterministic templates. Mode 2 requires network access to the Qwen2.5-1.5B-Instruct weights and adequate runtime memory. The separate references/ demonstration has additional dependencies.

## Verification status

Notebook syntax, corrected helper behavior, explicit-ID operational/cost queries, name matching, PDF formatting, and chunk overlap were checked using synthetic fixtures. The portable generator's small configuration was also checked in the earlier package. The full PDF index, model inference, and benchmark were not rerun. Current notebook outputs are cleared. The recorded source outputs remain in archive/hospital_chatbot_portfolio_v1.ipynb.

See docs/revision_notes.md for changes and docs/technical_notes.md for the original implementation and project-reported results.
