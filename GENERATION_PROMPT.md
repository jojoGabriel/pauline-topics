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

---

### 10. Style Rules

- No theological speculation beyond the text
- No cross-author harmonization
- No doctrinal argumentation
- Keep wording simple and precise
- Avoid repetition

---

### 11. Linking Rules

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

### 12. Output Format

- Output must be valid Markdown (.md)
- Clean and readable
- No commentary outside the module

---

### 13. Post-Generation Workflow (REQUIRED)

After generating or revising a topic module:

- confirm the topic ID and title against `topics.md` before creating files
- use `Volume1_Topics_FINAL.md` to determine which topic comes next when working through Volume 1
- validate all quote metadata and quoted text against the BSB source before considering the module complete
- fix any validation failures before final delivery
- do not generate a PDF unless the user explicitly requests it
- treat delivery as complete after validation unless the user also requests PDF output

---

### 14. Header Lines (Required)

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
