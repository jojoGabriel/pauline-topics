#!/usr/bin/env python3
"""Validate quoted verses in module markdown using the provided Bible Hub links."""

import argparse
import html
import json
import os
import re
import urllib.error
import urllib.request
from html.parser import HTMLParser


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._ignore_depth = 0
        self._parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self._ignore_depth += 1
        if tag in {"p", "div", "br", "li", "td", "tr", "blockquote", "section", "article"}:
            self._parts.append(" ")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self._ignore_depth:
            self._ignore_depth -= 1
        if tag in {"p", "div", "li", "td", "tr", "blockquote", "section", "article"}:
            self._parts.append(" ")

    def handle_data(self, data):
        if self._ignore_depth:
            return
        self._parts.append(data)

    def get_text(self):
        return "".join(self._parts)


def normalize_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")
    text = text.replace("—", "-").replace("–", "-")
    text = text.replace("…", "...")
    text = re.sub(r"([,;:?!])(?=\S)", r"\1 ", text)
    text = re.sub(r"\s+", " ", text.strip())
    text = re.sub(r"\s+([.,:;?!])", r"\1", text)
    return text


def normalize_search_text(text: str) -> str:
    text = normalize_text(text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text.strip())
    return text.lower()


def extract_metadata(lines, start_index):
    metadata = {}
    idx = start_index
    while idx < len(lines):
        line = lines[idx]
        if "-->" in line:
            break
        stripped = line.strip().lstrip("<!--").rstrip("-->").strip()
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            metadata[key.strip().lower()] = value.strip()
        idx += 1
    return metadata, idx


def extract_quote_block(lines, start_index):
    quote_lines = []
    idx = start_index
    # Skip blank lines between metadata and the quoted block.
    while idx < len(lines) and not lines[idx].lstrip().startswith(">"):
        if lines[idx].strip():
            break
        idx += 1

    while idx < len(lines):
        line = lines[idx]
        if line.lstrip().startswith(">"):
            quote_lines.append(line.lstrip()[1:].lstrip())
            idx += 1
            continue
        break
    cleaned = []
    for line in quote_lines:
        stripped = line.strip()
        if stripped.startswith("[") and "View on Bible Hub" in stripped:
            continue
        if stripped.startswith("*") and stripped.endswith("*"):
            continue
        if not stripped:
            continue
        cleaned.append(stripped)
    return " ".join(cleaned).strip(), idx


