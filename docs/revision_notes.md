# Notebook dependency revision

The current notebook provides deterministic PDF formatting and catalog-name resolution before the Mode 0 tests. It no longer relies on those functions being left over in a Colab session. It also uses configurable local paths, actual character overlap in chunking, and unit_cost in cost formatting to match the supplied generator.

The resolver matches names present in the synthetic drug catalog. It does not call RxNorm or invent unknown brand-to-ingredient mappings. An unknown brand may therefore return no matches until its mapping is supplied through an appropriate data source.

The previous portfolio notebook with successful historical outputs is preserved in archive/hospital_chatbot_portfolio_v1.ipynb. The original uploaded notebook remains at archive/hospital_chatbot_original.ipynb. Current execution outputs are cleared: corpus indexing, Qwen inference, and the evaluation were not rerun. The historical 6,383-passage count may change under the corrected chunker.

The setup guide now describes the corrected checkout-based workflow. Older implementation observations in docs/technical_notes.md refer to the historical source. Current code still uses retrieval-assisted templates, a separate guarded language-model path, and the same original heuristic scoring design. No new benchmark or clinical validation is claimed.
