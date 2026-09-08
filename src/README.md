# Page sources

`architecture-review.html` here is the **artifact source** for `../index.html` — the version
published to Claude, with the cross-link pointing at an artifact URL.

    python3 src/make_review_standalone.py     # -> ../index.html

`schema.html`, `python.html` and `laravel.html` at the repository root are edited directly.
They have no Claude artifact and no generator.

## Recovery

If a source is lost, take the published root file and strip the document wrapper — for the
review page also restore the title, the artifact cross-link, and swap the browser-local
notes store back for the capability block. Verify by round trip: regenerate and diff
against what is published. It should be identical.
