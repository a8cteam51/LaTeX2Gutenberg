# LaTeX2Gutenberg

A port of [LaTeX2WP](https://sourceforge.net/projects/latex2wp/) that outputs Gutenberg block markup for the WordPress block editor.

## Getting Started

Place `latex2wp.py`, `latex2wpstyle.py`, `macrosblog.tex`, and your `.tex` file in the same directory. Use `post-template.tex` as a starting point, writing your text between `\begin{document}` and `\end{document}`.

An alternative style file, `terrystyle.py`, is also included. To use it, copy it over `latex2wpstyle.py` before running the conversion.

## Usage

```
python latex2wp.py yourlatexfile.tex
```

This produces `yourlatexfile.html`, ready to be pasted into the WordPress block editor. Each paragraph, heading, quote, table, image, and display equation appears as its own editable Gutenberg block.

## Gutenberg Block Output

The converter produces the following block types:

- **Paragraphs** — `<!-- wp:paragraph -->` blocks
- **Sections** — `<!-- wp:heading -->` blocks (`<h2>` for sections, `<h3>` for subsections)
- **Theorem-like environments** — `<!-- wp:quote -->` blocks with inner `<!-- wp:paragraph -->` blocks
- **Display equations** — `<!-- wp:math -->` blocks with MathML annotation containing the raw LaTeX
- **Inline math** — `$latex ...$` WordPress shortcode format
- **Lists** — `<!-- wp:list -->` blocks (ordered and unordered)
- **Tables** — `<!-- wp:table -->` blocks
- **Images** — `<!-- wp:image -->` blocks
- **More tag** — `<!-- wp:more -->` block

## What Works

See `example.tex` for how to import figures, use different text colors, add URL links, and enter the WordPress "more" command.

- `\iftex ... \fi` — compiled by LaTeX, ignored in WordPress conversion
- `\ifblog ... \fi` — converted to WordPress, ignored by LaTeX
- `\iffalse ... \fi` — ignored by both
- Predefined macros: `\E` for `\mathop{\mathbb E}`, `\P` for `\mathop{\mathbb P}`, etc.
- Theorem-like environments: `theorem`, `lemma`, `proposition`, `definition`, `corollary`, `remark`, `example`, `exercise`, and `proof`
- `tabular` environment
- `\label{}`, `\eqref{}`, and `\ref{}`

## What Doesn't Work

- `\align` and `\eqnarray` (WordPress LaTeX limitations)
- `figure` and `table` environments
- `\medskip`, `\bigskip`, and other formatting commands (`\\` is recognized)
- Nesting `\em` inside `\bf` or vice versa
- `\subsubsection` and deeper
- Bibliographic references
- Footnotes

**Important:** An `\em` or `\bf` environment cannot contain curly brackets.

## Customization

Edit `latex2wpstyle.py` to customize the output.

### Pure HTML

Set `HTML = True` to generate standalone HTML that can be previewed in a browser.

### Adding Macros

The variable `M` contains a list of string pairs. Each occurrence of the first string is replaced by the second. Note that `\` must be written as `\\` and `"` as `\"`. Any macro defined in `M` must also be defined in `macrosblog.tex` for LaTeX compilation.

### Theorem Numbering

The variable `T` maps environment names to counter numbers. Environments sharing a counter number share the same numbering sequence (e.g., Lemma 2 followed by Theorem 3). Adjust `maxcounter` if you need more counters.

### New Theorem-like Environments

Add the environment name to `ThmEnvs`, assign it a counter in `T`, and add a corresponding `\newtheorem` in `macrosblog.tex`.

### Theorem Formatting

- `beginthm` / `beginnamedthm` — Use `__QUOTE_START__` and `__QUOTE_END__` markers to delimit the quote block region. The converter wraps the content in `<!-- wp:quote -->` with inner `<!-- wp:paragraph -->` blocks. Use `_ThmType_`, `_ThmNumb_`, and `_ThmName_` placeholders.
- `endthm` — What to output at the end of a theorem-like environment.
- `beginproof` / `endproof` — Proof environment formatting.

### Section Formatting

Set `section`, `sectionstar`, `subsection`, and `subsectionstar`. These should use `<!-- wp:heading -->` block markup with `<h2>` for sections and `<h3>` for subsections.
