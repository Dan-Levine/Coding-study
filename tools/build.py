#!/usr/bin/env python3
"""Generate navigation and search indices for the Interview Prep Guide site."""
from __future__ import annotations

import json
import re
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
TEX_DIR = ROOT / "tex"
ASSETS_DIR = ROOT / "assets"
INDEX_PATH = TEX_DIR / "index.json"
SEARCH_PATH = ASSETS_DIR / "search.json"

SECTION_ORDER = (
    "Algorithms",
    "Data Structures",
    "Systems",
    "Behavioral",
)

KEYWORD_MAP = {
    "Algorithms": ("algorithm", "search", "sort", "graph", "dynamic"),
    "Data Structures": ("structure", "tree", "heap", "stack", "queue", "array", "list"),
    "Systems": ("system", "design", "network", "scal", "architecture", "distributed"),
    "Behavioral": ("behavior", "culture", "lead", "communication", "team", "collabor"),
}

SECTION_PATTERN = re.compile(r"\\section\*\{(?P<title>[^}]+)\}")


def discover_tex_files(directory: Path) -> List[Path]:
    """Return a sorted list of .tex files inside the directory."""
    return sorted(directory.glob("*.tex"))


def extract_title(content: str, fallback: str) -> str:
    match = SECTION_PATTERN.search(content)
    if match:
        return match.group("title").strip()
    return fallback.replace("-", " ").replace("_", " ").title()


def extract_summary(content: str) -> str:
    """Strip simple LaTeX commands to build a concise summary string."""
    without_comments = re.sub(r"%.*", "", content)
    without_env = re.sub(r"\\(begin|end)\{[^}]+\}", " ", without_comments)
    without_commands = re.sub(r"\\[a-zA-Z]+[*]?", " ", without_env)
    without_braces = without_commands.replace("{", " ").replace("}", " ")
    compact = re.sub(r"\s+", " ", without_braces).strip()
    return compact[:200]


def categorize(title: str, summary: str) -> str:
    haystack = f"{title} {summary}".lower()
    for section, keywords in KEYWORD_MAP.items():
        if any(keyword in haystack for keyword in keywords):
            return section
    return "Behavioral"


def slugify(path: Path) -> str:
    return path.stem


def build_sections(entries: Iterable[Tuple[str, Dict[str, str]]]) -> List[Dict[str, object]]:
    grouped: Dict[str, List[Dict[str, str]]] = OrderedDict((name, []) for name in SECTION_ORDER)
    for section, item in entries:
        grouped.setdefault(section, []).append(item)

    for section_items in grouped.values():
        section_items.sort(key=lambda item: item["title"].lower())

    return [
        {"name": name, "items": items}
        for name, items in grouped.items()
    ]


def generate_indices() -> None:
    TEX_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    tex_files = discover_tex_files(TEX_DIR)
    if not tex_files:
        raise SystemExit("No .tex files found in tex/. Add content before building indices.")

    entries: List[Tuple[str, Dict[str, str]]] = []
    search_entries: List[Dict[str, str]] = []
    latest_mtime = max(tex_path.stat().st_mtime for tex_path in tex_files)
    timestamp = datetime.fromtimestamp(latest_mtime, tz=timezone.utc).isoformat()

    for tex_path in tex_files:
        content = tex_path.read_text(encoding="utf-8")
        slug = slugify(tex_path)
        title = extract_title(content, fallback=slug)
        summary = extract_summary(content)
        section = categorize(title, summary)

        item = {
            "title": title,
            "slug": slug,
            "path": f"tex/{tex_path.name}",
            "summary": summary,
        }
        entries.append((section, item))
        search_entries.append(
            {
                "slug": slug,
                "title": title,
                "summary": summary,
                "section": section,
                "path": f"tex/{tex_path.name}",
            }
        )

    sections = build_sections(entries)
    default_slug = next(
        (item["slug"] for section in sections for item in section["items"] if section["items"]),
        tex_files[0].stem,
    )

    index_payload = {
        "generated_at": timestamp,
        "default": default_slug,
        "sections": sections,
    }
    search_payload = {
        "generated_at": timestamp,
        "entries": sorted(search_entries, key=lambda entry: entry["title"].lower()),
    }

    def write_if_changed(path: Path, payload: Dict[str, object]) -> None:
        serialized = json.dumps(payload, indent=2) + "\n"
        if path.exists() and path.read_text(encoding="utf-8") == serialized:
            return
        path.write_text(serialized, encoding="utf-8")

    write_if_changed(INDEX_PATH, index_payload)
    write_if_changed(SEARCH_PATH, search_payload)

    print(f"Discovered {len(tex_files)} LaTeX file(s).")
    for section in sections:
        titles = ", ".join(item["title"] for item in section["items"])
        if not titles:
            titles = "(none)"
        print(f"- {section['name']}: {titles}")
    print(f"Default topic: {default_slug}")
    print(f"Wrote {INDEX_PATH.relative_to(ROOT)} and {SEARCH_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    generate_indices()
