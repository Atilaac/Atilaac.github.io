#!/usr/bin/env python3
"""
backfill_publications.py
========================
Enriches existing publication markdown files with new standard fields:
  - authors (parsed from citation field)
  - abstract (moved from body to frontmatter)
  - lay_summary (generated via Claude API, marked as draft)

Usage:
    ANTHROPIC_API_KEY=<key> python scripts/backfill_publications.py [--dry-run] [--pub pub_011]

Options:
    --dry-run      Preview changes without writing files
    --pub PUB_ID   Process only a specific pub (e.g. pub_011). Default: all.
    --no-ai        Skip Claude API lay summary generation
"""

import os
import re
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

REPO_ROOT = Path(__file__).parent.parent
PUBLICATIONS_DIR = REPO_ROOT / "_publications"

# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split markdown into (frontmatter_dict, body). Frontmatter is raw key->value."""
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return {}, text
    end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
    if end is None:
        return {}, text
    fm_lines = lines[1:end]
    body = "\n".join(lines[end + 1:]).lstrip("\n")

    fm: dict = {}
    current_key = None
    current_val: list[str] = []
    for line in fm_lines:
        m = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)', line)
        if m:
            if current_key:
                fm[current_key] = "\n".join(current_val).strip()
            current_key = m.group(1)
            current_val = [m.group(2)]
        elif current_key:
            current_val.append(line)
    if current_key:
        fm[current_key] = "\n".join(current_val).strip()
    return fm, body


def build_frontmatter(fm: dict) -> str:
    """Serialize dict back to YAML frontmatter block."""
    # Field ordering
    order = [
        "title", "collection", "category", "permalink", "excerpt",
        "date", "venue", "volume", "issue", "pages",
        "authors", "paperurl", "abstract", "lay_summary", "lay_summary_draft",
        "pdf_local", "supplementary_url", "slidesurl", "bibtexurl", "citation"
    ]
    lines = ["---"]
    seen = set()
    for key in order:
        if key in fm and fm[key] not in (None, ""):
            val = str(fm[key])
            # Multi-line: use literal block only if newlines present
            if "\n" in val:
                lines.append(f"{key}: |-")
                for l in val.split("\n"):
                    lines.append(f"  {l}")
            else:
                lines.append(f"{key}: {val}")
            seen.add(key)
    # Any remaining keys not in the order list
    for key, val in fm.items():
        if key not in seen and val not in (None, ""):
            lines.append(f"{key}: {val}")
    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Extract abstract from body
# ---------------------------------------------------------------------------

def extract_abstract_from_body(body: str) -> tuple[str, str]:
    """
    Look for ## Abstract (or ## Abstract:) section in body.
    Return (abstract_text, body_without_abstract_section).
    """
    pattern = re.compile(
        r'##\s+Abstract[:\s]*\n(.*?)(?=\n##\s|\Z)',
        re.DOTALL | re.IGNORECASE
    )
    m = pattern.search(body)
    if not m:
        return "", body
    abstract = m.group(1).strip()
    # Remove leading > quote markers if present
    abstract = re.sub(r'^>\s?', '', abstract, flags=re.MULTILINE)
    clean_body = body[:m.start()].rstrip() + "\n" + body[m.end():].lstrip()
    return abstract, clean_body.strip()


# ---------------------------------------------------------------------------
# Parse authors from citation
# ---------------------------------------------------------------------------

def parse_authors_from_citation(citation: str) -> str:
    """
    Extract author portion from a citation string.
    Handles: 'Lastname, F., Smith, J. "Title..."' or 'Atila et al. "Title..."'
    """
    citation = citation.strip().strip('"').strip("'")
    # Find the opening quote that starts the title
    # Citations look like: Author1, Author2. "Title." <i>Venue</i>
    m = re.search(r'["\u201c\u201d\\"]', citation)
    if m:
        authors_raw = citation[:m.start()].strip().rstrip('.').rstrip()
    else:
        # Fallback: take everything before the first period-space-capital sequence
        parts = re.split(r'\.\s+(?=[A-Z"\u201c])', citation)
        authors_raw = parts[0].strip() if parts else citation.split('.')[0].strip()
    # Clean up escaped quotes and trailing punctuation
    authors_raw = authors_raw.replace('\\"', '').replace("\\", "").strip().rstrip('.')
    return authors_raw if authors_raw else ""


