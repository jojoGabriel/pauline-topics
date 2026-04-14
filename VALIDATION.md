# Validation Overview

The validation checks exist to make module quality less dependent on memory or careful rereading by hand.

They serve four purposes:

- protect textual accuracy, especially for Scripture quotations and metadata
- keep each module internally coherent, so the definition, summary, key verse, and questions point in the same direction
- keep adjacent modules distinct, so topics do not collapse into one another across the volume
- keep the module set aligned with the canonical registry and the current volume plan

## Preferred Command

Run the full validation stack with:

```bash
python3 scripts/validate_module_set.py modules --bsb-json bsb_usj
```

## What Each Check Covers

- `validate_quotes.py`
  Confirms quote text and quote metadata match the BSB source.

- `check_definitions.py`
  Catches circular/self-referential definitions and definition dependence on neighboring topic titles.

- `check_summaries.py`
  Checks that summaries stay aligned with the module’s own definition instead of drifting into adjacent topics.

- `check_questions.py`
  Checks question counts, numbering, text-based grounding, speculative wording, and duplicate questions within a module.

- `check_topic_overlap.py`
  Flags suspicious cross-module overlap such as duplicate key verses and unusually similar definitions or summaries.

- `check_registry_alignment.py`
  Verifies module IDs, titles, and filenames against `topics.md`.

- `check_volume_coverage.py`
  Verifies current module coverage against `Volume1_Topics_FINAL.md`.

- `check_broader_connections.py`
  Ensures the optional broader-connections section stays reference-only.

- `check_question_similarity_volume.py`
  Flags repeated questions across modules.

## Interpretation

Most checks are heuristic guardrails, not final theological judgment.

Use them to identify likely problems quickly:

- quote problems should usually be treated as hard errors
- definition, summary, question, and overlap findings should usually trigger review and revision
- registry and volume findings show where the module set no longer matches the project plan
