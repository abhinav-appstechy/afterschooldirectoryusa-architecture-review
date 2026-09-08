# Page sources

The `.html` files here are the **artifact sources** — the versions published to
Claude, with cross-links pointing at artifact URLs. The files at the repository
root are generated from these and are what GitHub Pages serves.

    python3 src/make_schema_standalone.py     # -> ../schema.html
    python3 src/make_review_standalone.py     # -> ../index.html

Edit a source, regenerate, commit both.

## What the generators change

| | Artifact copy | Public copy |
|---|---|---|
| Cross-link | the companion artifact URL | a relative path |
| Document | a fragment; Claude supplies the wrapper | full `<!doctype html>` |
| Review notes | shared database, everyone sees everyone's | this browser only |
| Review export | the downloads capability | a real file download |

Both generators **refuse to run if the cross-link is missing**, so neither page
can ship without a way back to its companion.

## Recovery

These sources were once lost with a temporary directory, which is why they now
live here. If it happens again: take the published root file, strip the document
wrapper, restore the title and the artifact cross-link — and for the review page,
swap the browser-local notes store back for the capability block.

The restoration is verifiable by round trip: regenerate the root file from the
restored source and diff it against what is published. It should be identical.
