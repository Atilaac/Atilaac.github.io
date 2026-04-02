#!/usr/bin/env python3
"""
fetch_publications.py
=====================
Fetches publications from Google Scholar and generates Jekyll markdown files
for the academic website. Optionally uses Claude API to generate lay summaries.

Usage:
    GOOGLE_SCHOLAR_ID=<id> ANTHROPIC_API_KEY=<key> python fetch_publications.py

Environment variables:
    GOOGLE_SCHOLAR_ID   (required) Your Google Scholar author ID
    ANTHROPIC_API_KEY   (optional) Anthropic API key for auto lay-summary generation
    DRY_RUN             (optional) Set to "1" to preview without writing files
"""

import os
import re
import json
import glob
import html
from datetime import datetime
from pathlib import Path

from scholarly import scholarly

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
PUBLICATIONS_DIR = REPO_ROOT / "_publications"
RESULTS_DIR = SCRIPT_DIR / "results"

DRY_RUN = os.environ.get("DRY_RUN", "0") == "1"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def html_escape(text: str) -> str:
    return html.escape(str(text), quote=False)


def next_pub_number(publications_dir: Path) -> int:
    """Return the next available sequential pub number."""
    existing = sorted(publications_dir.glob("pub_*.md"))
    if not existing:
        return 1
    last = existing[-1].stem  # e.g. "pub_022"
    return int(last.split("_")[1]) + 1


def load_existing_titles(publications_dir: Path) -> set:
    """Return a set of lowercased titles already in the publications dir."""
    titles = set()
    for md_file in publications_dir.glob("pub_*.md"):
        content = md_file.read_text(encoding="utf-8")
        m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', content, re.MULTILINE)
        if m:
            titles.add(m.group(1).strip().lower())
    return titles


