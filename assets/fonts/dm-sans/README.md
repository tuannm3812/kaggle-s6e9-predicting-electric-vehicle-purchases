# DM Sans (SIL Open Font License 1.1)

Variable TTFs used by `scripts/render_pdf.py`, which **embeds them as
base64 data URIs** in the print stylesheet. That is deliberate: naming a
font in CSS only makes the renderer look it up on the local machine, so
an un-installed font is silently substituted and the layout shifts —
exactly the trap documented in
`4. Training/unsw-ma-hackathon-2026/docs/presentation/fonts/README.md`.
Embedding makes a rendered PDF reproduce identically on any machine.

Variable rather than static Regular/Bold: one file covers the whole
weight axis, and the companion italic gives real italics instead of the
synthesised oblique a renderer falls back to.

`OFL.txt` must travel with these files — the licence permits
redistribution only with the copyright notice and licence included.
Source: copied 2026-09-05 from the sibling hackathon repo, which
documents DM Sans as the open substitute for Google Sans.