def parse_module_file(file_path):
    with open(file_path, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    entries = []
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        if line.lstrip().startswith("<!--"):
            metadata, end_idx = extract_metadata(lines, idx + 1)
            if end_idx >= len(lines) or "-->" not in lines[end_idx]:
                idx += 1
                continue
            end_idx += 1
            quote_text, next_index = extract_quote_block(lines, end_idx)
            if quote_text and "source_url" in metadata:
                entries.append(
                    {
                        "source_file": file_path,
                        "source_line": idx + 1,
                        "metadata": metadata,
                        "quote_text": quote_text,
                    }
                )
            idx = next_index
            continue
        idx += 1
    return entries


def fetch_page_text(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; pauline-topics-validator/1.0; +https://github.com)"
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        raw_html = response.read().decode("utf-8", errors="ignore")
    parser = TextExtractor()
    parser.feed(raw_html)
    parser.close()
    return normalize_text(parser.get_text()), raw_html


def load_bsb_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


BOOK_CODE_MAP = {
    "romans": "ROM",
    "galatians": "GAL",
    "ephesians": "EPH",
    "philippians": "PHP",
    "colossians": "COL",
    "titus": "TIT",
    "philemon": "PHM",
    "1 corinthians": "1CO",
    "2 corinthians": "2CO",
    "1 thessalonians": "1TH",
    "2 thessalonians": "2TH",
    "1 timothy": "1TI",
    "2 timothy": "2TI",
}


def normalize_book_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.replace("-", " ").replace("_", " ").strip().lower())


def find_book_section(data, book_name):
    if not isinstance(book_name, str) or not isinstance(data, dict):
        return None
    normalized_target = normalize_book_name(book_name)
    for key, value in data.items():
        if normalize_book_name(str(key)) == normalized_target:
            return value
    for fallback_key in ("books", "bible", "Bible", "Books"):
        if fallback_key in data and isinstance(data[fallback_key], dict):
            value = find_book_section(data[fallback_key], book_name)
            if value is not None:
                return value
    return None


def get_chapter_section(book_section, chapter):
    if isinstance(book_section, dict):
        if chapter in book_section:
            return book_section[chapter]
        chapter_str = str(chapter)
        for key, value in book_section.items():
            if str(key) == chapter_str:
                return value
    return None


def make_verse_map_from_json(bsb_json, book, chapter):
    book_section = find_book_section(bsb_json, book)
    if book_section is None:
        return {}
    chapter_section = get_chapter_section(book_section, chapter)
    if chapter_section is None:
        return {}
    verse_map = {}
    if isinstance(chapter_section, dict):
        for verse_key, verse_text in chapter_section.items():
            try:
                verse_num = int(str(verse_key).strip())
            except ValueError:
                continue
            verse_map[verse_num] = normalize_text(str(verse_text))
    elif isinstance(chapter_section, list):
        for index, verse_text in enumerate(chapter_section):
            if index == 0:
                continue
            verse_map[index] = normalize_text(str(verse_text))
    return verse_map


def parse_reference(reference: str):
    if not reference:
        return None
    match = re.match(
        r"^([1-3]?\s?[A-Za-z]+(?:\s+[A-Za-z]+)*)\s+(\d+):(\d+)(?:-(\d+))?\s*$",
        reference,
    )
    if not match:
        return None
    book = match.group(1).strip()
    chapter = int(match.group(2))
    start = int(match.group(3))
    end = int(match.group(4)) if match.group(4) else start
    return book, chapter, start, end


def get_usj_code(book_name: str):
    normalized = normalize_book_name(book_name)
    return BOOK_CODE_MAP.get(normalized)


def parse_source_url(url: str):
    match = re.search(r"/bsb/([^/]+)/([0-9]+)\.htm", url)
    if not match:
        return None, None
    book = match.group(1).replace("_", " ").replace("-", " ")
    chapter = int(match.group(2))
    return book, chapter


def load_usj_file(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def make_verse_map_from_usj(usj_data, chapter):
    if not isinstance(usj_data, dict) or usj_data.get("type") != "USJ":
        return {}

    verse_map = {}
    current_chapter = None
    current_verse = None
    current_text = []

    def flatten_content(value):
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return "".join(flatten_content(item) for item in value)
        if isinstance(value, dict):
            item_type = value.get("type")
            if item_type in {"verse", "note", "char", "ref"}:
                return ""
            return flatten_content(value.get("content", ""))
        return ""

    def finish_verse():
        nonlocal current_verse, current_text
        if current_verse is not None:
            verse_map[current_verse] = normalize_text("".join(current_text))
            current_text = []

    for item in usj_data.get("content", []):
        item_type = item.get("type")
        if item_type == "chapter":
            if current_chapter == chapter and current_verse is not None:
                finish_verse()
            current_chapter = int(item.get("number")) if item.get("number") else None
            current_verse = None
            current_text = []
            continue

        if current_chapter != chapter:
            continue

        content = item.get("content")
        if isinstance(content, list):
            for token in content:
                if isinstance(token, dict) and token.get("type") == "verse" and token.get("marker") == "v":
                    if current_verse is not None:
                        finish_verse()
                    current_verse = int(token.get("number")) if token.get("number") else None
                    current_text = []
                    continue
                current_text.append(flatten_content(token))
        elif current_verse is not None and content is not None:
            current_text.append(flatten_content(content))

    if current_chapter == chapter and current_verse is not None:
        finish_verse()

    return verse_map


def strip_html_tags(html_text: str) -> str:
    return re.sub(r"<[^>]+>", "", html_text)


def fetch_verse_map(raw_html: str) -> dict:
    verse_map = {}
    pattern = re.compile(
        r'<span class="reftext">.*?<b>(\d+)</b>.*?</span>(.*?)(?=<A name="|$)',
        re.S,
    )
    for match in pattern.finditer(raw_html):
        verse_num = int(match.group(1))
        verse_text = strip_html_tags(match.group(2))
        verse_map[verse_num] = normalize_text(verse_text)
    return verse_map


def get_range_text(page_text: str, verse_map: dict, range_start: int, range_end: int):
    if not verse_map or range_start not in verse_map:
        return page_text
    collected = []
    for verse in range(range_start, range_end + 1):
        text = verse_map.get(verse)
        if text is None:
            return page_text
        collected.append(text)
    return " ".join(collected)


def select_validation_text(page_data, range_ref):
    if page_data.get("source") in {"json", "usj"}:
        verse_map = page_data.get("verse_map", {})
        if range_ref:
            return get_range_text("", verse_map, range_ref[2], range_ref[3])
        return " ".join(verse_map[v] for v in sorted(verse_map))

    if range_ref:
        return get_range_text(page_data["page_text"], page_data.get("verse_map"), range_ref[2], range_ref[3])
    return page_data["page_text"]


STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "for",
    "to",
    "of",
    "in",
    "on",
    "by",
    "with",
    "as",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "from",
    "that",
    "this",
    "these",
    "those",
    "it",
    "its",
    "his",
    "her",
    "their",
    "who",
    "whom",
    "which",
    "what",
    "when",
    "where",
    "how",
    "all",
    "not",
    "no",
    "so",
    "such",
}

def find_phrase_position(base_text: str, phrase: str) -> int:
    normalized_base = normalize_search_text(base_text)
    normalized_phrase = normalize_search_text(phrase)
    if not normalized_phrase:
        return -1
    exact_pos = normalized_base.find(normalized_phrase)
    if exact_pos != -1:
        return exact_pos

    phrase_words = [word for word in normalized_phrase.split() if word not in STOPWORDS]
    if len(phrase_words) < 4:
        return exact_pos

    base_words = normalized_base.split()
    base_index = 0
    start_pos = -1
    for phrase_word in phrase_words:
        while base_index < len(base_words) and base_words[base_index] != phrase_word:
            base_index += 1
        if base_index == len(base_words):
            return -1
        if start_pos == -1:
            start_pos = base_index
        base_index += 1
    if start_pos == -1:
        return -1
    # Reconstruct approximate character position from word index
    char_positions = []
    offset = 0
    for word in normalized_base.split():
        char_positions.append(offset)
        offset += len(word) + 1
    return char_positions[start_pos] if start_pos < len(char_positions) else -1


def search_segments(base_text: str, quote_segments):
    last_index = 0
    normalized_base = normalize_search_text(base_text)
    for segment in quote_segments:
        if not segment:
            continue
        segment_pos = find_phrase_position(normalized_base, segment)
        if segment_pos == -1:
            return False
        if segment_pos < last_index:
            return False
        segment_norm = normalize_search_text(segment)
        last_index = segment_pos + len(segment_norm)
    return True


def validate_entry(entry, page_data):
    metadata = entry["metadata"]
    quote_text = entry["quote_text"]
    normalized_quote = normalize_text(quote_text).strip(' "\'“”‘’')
    quote_type = metadata.get("type", "exact").lower()

    range_ref = parse_reference(metadata.get("reference", ""))
    verse_text = select_validation_text(page_data, range_ref)
    page_text_lower = verse_text.lower()
    normalized_quote_lower = normalized_quote.lower()

    if quote_type in {"excerpt", "partial"}:
        segments = [segment.strip(' "\'“”‘’') for segment in normalized_quote_lower.split("...") if segment.strip()]
        return search_segments(page_text_lower, segments)

    if normalized_quote_lower in page_text_lower:
        return True

    if normalize_search_text(normalized_quote_lower) in normalize_search_text(page_text_lower):
        return True

    fallback_segments = [segment.strip(' "\'“”‘’') for segment in re.split(r"[\.,;:\?!]", normalized_quote_lower) if segment.strip()]
    return search_segments(page_text_lower, fallback_segments)


def find_markdown_files(root_path):
    for base, _, files in os.walk(root_path):
        for filename in files:
            if filename.lower().endswith(".md"):
                yield os.path.join(base, filename)


def main():
    parser = argparse.ArgumentParser(description="Validate quoted verses in Pauline Topics markdown modules.")
    parser.add_argument(
        "path",
        nargs="?",
        default="modules",
        help="Path to a markdown file or directory containing module markdown files.",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed validation output.")
    parser.add_argument(
        "--bsb-json",
        help="Path to a local BSB JSON file or BSB USJ directory for validation.",
    )
    args = parser.parse_args()

    paths = [args.path] if os.path.isfile(args.path) else list(find_markdown_files(args.path))
    if not paths:
        print(f"No markdown files found at: {args.path}")
        return 1

    entries = []
    for path in paths:
        entries.extend(parse_module_file(path))

    if not entries:
        print("No quote metadata entries found.")
        return 1

    bsb_source = None
    if args.bsb_json:
        if os.path.isdir(args.bsb_json):
            bsb_source = {"type": "dir", "path": args.bsb_json}
        else:
            try:
                bsb_source = {"type": "file", "data": load_bsb_json(args.bsb_json)}
            except Exception as exc:
                print(f"Failed to load BSB JSON from {args.bsb_json}: {exc}")
                return 1
    elif os.path.isdir("bsb_usj"):
        bsb_source = {"type": "dir", "path": os.path.abspath("bsb_usj")}

    page_cache = {}
    failures = []
    for entry in entries:
        source_url = entry["metadata"].get("source_url")
        if not source_url:
            failures.append((entry, "Missing source_url metadata."))
            continue

        if source_url not in page_cache:
            try:
                if bsb_source is not None:
                    if bsb_source["type"] == "dir":
                        book, chapter = parse_source_url(source_url)
                        if not book:
                            ref_book = parse_reference(entry["metadata"].get("reference", ""))
                            book = ref_book[0] if ref_book else None
                            chapter = ref_book[1] if ref_book else None
                        code = get_usj_code(book) if book else None
                        if not code:
                            raise ValueError(f"Cannot map book name '{book}' to USJ file code")
                        usj_path = os.path.join(bsb_source["path"], f"{code}.usj")
                        if not os.path.exists(usj_path):
                            raise FileNotFoundError(f"USJ file not found: {usj_path}")
                        usj_data = load_usj_file(usj_path)
                        verse_map = make_verse_map_from_usj(usj_data, chapter)
                        page_cache[source_url] = {
                            "source": "usj",
                            "verse_map": verse_map,
                        }
                    else:
                        book, chapter = parse_source_url(source_url)
                        verse_map = make_verse_map_from_json(bsb_source["data"], book, chapter)
                        page_cache[source_url] = {
                            "source": "json",
                            "verse_map": verse_map,
                        }
                else:
                    page_text, raw_html = fetch_page_text(source_url)
                    page_cache[source_url] = {
                        "source": "web",
                        "page_text": page_text,
                        "verse_map": fetch_verse_map(raw_html),
                    }
            except urllib.error.HTTPError as exc:
                failures.append((entry, f"HTTP error fetching {source_url}: {exc.code}"))
                continue
            except urllib.error.URLError as exc:
                failures.append((entry, f"URL error fetching {source_url}: {exc.reason}"))
                continue
            except Exception as exc:
                failures.append((entry, f"Failed to prepare source data for {source_url}: {exc}"))
                continue

        page_data = page_cache[source_url]
        valid = validate_entry(entry, page_data)
        if not valid:
            failures.append((entry, "Quoted text not found on source page."))
        elif args.verbose:
            print(
                f"OK: {entry['source_file']}:{entry['source_line']} id={entry['metadata'].get('id')} reference={entry['metadata'].get('reference')}"
            )

    if failures:
        print("\nValidation failures:\n")
        for entry, reason in failures:
            meta = entry["metadata"]
            print(
                f"- {entry['source_file']}:{entry['source_line']} id={meta.get('id')} reference={meta.get('reference')} source_url={meta.get('source_url')}"
            )
            print(f"  Reason: {reason}")
            if args.verbose:
                print(f"  Quote: {entry['quote_text']}")
            print()
        return 2

    print(f"Validated {len(entries)} quote entries successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
