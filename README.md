# lute-xhosa

An isiXhosa language parser plugin for [Lute3](https://github.com/LuteOrg/lute-v3), splitting agglutinative noun/verb morphology into separately trackable tokens.

**Status: scaffold only.** This is a fork of [lute-shona](https://github.com/graciax452/lute-shona), started per that project's `DESIGN.md` (section 10) forking guidance, before any real isiXhosa data has been added. Every table in `lute_xhosa_parser/rules.py` is currently empty, so the parser installs, runs, and safely leaves every word whole — it doesn't split anything useful yet. See that file's docstring for exactly what's expected to change once real reference material comes in.

## What this will solve (once populated)

isiXhosa, like Shona, is space-delimited — Lute's stock "Space Delimited" parser already gets word boundaries right, including click-consonant letters (`c`, `q`, `x` and their combinations), which are just ordinary letters within a word, not separate tokens. The problem is that a single space-delimited word is often several grammatical morphemes glued together (noun class prefix, verb subject/tense/object/extension affixes), leaving the whole inflected word as one unclickable blob in Lute. See lute-shona's `README.md`/`DESIGN.md` for the full writeup of this problem and the lexicon-gated design used to solve it — the same design is copied here as a starting point.

**Read lute-shona's `DESIGN.md` before adding data here.** It documents the full methodology (lexicon-gated stripping to avoid overstemming, the token model, the closed-construction pattern, real mistakes made and corrected) that this fork should follow, not reinvent — and explicitly flags what's Shona-specific (don't assume it transfers) vs. what's likely general to Bantu-language morphology (the engine architecture, the safety principles).

## Install

```powershell
pip install -e .
```

into whichever venv runs your Lute3 instance. Restart Lute; "isiXhosa" should appear in `Enabled parsers:` at startup and in the language dropdown (it registers correctly even with empty tables — it just won't split anything until `rules.py` has real data). Create an isiXhosa language in Lute's Settings with parser type `lute_xhosa`.

## Tests

```powershell
python tests/test_morphology.py
```

Currently only checks the empty-lexicon safe-fallback behavior. Expand the same way lute-shona's test suite grew: dry-run every new example against `split_word()` directly before writing down an expected result — lute-shona's history has several instances of a hand-traced expectation turning out wrong once actually run.

## Optional: highlight grammar tokens

```powershell
python scripts/generate_css.py > xhosa_grammar.css
```

Same mechanism as lute-shona — see its `DESIGN.md` section 8.
