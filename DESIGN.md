# Design notes: lute-xhosa

**Read lute-shona's `DESIGN.md` first.** It's the actual methodology
document — lexicon-gated stripping to avoid overstemming, the token
model, the closed-construction pattern, the many worked examples of
mistakes made and corrected. This file only records what's specific to
the isiXhosa fork: what was carried over, what's genuinely different,
and what's deliberately deferred rather than guessed at.

## Source material

- **J.C. Oosthuysen, "The Grammar of isiXhosa" (SUN PRESS, 2016)** —
  a published academic grammar (Stellenbosch University Press),
  confirmed via a matching JSTOR listing (`jstor.org/stable/j.ctv1nzg1tj`).
  This is the primary source for everything in `rules.py` marked with
  a page citation. It's a scanned-image PDF with no text layer
  (`pypdf`/`pdftotext` both return empty), so it was read by rendering
  pages to PNG with `pdftoppm` (installed via `winget install
  oschwartz10612.Poppler` — the machine's original Read-tool PDF
  path needed `poppler-utils`, not present by default) and reading the
  images directly. 396 pages; navigated via the table of contents
  (pp. i–ix, no embedded bookmarks) rather than reading sequentially.
- **furman.edu isiXhosa noun-class course notes**, citing the Oxford
  Xhosa-English dictionary — cross-checked against Oosthuysen's noun
  class table and found consistent on every point checked, plus
  supplied the derivational-noun examples (`-qhekeza`, `-phula` forming
  different nouns across classes) used to seed several
  `NOUN_ROOT_LEXICON` cross-class entries.
- **A "cross-checked" summary from a parallel conversation** (citing
  Wiktionary's Xhosa appendix, UCT course notes, an academic paper, and
  MasakhaNER) — used as an initial orientation before Oosthuysen was
  found, largely confirmed by it afterward (person-based subject
  concords, the general augment+prefix structural claim). Superseded
  by direct primary-source extraction wherever the two differ in
  detail (e.g. exact per-class concord forms).
- **A generic AI-written "parser blueprint"** — rejected outright as a
  code source. Verified directly against the installed Lute source
  that its `ParsedToken(token_text=..., lemma=...)` call would crash
  (`ParsedToken.__init__` only accepts `token`/`is_word`/
  `is_end_of_sentence`) and its `get_name()` method wouldn't be
  recognized by Lute's registry (`AbstractParser` requires a `name()`
  classmethod). Written without checking Lute's actual API. Not used
  for any code or data.
- **A "Understanding Noun Classes" lesson page** — rejected entirely
  as unreliable, not reconciled with anything. It misclassified
  `isikolo` (school) into class 5 instead of 7 (every other source,
  correctly, puts it in 7), listed `"ocean-"` as a literal noun-class
  prefix (not a real morpheme), and invented separate classes 12/13/14
  all as `uku-` with different examples, when isiXhosa has no classes
  12/13 at all and `uku-` is simply class 15. Internally inconsistent
  and contradicted every other source — the kind of thing to actively
  watch for and discard, not average in with better sources.

## What's carried over from Shona unchanged, and why it turned out to be enough

`morphology.py`'s cascade structure, the lexicon-gating principle, and
even `_try_noun`'s code are **unchanged from Shona** — no new stripping
logic was needed for isiXhosa's two-layer augment+prefix noun structure
(see below). `_try_verb_slot` and `_resolve_stem` are also structurally
unchanged; only the *data* they read (`VERB_SUBJECT_PREFIXES`,
`OBJECT_MARKERS`, `TAM_MARKERS`, `PAST_SUBJECT_PREFIXES`,
`VERB_ROOT_LEXICON`) is isiXhosa-specific. Every example gathered so
far (noun class pairs, derivational nouns, infinitives, present tense,
a-past) dry-ran correctly against this unchanged engine on the first
try — a genuinely useful data point for how much of lute-shona's
architecture actually is Bantu-general rather than Shona-specific, as
speculated in that project's forking guidance.

Not carried over: `_try_negative_have()` and `_try_sati_construction()`
(Shona's confirmed `ha- + concord + -na` and `[subject] + sati`
constructions) — no isiXhosa equivalent has been confirmed, so there's
nothing to add yet. If/when one turns up, add it the same deliberate
way Shona's were: confirm it's productive (not a one-off idiom) and has
fixed, closed-class boundaries before writing a rule instead of a
whole-word exception.

## The augment+prefix noun structure — a real architectural question, resolved through data, not code

