# Evaluation materials

- prompts.json exports the original 30-prompt suite: ten normal, ten ambiguous, and ten adversarial queries.
- design.json records the suite size, 180 saved calls, retrieval settings, model-temperature behavior, and provenance.
- The original notebook includes the evaluation loop and its saved summary.

The complete generated runs.csv was not attached. The source notebook displays only a preview of its rows and a grouped scoring summary. Project-reported performance figures appear in the presentation; see docs/technical_notes.md for the distinction between those figures and the supplied rule-based scoring function.

For future extensions, preserve complete responses, timestamps, source IDs, model settings, ground-truth labels, and reviewer judgments so a result can be recomputed from its underlying records.
