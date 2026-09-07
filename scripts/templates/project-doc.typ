// Typst template for this project's rendered docs and notebooks.
//
// Modelled on the sibling 36126-active-fire-research pipeline (markdown →
// pandoc → Typst → PDF), which gives what the previous headless-Chrome
// pipeline could not: a running header, page numbers, and tables that
// paginate instead of overflowing. That project's template lives in a
// `uts-mdsi` repo which is not on this machine, so this is a fresh
// template carrying THIS project's palette rather than a copy of theirs.
//
// Palette matches scripts/render_pdf.py and scripts/make_figures.py:
// heading colour steps down the hierarchy, and lightness steps with hue so
// levels survive greyscale printing.

#let INK = rgb("#1C2333")
#let BLUE = rgb("#31688E")
#let GREEN = rgb("#2D7F5E")
#let MUTED = rgb("#6E7278")
#let RULE = rgb("#D9D6CC")
#let CODE_BG = rgb("#F7F7F5")

// Syntax colours for code blocks, in the same palette as the headings.
// Typst's built-in theme is a generic light scheme whose reds and purples
// match nothing else on the page.
#let CODE_THEME = "code-theme.tmTheme"

#let conf(
  project: "",
  kind: "",
  title: "",
  provenance: "",
  body,
) = {
  set document(title: title)
  set page(
    paper: "a4",
    margin: (x: 20mm, y: 20mm),
    header: context {
      set text(size: 7.5pt, font: "DM Sans 9pt")
      grid(
        columns: (1fr, 1fr),
        align(left, text(fill: BLUE, weight: 600, upper(project))),
        align(right, text(fill: MUTED, kind + sym.space.en + sym.dash.em
                                       + sym.space.en + title)),
      )
      v(-0.4em)
      line(length: 100%, stroke: 0.5pt + RULE)
    },
    footer: context {
      set text(size: 7.5pt, font: "DM Sans 9pt", fill: MUTED)
      align(right, counter(page).display("01"))
    },
  )
  // "DM Sans 9pt", not "DM Sans": Typst names a variable font from its
  // optical-size axis. Getting this wrong is silent -- Typst warns but
  // still compiles, falling back to Libertinus Serif.
  set text(font: "DM Sans 9pt", size: 10pt, fill: INK, lang: "en")
  set par(justify: false, leading: 0.68em)

  // Pandoc wraps tables in #figure, and a Typst figure is an unbreakable
  // block: a long table would be pushed whole to the next page, stranding
  // a near-empty one behind it, or overflow if longer than a page. This
  // project's ledger tables are long, so figures must break.
  show figure: set block(breakable: true)
  show table: set text(size: 8pt)
  set table(stroke: 0.5pt + RULE, inset: 5pt)

  show heading.where(level: 1): it => {
    set text(size: 16pt, weight: 700, fill: INK)
    block(above: 1.4em, below: 0.7em, it)
  }
  show heading.where(level: 2): it => {
    set text(size: 12.5pt, weight: 700, fill: BLUE)
    block(above: 1.3em, below: 0.6em, it)
  }
  show heading.where(level: 3): it => {
    set text(size: 10.5pt, weight: 700, fill: GREEN)
    block(above: 1.1em, below: 0.5em, it)
  }
  show heading.where(level: 4): it => {
    set text(size: 9.5pt, weight: 700, fill: MUTED)
    block(above: 1em, below: 0.4em, it)
  }
  set raw(theme: CODE_THEME)
  show raw.where(block: true): it => block(
    width: 100%, fill: CODE_BG, inset: 7pt, radius: 2pt,
    stroke: (left: 2pt + BLUE, rest: 0.5pt + RULE),
    text(size: 7.6pt, it),
  )
  show raw.where(block: false): it => box(
    fill: CODE_BG, inset: (x: 2.5pt, y: 0pt), outset: (y: 2.5pt),
    radius: 1.5pt, text(size: 8.2pt, it),
  )
  show link: set text(fill: BLUE)

  // The provenance stamp — which file, at which commit — sits above the
  // title so a printed PDF says exactly what it was rendered from. Adopted
  // from the fire-research pipeline; it suits a project whose whole claim
  // is that results trace to a recorded source.
  if provenance != "" {
    text(size: 7.5pt, fill: MUTED, provenance)
    v(0.4em)
  }
  text(size: 20pt, weight: 700, fill: INK, title)
  v(0.3em)
  line(length: 100%, stroke: 1.2pt + INK)
  v(1em)

  body
}
