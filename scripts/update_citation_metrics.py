import datetime
import json
import pathlib
import urllib.request

ORCID = "0000-0003-4148-5908"
URL = f"https://api.openalex.org/authors/orcid:{ORCID}?select=cited_by_count,summary_stats&mailto=achraf.atila@gmail.com"
OUTPUT = pathlib.Path(__file__).resolve().parent.parent / "_data" / "scholar_metrics.yml"

with urllib.request.urlopen(URL, timeout=60) as response:
    author = json.load(response)

metrics = {
    "citations": int(author["cited_by_count"]),
    "h_index": int(author["summary_stats"]["h_index"]),
    "i10_index": int(author["summary_stats"]["i10_index"]),
}
if metrics["citations"] <= 0:
    raise SystemExit(f"Refusing to write implausible metrics: {metrics}")

OUTPUT.write_text(
    f"citations: {metrics['citations']}\n"
    f"h_index: {metrics['h_index']}\n"
    f"i10_index: {metrics['i10_index']}\n"
    f"last_updated: '{datetime.date.today().isoformat()}'\n"
)
print(metrics)
