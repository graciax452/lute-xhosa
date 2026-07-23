# lute-xhosa

An isiXhosa language parser plugin for [Lute3](https://github.com/LuteOrg/lute-v3), splitting agglutinative noun/verb morphology into separately trackable tokens.

Fork of [lute-shona](https://github.com/graciax452/lute-shona), following that project's `DESIGN.md` (section 10) forking guidance. **Read lute-shona's `DESIGN.md` first** — it's the actual design methodology (lexicon-gated stripping to avoid overstemming, the token model, the closed-construction pattern); this project's own `DESIGN.md` only covers what's isiXhosa-specific.

## What this solves

Same problem as Shona: isiXhosa is space-delimited (Lute's stock "Space Delimited" parser gets word boundaries right, including click-consonant letters — `c`, `q`, `x` — which are just ordinary letters within a word), but a single space-delimited word is often several grammatical morphemes glued together, leaving the whole inflected word as one unclickable blob.

**Genuinely different from Shona**, not just a data swap: isiXhosa nouns have a two-layer prefix (an augment vowel plus a class prefix, e.g. `abantu` = `a-` + `ba-` + `-ntu`), and object concords use different surface forms from subject concords in several classes (unlike Shona, where they mostly overlap). See `DESIGN.md` for how the augment+prefix structure turned out to need only more data, not new engine code.

## Status

Working noun-class splitting (all confirmed classes with singular/plural pairs, cross-class shared roots, derivational examples) and verb splitting (infinitives, present-tense `-ya-` infix, class-1 `a-past`). **Not yet implemented**: the `-ile` perfect suffix (structurally different from a prefix TAM marker — needs its own design pass), verbal extensions (causative/applicative/passive — not yet sourced), future tense (reportedly periphrastic, unconfirmed), and most persons' `a-past` forms beyond class 1. See `DESIGN.md` for the full list of what's confirmed vs. deferred, with page citations to the source grammar.

Source: J.C. Oosthuysen, *The Grammar of isiXhosa* (SUN PRESS, 2016), extracted directly from the PDF (see `DESIGN.md` for how — it's a scanned-image book with no text layer).

## Install

```powershell
pip install -e .
```

into whichever venv runs your Lute3 instance. Restart Lute; "isiXhosa" should appear in `Enabled parsers:` at startup and in the language dropdown. Create an isiXhosa language in Lute's Settings with parser type `lute_xhosa`.

## Tests

```powershell
python tests/test_morphology.py
```

Every check was dry-run against the actual code before being written down — see `DESIGN.md` for why that discipline matters here specifically (it caught a real bug: `VERB_ROOT_LEXICON` needs bare roots without the terminal vowel, same convention as lute-shona).

## Optional: highlight grammar tokens

```powershell
python scripts/generate_css.py > xhosa_grammar.css
```

Same mechanism as lute-shona — see its `DESIGN.md` section 8.