def generate_lay_summary(title: str, abstract: str) -> str | None:
    """
    Call Claude API to generate a draft lay summary.
    Returns None if ANTHROPIC_API_KEY is not set or call fails.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        prompt = (
            f"You are a science communicator. Given the following research paper title and abstract, "
            f"write a concise (3-5 sentences) plain-language summary suitable for a general audience. "
            f"Explain what was done, what was found, and why it matters. "
            f"Avoid jargon. Write in an engaging, accessible tone.\n\n"
            f"Title: {title}\n\nAbstract: {abstract}\n\nPlain-language summary:"
        )
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    except Exception as e:
        print(f"  [WARNING] Could not generate lay summary: {e}")
        return None


def format_authors(pub_data: dict) -> str:
    """Extract and format the author list from scholarly publication data."""
    bib = pub_data.get("bib", {})
    author_str = bib.get("author", "")
    if not author_str:
        return ""
    # scholarly returns "Lastname, Firstname and Lastname2, Firstname2 ..."
    authors = [a.strip() for a in author_str.split(" and ")]
    formatted = []
    for a in authors:
        parts = [p.strip() for p in a.split(",")]
        if len(parts) == 2:
            last, first = parts
            # Use initials for first name
            initials = ".".join(n[0] for n in first.split() if n) + "."
            formatted.append(f"{initials} {last}")
        else:
            formatted.append(a)
    return ", ".join(formatted)


def make_markdown(pub_num: int, pub_data: dict, lay_summary: str | None) -> tuple[str, str]:
    """
    Build Jekyll frontmatter + body for a publication.
    Returns (filename, markdown_content).
    """
    bib = pub_data.get("bib", {})

    title = bib.get("title", "Untitled").replace("{", "").replace("}", "")
    authors = format_authors(pub_data)
    venue = bib.get("journal") or bib.get("booktitle") or bib.get("venue") or ""
    venue = venue.replace("{", "").replace("}", "")
    year = bib.get("pub_year") or bib.get("year") or "1900"
    volume = bib.get("volume", "")
    issue = bib.get("number", "")
    pages = bib.get("pages", "")
    abstract = bib.get("abstract", "")

    # Determine category
    if bib.get("booktitle"):
        category = "conferences"
    else:
        category = "manuscripts"

    pub_id = f"pub-{pub_num:03d}"
    pub_file = f"pub_{pub_num:03d}"
    date_str = f"{year}-01-01"

    # Citation
    citation = f'{authors}. "{html_escape(title)}." <i>{html_escape(venue)}</i>. ({year}).'

    # Excerpt: first sentence of abstract, or title
    if abstract:
        excerpt = abstract.split(".")[0].strip() + "."
    else:
        excerpt = title

    # Build frontmatter
    fm = f'---\n'
    fm += f'title: "{html_escape(title)}"\n'
    fm += f'collection: publications\n'
    fm += f'category: {category}\n'
    fm += f'permalink: "/publication/{pub_id}"\n'
    fm += f'excerpt: "{html_escape(excerpt)}"\n'
    fm += f'date: {date_str}\n'
    if venue:
        fm += f'venue: "{html_escape(venue)}"\n'
    if volume:
        fm += f'volume: "{volume}"\n'
    if issue:
        fm += f'issue: "{issue}"\n'
    if pages:
        fm += f'pages: "{pages}"\n'
    if authors:
        fm += f'authors: "{html_escape(authors)}"\n'

    # Paper URL
    eprint = pub_data.get("eprint_url") or ""
    pub_url = pub_data.get("pub_url") or ""
    paper_url = eprint or pub_url or ""
    if paper_url:
        fm += f'paperurl: "{paper_url}"\n'

    # Lay summary
    if lay_summary:
        safe_lay = lay_summary.replace('"', "'").replace('\n', ' ')
        fm += f'lay_summary: "{safe_lay}"\n'
        fm += f'lay_summary_draft: true\n'

    # Abstract in frontmatter
    if abstract:
        safe_abstract = abstract.replace('"', "'").replace('\n', ' ')
        fm += f'abstract: "{html_escape(safe_abstract)}"\n'

    fm += f'citation: "{html_escape(citation)}"\n'
    fm += f'---\n'

    # Body
    body = ""
    if abstract:
        body += f"\n## Abstract\n{abstract}\n"
    if lay_summary:
        body += f"\n## Plain Language Summary\n> **Draft** — review and edit before publishing.\n\n{lay_summary}\n"

    return f"{pub_file}.md", fm + body


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    scholar_id = os.environ.get("GOOGLE_SCHOLAR_ID")
    if not scholar_id:
        raise SystemExit("ERROR: Set GOOGLE_SCHOLAR_ID environment variable.")

    print(f"Fetching author profile for ID: {scholar_id}")
    author = scholarly.search_author_id(scholar_id)
    scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])

    name = author.get("name", "Unknown")
    print(f"Author: {name} — {len(author['publications'])} publications found on Scholar\n")

    # Save updated gs_data.json (citation counts etc.)
    RESULTS_DIR.mkdir(exist_ok=True)
    author_copy = dict(author)
    author_copy["updated"] = str(datetime.now())
    author_copy["publications"] = {
        v["author_pub_id"]: v for v in author["publications"]
    }
    with open(RESULTS_DIR / "gs_data.json", "w", encoding="utf-8") as f:
        json.dump(author_copy, f, ensure_ascii=False, indent=2)

    shieldio_data = {
        "schemaVersion": 1,
        "label": "citations",
        "message": str(author.get("citedby", 0)),
    }
    with open(RESULTS_DIR / "gs_data_shieldsio.json", "w", encoding="utf-8") as f:
        json.dump(shieldio_data, f, ensure_ascii=False)

    # Load existing papers to avoid duplicates
    existing_titles = load_existing_titles(PUBLICATIONS_DIR)
    next_num = next_pub_number(PUBLICATIONS_DIR)

    new_count = 0
    skipped_count = 0

    for pub in author["publications"]:
        # Fill publication details
        try:
            scholarly.fill(pub)
        except Exception as e:
            print(f"  [WARNING] Could not fill pub '{pub.get('bib', {}).get('title', '?')}': {e}")

        bib = pub.get("bib", {})
        title = bib.get("title", "").replace("{", "").replace("}", "").strip()

        if not title:
            print("  [SKIP] Empty title")
            skipped_count += 1
            continue

        if title.lower() in existing_titles:
            print(f"  [SKIP] Already imported: {title[:70]}")
            skipped_count += 1
            continue

        print(f"  [NEW] {title[:70]}{'...' if len(title) > 70 else ''}")

        # Generate lay summary
        abstract = bib.get("abstract", "")
        lay_summary = None
        if abstract:
            print("       Generating lay summary via Claude API...")
            lay_summary = generate_lay_summary(title, abstract)
            if lay_summary:
                print("       Done.")

        filename, content = make_markdown(next_num, pub, lay_summary)

        if DRY_RUN:
            print(f"\n--- DRY RUN: would write {filename} ---\n{content[:500]}\n---\n")
        else:
            out_path = PUBLICATIONS_DIR / filename
            out_path.write_text(content, encoding="utf-8")
            print(f"       Written: {out_path}")

        existing_titles.add(title.lower())
        next_num += 1
        new_count += 1

    print(f"\nDone. {new_count} new paper(s) added, {skipped_count} skipped.")


if __name__ == "__main__":
    main()
