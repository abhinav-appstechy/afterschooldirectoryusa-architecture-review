# Page sources

`schema.html` here is the **artifact source** — the version published to Claude,
with cross-links pointing at artifact URLs. The file at the repository root is
generated from it and is what GitHub Pages serves.

    python3 src/make_schema_standalone.py

Edit the source, regenerate, commit both. The generator refuses to run if the
cross-link is missing, so a page can never ship without a way back to its
companion.

The published root files are the recovery copy: if a source is ever lost, strip
the document wrapper from the root file and restore the artifact cross-link.