isiXhosa nouns have two layers where Shona has one: an augment vowel
(`u-`/`a-`/`i-`/`oo-`, varies by class) plus a class prefix (`m-`,
`ba-`, `si-`, ...), e.g. `abantu` = augment `a-` + prefix `ba-` + root
`-ntu`. Critically, **the augment drops independently** in some
constructions (vocatives, certain imperatives, per Oosthuysen and
cross-confirmed by the earlier summary's Wiktionary citation on
`Musani ukutya`) — so it can't just be folded into one fixed per-class
prefix string the way Shona's single-layer prefixes work.

The question going in was whether this needed new stripping logic in
`_try_noun` (try augment, then try prefix, as two independent steps).
**It didn't.** Since `_try_noun` already tries every matching prefix
candidate (sorted longest-first) against the same root lexicon, simply
listing *both* the augmented form (`"aba"`) and the bare class-prefix
form (`"ba"`) as separate entries in `NOUN_CLASS_PREFIXES` reproduces
the two-layer behavior entirely through data — the existing longest-
match-first, lexicon-gated loop handles augmented and augment-dropped
forms identically, correctly, with zero new code. This was verified by
dry-running every collected example, not assumed. Worth remembering
for any future fork: a linguistic difference that sounds like it needs
new engine logic sometimes just needs a richer prefix table instead —
check before assuming a code change is required.

## Concord tables: genuinely different from Shona, not just relabeled

Unlike Shona, where subject and object markers mostly share the same
surface forms, isiXhosa's differ in several places — confirmed from
Oosthuysen's full concord tables (subject: p.175, object: p.183):

- 2sg subject is `u-`, but 2sg object is `-ku-`.
- Class 1 subject is `u-` (or `a-` in some moods), but class 1 object
  is the syllabic `-m-`.
- Several other classes differ similarly (3/4: subject `u-`/`i-` vs.
  object `-wu-`/`-yi-`; 5/6: subject `li-`/`a-` vs. object `-li-`/
  `-wa-`).

This is exactly why `OBJECT_MARKERS` is its own independently-sourced
table, not derived from `VERB_SUBJECT_PREFIXES` — a design that was
already correct for Shona (where the two tables happen to overlap a
lot) but matters much more here.

**`ku-` is more overloaded here than in Shona.** It's simultaneously:
the class 15 infinitive prefix, the class 17 locative prefix, the
class 15/17 *subject* concord, and *both* the 2sg *and* class 15/17
*object* concord — four distinct jobs on one string, versus Shona's
three-way overload on `ku-`. Handled the same way: `_try_infinitive`
is checked first and gated on the verb root lexicon, everything else
falls through to the general engine, which is itself gated on its own
lexicons. No special-casing beyond that; flagged here so a future
maintainer doesn't mistake the ambiguity for a bug.

## Tense/aspect: a real structural difference from Shona, not fully built yet

Shona's tense system is a simple TAM-prefix slot (`-no-`/`-cha-`/`-ka-`,
between subject and object). isiXhosa's is not a single mechanism:

- **Imperfect/present**: `-ya-` infix in the same slot position as
  Shona's TAM markers (`ndiyasebenza` = `ndi`+`ya`+`sebenza`) — fits
  the existing engine directly, **implemented**.
- **A-past**: subject concord + `-a-` coalescing into a fused prefix
  (`wadala` = `u-` + `a-` → `wa-` + `dala`) — structurally identical
  to Shona's `nda-`/`wa-`/`ta-`/`ma-` family, fits `PAST_SUBJECT_PREFIXES`
  directly. **Only class 1's `wa-` form is confirmed and implemented**;
  other persons' a-past fusions are unconfirmed and must not be
  guessed by analogy to Shona's paradigm — isiXhosa's actual forms
  need their own source before going in the table.
  - Note: `"a-past tense"` in Oosthuysen's own terminology (a vowel
    length distinction) — take this at face value from the source, not
    as a guess about what "should" parallel Shona.
- **Perfect**: an `-ile` **suffix** near the end of the word
  (`bahambile` = `ba` + `hamb` + `ile`), not a prefix at all. This
  doesn't fit the current TAM slot mechanism — it needs a real change
  to `_resolve_stem`'s terminal-vowel contract (which currently assumes
  a single-character vowel, not a 3-character suffix). **Deliberately
  NOT implemented** rather than forced into the wrong slot; words using
  it (`bahambile`, `ndifundile`) currently and correctly stay whole.
  Design this properly in its own pass rather than bolting it onto the
  existing single-vowel assumption.
