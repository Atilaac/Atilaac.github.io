#!/usr/bin/env bash
# Usage: bash scripts/add_pdf.sh pub-XXX /path/to/paper.pdf [/path/to/supplementary.pdf]
# Copies PDF(s) into files/papers/pub-XXX/ and prints the frontmatter fields to add.

set -e

PUB_ID="$1"
PDF_PATH="$2"
SUPP_PATH="$3"

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST_DIR="$ROOT_DIR/files/papers/$PUB_ID"

if [ -z "$PUB_ID" ] || [ -z "$PDF_PATH" ]; then
  echo "Usage: bash scripts/add_pdf.sh pub-XXX /path/to/paper.pdf [/path/to/supplementary.pdf]"
  exit 1
fi

mkdir -p "$DEST_DIR"

cp "$PDF_PATH" "$DEST_DIR/paper.pdf"
echo "Copied paper.pdf to $DEST_DIR/"

if [ -n "$SUPP_PATH" ]; then
  cp "$SUPP_PATH" "$DEST_DIR/supplementary.pdf"
  echo "Copied supplementary.pdf to $DEST_DIR/"
fi

echo ""
echo "Add these fields to _publications/${PUB_ID//-/_}.md frontmatter:"
echo "  pdf_local: \"/files/papers/$PUB_ID/paper.pdf\""
if [ -n "$SUPP_PATH" ]; then
  echo "  supplementary_url: \"/files/papers/$PUB_ID/supplementary.pdf\""
fi
