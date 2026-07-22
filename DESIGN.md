# Design notes: lute-xhosa

This file is a placeholder. `lute-shona`'s `DESIGN.md` is the actual
methodology document to read first — this fork was started by following
its section 10 ("Forking for another Bantu language") verbatim:

1. Copy the package, rename the entry point. Done (`lute_xhosa_parser`,
   entry point `lute_xhosa`, class `XhosaParser`).
2. Replace `rules.py` entirely — it's 100% language-specific data.
   Not done yet: every table in `rules.py` is currently empty.
   Nothing in it should be assumed to transfer from Shona.
3. Start with `morphology.py`/`parser.py` unchanged, and see how far the
   *engine* (not the data) actually gets you. Done as a starting
   hypothesis, **not** a settled decision — two things were
   deliberately *not* carried over because they're confirmed
   Shona-specific idioms with no assumed isiXhosa equivalent:
   `_try_negative_have()` (Shona's `ha- + concord + -na` construction)
   and `_try_sati_construction()` (`[subject] + sati`, "before ~ing").
   If isiXhosa turns out to have analogous closed constructions, add
   them the same deliberate way Shona's were added — see lute-shona
   `DESIGN.md` section 7, especially its closing paragraph on the
   deciding question (is the pattern productive, are both boundaries
   closed-class?) before writing a rule instead of a whole-word
   exception.
4. Only after this is actually working should a shared `BantuParser`
   base class be extracted, comparing the two real `morphology.py`
   files — not before, and not as a guess.
5. Expect the same category of judgment calls lute-shona hit
   repeatedly (whole-word exception vs. small dedicated rule; true
   homonyms vs. branch-ordering collisions; short-root collision risk).
   Read lute-shona's `DESIGN.md` sections 7 and 9 for the concrete,
   worked examples before re-deriving the same lessons from scratch.

## What's actually isiXhosa-specific and needs real sourcing

Everything in `rules.py` (noun class inventory, verb subject/TAM/
object/extension forms, terminal vowels, any closed constructions).
isiXhosa is a Nguni language (like Zulu), while Shona is a Shona-group
language — related, but with real, expected differences: different
noun class prefixes, click consonants, different phonological rules
(its own vowel-coalescence/elision patterns, not Shona's). Do not port
Shona's specific prefix/root strings here on the assumption they're
"close enough" — confirm each one from real isiXhosa reference
material or a fluent speaker, the same discipline lute-shona used
throughout (see that project's DESIGN.md section 2 for what counts as
adequate sourcing, and section 11 for why getting corrections right
mattered more than avoiding them).

This file should be rewritten from scratch once real isiXhosa data and
decisions exist — treat it the way lute-shona's `DESIGN.md` looked
after its first real noun-class table was mined, not as a final
document.