- **Future**: reportedly periphrastic (auxiliary `ukuza` "to come" +
  infinitive, per the earlier cross-checked summary's Wiktionary
  citation) — genuinely different from Shona's single fused prefix
  `-cha-`. Not yet independently verified against Oosthuysen directly,
  but partially corroborated by real text: "Ngoku ndiza kufa ndifela
  inceba yam" ("Now I am going to die...") in the story tested in the
  next section uses exactly this shape (`ndiza` + infinitive `kufa`,
  augment dropped). No dedicated engine support added — it happens to
  split correctly already because `kufa`'s `ku-` gets matched as the
  class 15/17 subject concord by the general verb-slot branch, landing
  on the same tokens a dedicated periphrastic-future rule would
  produce. Worth building a real rule for this later if it turns out
  to matter for cases the current accidental path doesn't cover, but
  not urgent given the output is already correct.

## Real-text validation round (`Ingonyama nenkawu` — The Lion and the Monkey)

Same validation method as lute-shona's grandpa-tortoise story: run a
real, unfamiliar narrative through `split_word` rather than only
testing against constructed examples. Of 338 unique words, 7 split and
331 stayed whole (expected — the seed lexicons are still small). Of
the 7: 5 were correct out of the box (`indlela`, `kufa`, `ndihambe`,
`ukubona`, `ukutya` — see `test_real_story_correct_splits`), and 2 were
genuine collisions, both found by testing, not by inspection:

- **`kudala`** — verb-slot resolves it as `ku-` (cl.15/17 subject
  concord) + `dal-` (seeded root "create") + `-a`, i.e. "it creates" —
  because `dal` is a seeded verb root and the shape happens to fit.
  Actual meaning in context ("Kudala ndilapha okoko kwakusasa" — "I've
  been here a long time, since this morning"): the fixed temporal
  adverb "long ago"/"for a long time," unrelated to the verb.
- **`uthi`** — the noun branch resolves it as `u-` (augment, cl.1a/11)
  + `thi` (seeded noun root "tree/stick"), i.e. "a stick." Actual
  meaning in context ("...uthi, '...'" — "...and say, '...'"): the verb
  "you say" (`u-` + `-thi-`). A true homonym, same category as
  lute-shona's `kamba` (tortoise vs. small house) — `thi` isn't even
  seeded as a verb root, so only the wrong noun reading could fire.

Both protected via `WORD_EXCEPTIONS` rather than any structural change
— removing the `u`/`ku` prefixes that enable these collisions would
also break the many words they correctly split elsewhere (`uthando`,
`uluthi`, `ukutya`, `ukufa`, ...). Same lesson as lute-shona's
`mudzidzisi`/`mukanwa`: a short, useful prefix will occasionally
collide with a real word; fix the specific collision, keep the prefix.

## Known gaps, not guessed at

- **Verbal extensions** (causative/applicative/passive/reciprocal) —
  not yet located in Oosthuysen. The general CARP ordering principle
  (Causative→Applicative→Reciprocal→Passive) is very likely to hold,
  being Nguni/Bantu-wide, but the exact isiXhosa surface forms need
  their own source before going in `VERB_EXTENSIONS` — do not assume
  Shona's `-is-`/`-ir-`/`-w-`/`-an-` forms transfer.
- **The reflexive link `-zi-`** — confirmed to exist (Oosthuysen 10.4,
  p.185) but not yet read in detail. Currently just noted as a possible
  second meaning of the `zi` entry in `OBJECT_MARKERS` (already used
  for cl.7/8/9/10 plural object) — genuinely ambiguous until read
  properly.
- **Consonant-mutated derivational forms** — e.g. class 9's
  `inkqekezo` (from `-qhekeza`) surfaces with a mutated root
  (`nkqekez-`, not `qhekez-`), the same unmodeled-mutation category as
  Shona's class 5. Not seeded; falls back safely to whole-word.
- **`NOUN_ROOT_LEXICON` is small and citation-example-driven**, same
  caveat as Shona's — most isiXhosa nouns outside the seed won't split
  yet. Grow from real text, not more reference-grammar mining in the
  abstract, per lute-shona DESIGN.md section 9's calibration finding.

## Forking notes for whoever builds the next one

The augment+prefix "solved by data, not code" result (above) is worth
testing again on a third language before treating it as a general
Bantu-fork pattern — one confirmation isn't a rule. The concord-table
divergence (object markers genuinely different from subject markers)
is a good reminder that "looks similar to Shona" is a hypothesis to
verify per-table, not a starting assumption — check the actual data
before assuming reuse, the same discipline used throughout both of
these projects.
