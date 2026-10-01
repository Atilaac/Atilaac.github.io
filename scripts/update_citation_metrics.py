import datetime
import pathlib
import re
import urllib.request

SCHOLAR_ID = "TTAujLUAAAAJ"
URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
OUTPUT = pathlib.Path(__file__).resolve().parent.parent / "_data" / "scholar_metrics.yml"

request = urllib.request.Request(URL, headers={"User-Agent": USER_AGENT})
with urllib.request.urlopen(request, timeout=60) as response:
    html = response.read().decode("utf-8", errors="replace")

# Stats table cells, in order: citations, h-index, i10-index, each as (all, since 5 years ago)
values = [int(value) for value in re.findall(r'class="gsc_rsb_std">(\d+)<', html)]
if len(values) != 6 or values[0] <= 0:
    raise SystemExit(f"Could not read metrics from Google Scholar (blocked or page changed): found {values}")

OUTPUT.write_text(
    f"citations: {values[0]}\n"
    f"h_index: {values[2]}\n"
    f"i10_index: {values[4]}\n"
    f"last_updated: '{datetime.date.today().isoformat()}'\n"
)
print({"citations": values[0], "h_index": values[2], "i10_index": values[4]})
