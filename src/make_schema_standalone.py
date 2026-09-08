"""Generate the public schema page from the artifact source.

Same content; the only differences are the document wrapper and the cross-link,
which points at a relative path publicly and at the workspace artifact in Claude.

    python3 src/make_schema_standalone.py
"""

from pathlib import Path

SRC = Path(__file__).parent / "schema.html"
OUT = Path(__file__).parent.parent / "schema.html"
REVIEW_ART = "https://claude.ai/code/artifact/4df5bd21-41fa-4069-ae61-11951ea6d084"

src = SRC.read_text()

if REVIEW_ART not in src:
    raise SystemExit("cross-link to the review page is missing — refusing to publish")
src = src.replace(REVIEW_ART, "index.html")

head, body = src.split('<header class="masthead">', 1)
head = head.replace(
    "<title>Tables of Record</title>",
    "<title>Tables of Record — AfterschoolDirectoryUSA schema</title>",
)

OUT.write_text(
    "<!doctype html>\n"
    '<html lang="en">\n'
    "<head>\n"
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<meta name="robots" content="noindex, nofollow">\n'
    + head
    + "</head>\n<body>\n"
    + '<header class="masthead">'
    + body
    + "\n</body>\n</html>\n"
)
print("written", round(OUT.stat().st_size / 1024), "KB")
print("  links to index.html:", OUT.read_text().count('href="index.html"'))
print("  artifact urls left: ", OUT.read_text().count("claude.ai/code/artifact"))
