# Hospital Supply-Chain Chatbot

**Python · TF-IDF · pandas · Hugging Face Transformers · LLM Evaluation**

Hospital pharmacy and supply-chain teams need to locate stock, trace expiring lots, compare contracts, and research alternatives during shortages. This prototype brings those questions into one conversational workflow using synthetic hospital records and reference documents.

[Notebook](notebooks/hospital_supply_chain_chatbot.ipynb) · [Presentation](reports/hospital_supply_chain_chatbot_presentation.pptx) · [Evaluation prompts](evaluation/prompts.json) · [Setup](docs/setup.md)

## Recorded project scale

**200K synthetic inventory lots · 8K catalog entries · 80 locations · 6,383 indexed passages · 180 evaluation calls**

Operational data covers three simulated hospitals and 8,000 cost-contract records.

## Project results

Results presented in the [original project presentation](reports/hospital_supply_chain_chatbot_presentation.pptx):

| Measure | Project result |
| --- | --- |
| Query resolution | **Under 10 seconds**, compared with a 15–45-minute manual workflow |
| Retrieval-assisted mode | **Under 2% hallucination** |
| LLM-only mode | **10–15% hallucination on unblocked queries** |
| Ambiguous queries | Approximately **40–50% abstention** |

[Evaluation context](docs/technical_notes.md) explains the source and scope of these figures.

## Core functions

- **Inventory and lot lookup:** find stock by drug, facility, location, or lot and inspect status and expiration.
- **Alternative-drug recommender:** surface same-ingredient catalog options, apply optional dosage-form/route criteria and strength-aware ranking, and prioritize candidates by stock while displaying reference evidence.
- **Cost and contract lookup:** retrieve simulated vendor pricing and contract information.
- **Source-grounded answers:** attach table-field or document/page/chunk references to retrieved information.

## How it works

| Mode | Answer path |
| --- | --- |
| Direct retrieval | Returns operational rows or PDF passages with document/page/chunk references |
| Retrieval-assisted | Formats retrieved inventory and contract data into structured answers with citations |
| LLM-only | Uses Qwen2.5-1.5B-Instruct, with an operational-query guard before generation |

The test suite includes **10 normal, 10 ambiguous, and 10 adversarial prompts**. It exercises inventory lookup, lot tracing, unclear requests, and attempts to override system instructions.

## Explore or run

```bash
python scripts/generate_synthetic_data.py --output data/generated
```

[Notebooks](notebooks/) · [Data generator](scripts/) · [Evaluation](evaluation/) · [Reference demonstration](references/) · [Technical notes](docs/technical_notes.md)

[Setup](docs/setup.md) covers the synthetic tables, reference PDFs, and model requirements. [Revision notes](docs/revision_notes.md) document the code improvements and preserved original outputs.

Educational prototype using synthetic operational data; not a clinical service or live hospital integration.

Boston University Questrom MSBA group project. Original collaborators: Hamza Tariq and Ahrar Karim.
