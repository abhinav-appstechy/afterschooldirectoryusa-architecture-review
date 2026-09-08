"""Generate the public review page from the artifact source.

Two things differ between the copies, and both are reversed here:
  * the notes store — a shared database in Claude, this browser on the public page
  * the export path — the downloads capability in Claude, a real file download here

    python3 src/make_review_standalone.py
"""

import re
from pathlib import Path

SRC = Path(__file__).parent / "architecture-review.html"
OUT = Path(__file__).parent.parent / "index.html"
SCHEMA_ART = "https://claude.ai/code/artifact/71155eb2-21c8-4c1b-a187-c78136219e7c"

src = SRC.read_text()

# --- 1. browser-local notes store in place of the capability wiring -------

cap_start = src.index("  /* ---------- capabilities ---------- */")
cap_end = src.index("})();", cap_start)

LOCAL_STORE = '''  /* ---------- local store: notes stay in this browser ---------- */

  var LS_NOTES = "asd-review-notes-v1";
  var handler = null;

  function readAll() {
    try { return JSON.parse(localStorage.getItem(LS_NOTES) || "[]"); }
    catch (e) { return []; }
  }
  function writeAll(list) {
    try { localStorage.setItem(LS_NOTES, JSON.stringify(list)); return true; }
    catch (e) { return false; }
  }
  function emit() {
    if (!handler) return;
    var list = readAll().slice().sort(function (a, b) {
      return String(a.at || "").localeCompare(String(b.at || ""));
    });
    handler({ docs: list.map(function (n) { return { data: function () { return n; } }; }) });
  }

  db = {
    collection: function () {
      return {
        add: function (doc) {
          var list = readAll();
          list.push(doc);
          if (!writeAll(list)) return Promise.reject({ code: "storage_full" });
          emit();
          return Promise.resolve();
        },
        orderBy: function () { return this; },
        onSnapshot: function (next) { handler = next; emit(); return function () { handler = null; }; }
      };
    }
  };

  db.collection("notes").onSnapshot(function (snap) {
    notesBySection = {};
    snap.docs.forEach(function (doc) {
      var n = doc.data() || {};
      var key = typeof n.section === "string" ? n.section : "";
      if (!panels[key]) return;
      (notesBySection[key] = notesBySection[key] || []).push({
        author: typeof n.author === "string" ? n.author.slice(0, 80) : "",
        text: typeof n.text === "string" ? n.text.slice(0, 4000) : "",
        at: typeof n.at === "string" ? n.at : ""
      });
    });
    Object.keys(panels).forEach(renderNotes);
  });

'''

src = src[:cap_start] + LOCAL_STORE + src[cap_end:]

# --- 2. a real file download (works outside the artifact sandbox) ---------

dl_start = src.index('  var dlBtn = document.getElementById("btn-download");')
dl_end = src.index("  /* ---------- local store", dl_start)

DOWNLOAD = '''  var dlBtn = document.getElementById("btn-download");
  dlBtn.addEventListener("click", function () {
    var blob = new Blob([markdown()], { type: "text/markdown;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = "architecture-review-notes.md";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    status.textContent = "Exported \\u2014 send the file back.";
  });

'''

src = src[:dl_start] + DOWNLOAD + src[dl_end:]

# --- 3. tell the reader where their notes actually live ------------------

REPLACEMENTS = [
    (
        "Every section takes notes. They save as you post them and are visible to "
        "everyone with this link. Export collects them all as Markdown.",
        "Every section takes notes. They are saved in <strong>this browser only</strong> "
        "— nobody else sees them. When you have finished, press Export Markdown at "
        "the foot of the page and send the file back.",
    ),
    (
        '<span class="spacer" id="export-status">Notes are shared with everyone holding this link.</span>',
        '<span class="spacer" id="export-status">Your notes stay in this browser. Export when you are done.</span>',
    ),
    (
        "<p>Each section ends with a notes panel. Put your name in once and it is "
        "remembered. Notes are shared with everyone holding this link, so you will "
        "see each other's — please disagree in them.</p>",
        "<p>Each section ends with a notes panel. Put your name in once and it is "
        "remembered. Your notes stay in this browser and are private to you — when "
        "you are done, press <strong>Export Markdown</strong> at the foot of the page "
        "and send the file back.</p>",
    ),
    (
        "Notes cannot load in this view — open the shared link to read and post them.",
        "Notes could not load — your browser may be blocking local storage.",
    ),
]

for old, new in REPLACEMENTS:
    if old not in src:
        raise SystemExit(f"replacement target not found: {old[:60]}...")
    src = src.replace(old, new)

# --- 4. artifact link -> relative path on the public site -----------------

if SCHEMA_ART not in src:
    raise SystemExit("cross-link to the schema page is missing — refusing to publish")
src = src.replace(SCHEMA_ART, "schema.html")

# --- 5. wrap the fragment in a real document -----------------------------

head, body = src.split('<header class="masthead">', 1)
head = head.replace(
    "<title>Claims to Listings</title>",
    "<title>Claims to Listings — architecture review</title>",
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

doc = OUT.read_text()
print("written", round(OUT.stat().st_size / 1024), "KB")
print("  window.claude refs:", doc.count("window.claude"), "(0 expected)")
print("  sections:", len(re.findall(r"<section id=", doc)), "· panels:", doc.count('class="notes" data-section'))