# ---------------------------------------------------------------------------
# Claude API lay summary
# ---------------------------------------------------------------------------

def generate_lay_summary(title: str, abstract: str) -> str | None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        prompt = (
            "You are a science communicator. Given the following research paper title and abstract, "
            "write a concise (3-5 sentences) plain-language summary suitable for a general audience. "
            "Explain what was done, what was found, and why it matters. "
            "Avoid jargon. Write in an engaging, accessible tone. "
            "Do not use em dashes (—) or en dashes (–); use commas or rewrite the sentence instead.\n\n"
            f"Title: {title}\n\nAbstract: {abstract}\n\nPlain-language summary:"
        )
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        result = message.content[0].text.strip()
        # safety net: replace any stray dashes
        result = result.replace("—", ",").replace("–", "-")
        return result
    except Exception as e:
        print(f"    [WARNING] Claude API error: {e}")
        return None


# ---------------------------------------------------------------------------
# Process a single file
# ---------------------------------------------------------------------------

def process_file(md_path: Path, dry_run: bool, no_ai: bool) -> bool:
    """Returns True if file was (or would be) modified."""
    text = md_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    if not fm:
        print(f"  [SKIP] Could not parse frontmatter: {md_path.name}")
        return False

    modified = False

    # 1. Extract abstract from body → frontmatter
    if not fm.get("abstract"):
        abstract, new_body = extract_abstract_from_body(body)
        if abstract:
            # Strip wrapping quotes/HTML from abstract value
            clean_abstract = abstract.replace('"', "'").replace('\n', ' ').strip()
            fm["abstract"] = f'"{clean_abstract}"'
            body = new_body
            modified = True
            print(f"    + abstract extracted from body")

    # 2. Parse authors from citation
    if not fm.get("authors"):
        citation = fm.get("citation", "").strip('"').strip("'")
        if citation:
            authors = parse_authors_from_citation(citation)
            if authors:
                fm["authors"] = f'"{authors}"'
                modified = True
                print(f"    + authors: {authors[:60]}")

    # 3. Generate lay summary if not present and abstract available
    if not fm.get("lay_summary") and not no_ai:
        title = fm.get("title", "").strip('"').strip("'")
        abstract_raw = fm.get("abstract", "").strip('"').strip("'")
        if title and abstract_raw:
            print(f"    Generating lay summary via Claude API...")
            lay = generate_lay_summary(title, abstract_raw)
            if lay:
                safe_lay = lay.replace('"', "'").replace('\n', ' ')
                fm["lay_summary"] = f'"{safe_lay}"'
                fm["lay_summary_draft"] = "true"
                modified = True
                print(f"    + lay_summary (draft) added")

    if not modified:
        print(f"  [OK] No changes needed: {md_path.name}")
        return False

    # Rebuild file
    new_content = build_frontmatter(fm) + "\n"
    if body.strip():
        new_content += "\n" + body.strip() + "\n"

    if dry_run:
        print(f"  [DRY RUN] Would update {md_path.name}")
        print("  --- preview (frontmatter only) ---")
        print(build_frontmatter(fm)[:600])
        print("  ---")
    else:
        md_path.write_text(new_content, encoding="utf-8")
        print(f"  [WRITTEN] {md_path.name}")

    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Backfill publication metadata")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--pub", help="Process only this pub (e.g. pub_011)")
    parser.add_argument("--no-ai", action="store_true", help="Skip Claude API lay summary")
    args = parser.parse_args()

    if args.pub:
        files = sorted(PUBLICATIONS_DIR.glob(f"{args.pub}.md"))
    else:
        files = sorted(PUBLICATIONS_DIR.glob("pub_*.md"))

    if not files:
        print(f"No matching files found in {PUBLICATIONS_DIR}")
        sys.exit(1)

    changed = 0
    for md_path in files:
        title_preview = md_path.name
        try:
            fm, _ = parse_frontmatter(md_path.read_text(encoding="utf-8"))
            title_preview = fm.get("title", md_path.name).strip('"').strip("'")[:60]
        except Exception:
            pass
        print(f"\n{md_path.name}: {title_preview}")
        if process_file(md_path, dry_run=args.dry_run, no_ai=args.no_ai):
            changed += 1

    print(f"\nDone. {changed}/{len(files)} file(s) {'would be' if args.dry_run else 'were'} updated.")


if __name__ == "__main__":
    main()
