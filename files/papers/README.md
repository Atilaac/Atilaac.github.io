# Papers File Repository

Each subdirectory corresponds to one publication entry in `_publications/`.

## Naming Convention

```
files/papers/pub-XXX/
  paper.pdf           # Main paper PDF (required for download button to appear)
  supplementary.pdf   # Supplementary materials (optional)
```

## Linking in Publication Frontmatter

In `_publications/pub_XXX.md`, set:

```yaml
pdf_local: "/files/papers/pub-XXX/paper.pdf"
supplementary_url: "/files/papers/pub-XXX/supplementary.pdf"
```

Leave these fields blank (or omit them) if no files are available yet.

## Adding a New Paper's Files

1. Drop `paper.pdf` into `files/papers/pub-XXX/`
2. Update the `pdf_local` field in `_publications/pub_XXX.md`
3. Commit both the PDF and the updated markdown file

Or use the helper script:
```bash
bash scripts/add_pdf.sh pub-XXX /path/to/paper.pdf
```
