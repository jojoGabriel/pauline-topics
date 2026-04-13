# Pauline Topics — Module Generation Prompt

You are generating a structured Bible study module based ONLY on the letters of Paul the Apostle.

---

## 🔒 CORE RULES (MANDATORY)

### 1. Primary Corpus Rule

- Use ONLY the letters of Paul the Apostle:
  - Romans, 1–2 Corinthians, Galatians, Ephesians, Philippians, Colossians,
    1–2 Thessalonians, 1–2 Timothy, Titus, Philemon
- Do NOT include non-Pauline passages in main content

---

### 2. Optional Cross-References

- You MAY include a final section:

  ## 13. Broader Scripture Connections (Optional)

- This section:
  - contains ONLY references (no quotes)
  - contains NO explanation

---

### 3. Translation Rule

- All quotations must match the Berean Standard Bible (BSB)
- Do NOT paraphrase Scripture
- Do NOT modify wording

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

- Clarify term only on first occurrence per module
- Do NOT use synonyms interchangeably

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
- Use correct Bible Hub URL format
- Mark type accurately:
  - exact → full verse(s)
  - partial → portion of verse
  - excerpt → condensed with ellipsis

---

### 6. Quote Formatting

- Use blockquote format:
  > “Text”
  > *(Reference)*

- Include a visible link:
  [View on Bible Hub](URL)

---

### 7. Passage Integrity Rule

- If referencing a full passage (e.g., Romans 3:21–24):
  - ensure content matches that passage
- If shortened → must be marked as `excerpt`

---

### 8. Structure (DO NOT CHANGE)

Each module MUST follow this exact structure:

# [PT-XX] Topic Title

Teachings from the Letters of Paul the Apostle  
Text Basis: Berean Standard Bible (BSB)

## 1. Definition

## 2. The Problem / Context

## 3. God’s Action / Provision

## 4. Means / Response

## 5. Illustration / Example

## 6. Result / Outcome

## 7. Summary

## 8. Key Verse

## 9. References

## 10. Observation Questions (2–3)

## 11. Reflection Questions (2–3)

## 12. Application Questions (1–2)

## 13. Broader Scripture Connections (Optional)

---

### 9. Question Rules

- Keep total study time: 30–45 minutes
- Questions must be:
  - text-based
  - clear
  - non-speculative

---

### 10. Style Rules

- No interpretation beyond the text
- No theological arguments
- No cross-author harmonization
- Keep wording simple and precise
- Avoid repetition and filler

---

### 11. Linking Rules

- Include links ONLY:
  - in metadata
  - in quote blocks
- Do NOT link:
  - questions
  - reference section

---

### 12. Output Format

- Output must be valid Markdown (.md)
- Clean and readable
- No extra commentary outside the module

---

## 🎯 TASK

Generate a complete module for:

TOPIC: {INSERT TOPIC NAME}
MODULE ID: PT-XX

Follow ALL rules exactly.
