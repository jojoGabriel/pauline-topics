#!/usr/bin/env python3
"""Render a module markdown file to PDF."""

from __future__ import annotations

import argparse
import html
import os
import re
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    parts = text.split("\n---\n", 1)
    if len(parts) == 2:
        return parts[1]
    return text


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def escape_markdown_to_html(text: str) -> str:
    text = html.escape(text.strip())
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = text.replace("\n", "<br/>")
    return text.replace("  ", "<br/>")


def build_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ModuleTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            textColor=HexColor("#1f2937"),
            spaceAfter=10,
        ),
        "subtitle": ParagraphStyle(
            "ModuleSubtitle",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            textColor=HexColor("#4b5563"),
            spaceAfter=6,
        ),
        "heading": ParagraphStyle(
            "ModuleHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=HexColor("#111827"),
            spaceBefore=8,
            spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "ModuleBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            textColor=HexColor("#111827"),
            spaceAfter=8,
        ),
        "quote": ParagraphStyle(
            "ModuleQuote",
            parent=styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=10.5,
            leading=15,
            textColor=HexColor("#1f2937"),
            leftIndent=18,
            rightIndent=12,
            borderPadding=0,
            spaceAfter=4,
        ),
        "cite": ParagraphStyle(
            "ModuleCitation",
            parent=styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=9.5,
            leading=12,
            textColor=HexColor("#6b7280"),
            leftIndent=24,
            spaceAfter=10,
        ),
        "list": ParagraphStyle(
            "ModuleList",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            leftIndent=14,
            bulletIndent=0,
            textColor=HexColor("#111827"),
            spaceAfter=5,
        ),
    }


def parse_markdown_blocks(text: str):
    lines = text.splitlines()
    blocks = []
    i = 0

    def collect_paragraph(start_index: int):
        parts = []
        idx = start_index

        while idx < len(lines):
            raw_line = lines[idx]
            current = raw_line.strip()
            if not current:
                break
            if current == "---" or current.startswith("#") or current.startswith(">"):
                break
            if re.match(r"^(\d+)\.\s+", current) or current.startswith("- "):
                break

            if parts:
                previous_raw = lines[idx - 1]
                parts.append("\n" if re.search(r"\s{2,}$", previous_raw) else " ")
            parts.append(current)
            idx += 1

        return "".join(parts), idx

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            blocks.append(("rule", ""))
            i += 1
            continue

        if stripped.startswith("# "):
            blocks.append(("title", stripped[2:].strip()))
            i += 1
            continue

        if stripped.startswith("## "):
            blocks.append(("heading", stripped[3:].strip()))
            i += 1
            continue

        if stripped.startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quote_lines.append(lines[i].lstrip()[1:].lstrip())
                i += 1

            quote_text = []
            cite_text = []
            for quote_line in quote_lines:
                if not quote_line.strip():
                    continue
                if quote_line.startswith("[View on Bible Hub]"):
                    continue
                if quote_line.startswith("*(") and quote_line.endswith(")*"):
                    cite_text.append(quote_line.strip("*"))
                else:
                    quote_text.append(quote_line)

            if quote_text:
                blocks.append(("quote", " ".join(part.strip() for part in quote_text)))
            if cite_text:
                blocks.append(("cite", " ".join(part.strip() for part in cite_text)))
            continue

        list_match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if list_match:
            while i < len(lines):
                current = lines[i].strip()
                current_match = re.match(r"^(\d+)\.\s+(.*)$", current)
                if not current_match:
                    break
                blocks.append(("olist", current_match.group(2).strip()))
                i += 1
            continue

        if stripped.startswith("- "):
            while i < len(lines):
                current = lines[i].strip()
                if not current.startswith("- "):
                    break
                blocks.append(("ulist", current[2:].strip()))
                i += 1
            continue

        paragraph_text, i = collect_paragraph(i)
        blocks.append(("paragraph", paragraph_text))

    return blocks


def render_pdf(input_path: Path, output_path: Path):
    raw_text = input_path.read_text(encoding="utf-8")
    clean_text = strip_html_comments(strip_frontmatter(raw_text))
    blocks = parse_markdown_blocks(clean_text)
    styles = build_styles()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=LETTER,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=input_path.stem,
        author="Pauline Topics",
    )

    story = []
    title_seen = False

    ordered_index = 0

    for block_type, content in blocks:
        if block_type == "rule":
            ordered_index = 0
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=0.6, color=HexColor("#d1d5db")))
            story.append(Spacer(1, 8))
            continue

        if block_type == "title":
            ordered_index = 0
            title_seen = True
            story.append(Paragraph(escape_markdown_to_html(content), styles["title"]))
            continue

        if not title_seen and block_type == "paragraph":
            ordered_index = 0
            for subtitle_line in content.split("\n"):
                if subtitle_line.strip():
                    story.append(Paragraph(escape_markdown_to_html(subtitle_line), styles["subtitle"]))
            continue

        if block_type == "heading":
            ordered_index = 0
            story.append(Paragraph(escape_markdown_to_html(content), styles["heading"]))
        elif block_type == "paragraph":
            ordered_index = 0
            story.append(Paragraph(escape_markdown_to_html(content), styles["body"]))
        elif block_type == "quote":
            ordered_index = 0
            story.append(Paragraph(escape_markdown_to_html(content), styles["quote"]))
        elif block_type == "cite":
            ordered_index = 0
            story.append(Paragraph(escape_markdown_to_html(content), styles["cite"]))
        elif block_type == "ulist":
            ordered_index = 0
            story.append(Paragraph(escape_markdown_to_html(content), styles["list"], bulletText="•"))
        elif block_type == "olist":
            ordered_index += 1
            story.append(Paragraph(escape_markdown_to_html(content), styles["list"], bulletText=f"{ordered_index}."))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story)


def main():
    parser = argparse.ArgumentParser(description="Render a module markdown file to PDF.")
    parser.add_argument("input_path", help="Path to the module markdown file.")
    parser.add_argument(
        "--output",
        "-o",
        help="Output PDF path. Defaults to the input path with a .pdf extension.",
    )
    args = parser.parse_args()

    input_path = Path(args.input_path).resolve()
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    output_path = Path(args.output).resolve() if args.output else input_path.with_suffix(".pdf")
    render_pdf(input_path, output_path)
    print(output_path)


if __name__ == "__main__":
    main()
