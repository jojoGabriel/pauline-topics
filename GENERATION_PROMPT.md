# Pauline Topics — Module Generation Prompt

You are generating a structured Bible study module based ONLY on the letters of Paul the Apostle.

Use `topics.md` as the canonical master list for global topic numbering, naming, and completion state.
Use `Volume1_Topics_FINAL.md` to determine the generation order for Volume 1.
If a volume planning file and `topics.md` differ, preserve the canonical IDs and names from `topics.md` and use the volume file only for sequencing.

---

## 🔒 CORE RULES (MANDATORY)

### 1. Primary Corpus Rule

Use ONLY the letters of Paul the Apostle:

- Romans  
- 1–2 Corinthians  
- Galatians  
- Ephesians  
- Philippians  
- Colossians  
- 1–2 Thessalonians  
- 1–2 Timothy  
- Titus  
- Philemon  

Do NOT include non-Pauline passages in the main content.

---

### 2. Optional Cross-References

You MAY include a final section:

## 13. Broader Scripture Connections (Optional)

Rules:

- references only (no quotations)
- no explanation

---

### 3. Translation Rule

All quotations must match the Berean Standard Bible (BSB).

- Do NOT paraphrase Scripture
- Do NOT modify wording
- Do NOT harmonize wording

---

### 4. Vocabulary System

Use consistent terminology:

- justified → declared righteous before God  
- righteousness → right standing before God  
- grace → God’s undeserved favor  
- faith → trust in God and in Jesus Christ  
- Law → commandments given through Moses  
- sin → disobedience against God  

Rules:

- Define terms on first occurrence only
- Do NOT rotate synonyms unnecessarily

---

### 5. Quote Metadata (REQUIRED)

Every quotation MUST have a metadata block immediately above it:

<!--
id: PTXX-QX
reference: Book Chapter:Verse(s)
source: BSB
source_url: https://biblehub.com/bsb/{book}/{chapter}.htm
type: exact | partial | excerpt
ellipsis_allowed: true | false
-->

Rules:

- ID must be unique (e.g., PT03-Q1)
- Use correct Bible Hub URL
- Mark type accurately:
  - exact → full verse(s)
  - partial → portion of verse
  - excerpt → condensed or shortened

---

### 6. Quote Formatting

Use blockquote format:

> “Text”
> *(Reference)*

Include a visible link:

[View on Bible Hub](URL)

---

### 7. Passage Integrity Rule

- If using a full passage (e.g., Romans 3:21–24):
  - ensure accuracy of content
- If shortened:
  - must be marked as `excerpt`
  - ellipsis must be intentional

---

### 8. Structure (DO NOT CHANGE)

Each module MUST follow this exact structure:

# Topic Title

**Paul’s Teachings by Topic**  
**Volume 1: Salvation and Foundations**  
**A Structured Topical Study from the Letters of Paul the Apostle Using Selected Passages**  
**Text Basis:** Berean Standard Bible (BSB)

---

## 1. Definition

## 2. The Problem / Context

## 3. God’s Action / Provision

## 4. Means / Response

## 5. Illustration / Example

## 6. Result / Outcome

## 7. Summary

## 8. Key Verse

## 9. Observation Questions (2–3)

## 10. Reflection Questions (2–3)

## 11. Application Questions (1–2)

## 12. Broader Scripture Connections (Optional)

---

### 9. Question Rules

- Designed for 30–45 minute study
- Must be text-based
- Must be clear and direct
- Avoid speculation
- Keep observation questions explicitly tied to cited passages
- Avoid duplicate questions across observation, reflection, and application sections

---

### 10. Definition Integrity Rule

In `## 1. Definition`:

- explain the topic without using the topic term itself as its own gloss
- make the definition understandable even if the title were hidden
- mention adjacent topics only as supporting vocabulary, not as the main explanatory dependency
- avoid circular wording such as `Faith refers to faith` or `Grace means grace`

---

### 11. Summary Alignment Rule

In `## 7. Summary`:

- restate the module’s own center of gravity before naming causes, results, or adjacent topics
- keep the summary aligned with the definition and key verse rather than shifting into a neighboring topic
- you may mention major results or linked themes, but they should support the topic summary rather than replace it

---

### 12. Style Rules

- No theological speculation beyond the text
- No cross-author harmonization
- No doctrinal argumentation
- Keep wording simple and precise
- Avoid repetition

---

### 13. Linking Rules

Include links ONLY:

- in metadata
- in quote blocks
- in question sections as review-only verse links

Do NOT include links in:

- explanatory prose outside those sections

Question-section links rule:

- you may add markdown links in observation, reflection, and application questions to help review the cited passages in the markdown source
- these links are for on-screen review and should not be relied on for print output
- prefer linking verse references or short reference labels, not full sentences

---

### 14. Output Format

- Output must be valid Markdown (.md)
- Clean and readable
- No commentary outside the module

---

### 15. Post-Generation Workflow (REQUIRED)

After generating or revising a topic module:

- confirm the topic ID and title against `topics.md` before creating files
- use `Volume1_Topics_FINAL.md` to determine which topic comes next when working through Volume 1
- validate the `## 1. Definition` section with `python3 scripts/check_definitions.py` before considering the module complete
- validate `## 7. Summary` alignment with `python3 scripts/check_summaries.py` before considering the module complete
- validate question structure and clarity with `python3 scripts/check_questions.py` before considering the module complete
- review cross-module overlap with `python3 scripts/check_topic_overlap.py` before considering the module complete
- verify module IDs, titles, and filenames against `topics.md` with `python3 scripts/check_registry_alignment.py`
- verify current module coverage against `Volume1_Topics_FINAL.md` with `python3 scripts/check_volume_coverage.py`
- validate `## 12. Broader Scripture Connections (Optional)` with `python3 scripts/check_broader_connections.py` when that section is present
- review repeated questions across modules with `python3 scripts/check_question_similarity_volume.py`
- validate all quote metadata and quoted text against the BSB source before considering the module complete
- when possible, prefer the one-command check `python3 scripts/validate_module_set.py modules --bsb-json bsb_usj`
- fix any validation failures before final delivery
- do not generate a PDF unless the user explicitly requests it
- treat delivery as complete after validation unless the user also requests PDF output

---

### 16. Header Lines (Required)

At the top, under the title, include these lines exactly:

**Paul’s Teachings by Topic**  
**Volume 1: Salvation and Foundations**  
**A Structured Topical Study from the Letters of Paul the Apostle Using Selected Passages**  
**Text Basis:** Berean Standard Bible (BSB)

---

## 🎯 TASK

Generate a complete module for:

TOPIC: {INSERT TOPIC NAME}  
MODULE ID: PT-XX

Follow ALL rules exactly.
