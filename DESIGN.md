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

## What's carried over from Shona unchanged, and why it turned out to be (almost) enough

`morphology.py`'s cascade structure and the lexicon-gating principle
are unchanged from Shona, and initially `_try_noun`'s code was too —
no new stripping logic was needed for isiXhosa's two-layer
augment+prefix noun structure (see below), and every example gathered
before the bulk lexicon import (noun class pairs, derivational nouns,
infinitives, present tense, a-past) dry-ran correctly against the
unmodified engine on the first try — a genuinely useful data point for
how much of lute-shona's architecture is Bantu-general rather than
Shona-specific, as speculated in that project's forking guidance.
`_try_verb_slot` and `_resolve_stem` remain structurally unchanged
throughout; only the *data* they read (`VERB_SUBJECT_PREFIXES`,
`OBJECT_MARKERS`, `TAM_MARKERS`, `PAST_SUBJECT_PREFIXES`,
`VERB_ROOT_LEXICON`) is isiXhosa-specific.

`_try_noun` did end up needing one real change, though — not from the
augment+prefix structure itself, but from growing the lexicon by 20x
(see the bulk-import section below): a latent gap where the
"before vowel-initial stem" allomorphs (`ab-`, `am-`, `is-`, `iz-`,
`ub-`) weren't actually vowel-gated in code, just in a comment. It took
a big enough lexicon for a coincidental collision to surface the gap.
Worth remembering: "unchanged and correct so far" isn't the same claim
as "provably correct" — it just means nothing has stressed that code
path hard enough yet.

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

(These 7/338 numbers are the pre-bulk-import baseline, seed lexicon
only. See below for what the same story looks like after the
isixhosa.click import — coverage jumps substantially, at the cost of
a handful of new collisions from the larger lexicon.)

## Bulk lexicon import from isixhosa.click — coverage vs. collision surface

Manually seeding roots one story at a time doesn't scale — after two
real-text validation rounds the lexicons still only had ~30 noun roots
and ~9 verb roots, and a second unrelated story ("Indoda engenakhaya")
only split 4/202 unique words. The fix wasn't a smarter algorithm, it
was more root vocabulary — the engine already handles the *grammar*
generically; what's missing was always vocabulary.

**Source**: [isixhosa.click](https://isixhosa.click) / its
[database repo](https://github.com/IsiXhosa-click/database)
(`words.csv`), a UCT student-led project backed by SADiLaR (South
African Centre for Digital Language Resources) and UCT Computer
Science. **Licensed CC BY-SA 4.0.** 2,336 entries total, each tagged
with `part_of_speech` and (for nouns) an explicit `noun_class` number;
verb entries store the bare root already separated from the `uku-`
infinitive marker (e.g. `bona` "see", `infinitive: ukubona`).

Several other sources were checked and rejected before landing on this
one — worth recording since they came from repeated, confident-sounding
chatbot suggestions that didn't hold up:
- `asideofcode/duramazwi` on GitHub, claimed to be "the complete
  backend repository for the famous Duramazwi Shona dictionary" — it's
  an unrelated small community web app (188 commits, 2 stars) with no
  stated data provenance. Verified directly against its README.
- VaShona.com, claimed to have "100,000+ words, downloadable" — the
  site is real, but its own footer says "All rights reserved. Do not
  distribute or reproduce," and there is no bulk export. Not usable
  even if the word count claim were true.
- The official ALLEX/Duramazwi academic dictionaries (Oosthuysen's
  publisher's institutional cousins) have no public digital access
  point at all that could be found — the University of Oslo project
  pages from the 1990s/2000s are dead (404/503), and ALRI's own page
  lists the dictionaries as completed works with no download or
  purchase information.

**Extraction method**: for each single-word noun entry, try every
prefix in `NOUN_CLASS_PREFIXES` (longest first, same as the live
engine) rather than filtering by the CSV's stated class label — the
first pass filtered by label and only matched 846/1585 nouns, because
`NOUN_CLASS_PREFIXES` doesn't duplicate every prefix under every class
it applies to (e.g. `um`/`m` are labeled class 1 only, even though
they also apply to class 3). Fixing the script to mirror the real
`_try_noun` matching order (ignore labels, just try every prefix
string) recovered nearly all of it: 1150/1585 matched, with the 4
unmatched being genuine CSV data-quality issues (swapped
english/xhosa columns). Multi-word phrases (369), proper nouns, and
hyphenated loanword entries (`i-orenji`, "orange") were excluded —
the hyphen marks a real orthographic prefix boundary the current
engine doesn't parse, and forcing it through the plain prefix-strip
logic produced malformed roots like `-abscissa` (caught by spot-
checking before merging, not left in). Verb entries: strip the final
vowel from the already-bare `xhosa` column, cross-checked against the
`infinitive` column where present. Net result: 666 new noun roots,
396 new verb roots, roughly **20x** the seed lexicon size.

**A real, non-obvious bug caught before merging**: several extracted
roots came out capitalized (`Bhulu`, `Cawe`, `Xhosa`, `Zulu`...) —
isiXhosa capitalizes proper-noun-like stems (ethnonyms, day names,
language names) even when prefixed with a lowercase class prefix
(`umBhulu`, not `umbhulu`). `_try_noun` always does
`stem.lower() in NOUN_ROOT_LEXICON` at lookup time, so a capitalized
lexicon entry would silently never match anything. Fixed by lowercasing
every extracted root before merging — a one-line fix, but the kind that
would have quietly wasted ~15 entries if the extraction hadn't been
inspected before merging rather than trusted blind.

**A more important lesson: growing the lexicon grows the collision
surface, not just the coverage.** Six real collisions surfaced
immediately after merging, found by re-running both validation stories
through the updated engine rather than assuming a pure-addition change
was safe:
- **`ubhuti`** ("brother") started splitting as `ub`+`huti` instead of
  `u`+`bhuti`, because the bulk import added `huti` as a root, and the
  `ub-` allomorph (documented as "only valid before a vowel-initial
  stem," e.g. `uboya`) was never actually *enforced* to require a vowel
  — it just happened to never have a coincidental lexicon hit for the
  wrong reading before. This was a **latent engine gap**, not just a
  data problem: fixed by adding `NOUN_PREFIXES_REQUIRE_VOWEL_STEM`
  (`ab`, `am`, `is`, `iz`, `ub`) and enforcing it explicitly in
  `_try_noun`. `uboya` (genuinely vowel-initial) still resolves
  correctly; `ubhuti` (consonant-initial) no longer wrongly matches
  the allomorph.
- **`umqhekezi`/`isiqhekezi`** (derivational nouns, "burglar"/"expert
  breaker") started wrongly resolving through verb-slot once `qhekez`
  (from the bulk-imported verb `-qhekeza`, "break in/off") became a
  seeded verb root — e.g. `u-`(you)+`m-`(him)+`qhekez-`(break)+`i` =
  "you break him." `uqhekezo` (same family, ends in `-o`, not a valid
  terminal vowel) is unaffected on its own.
- **`umthi`/`uluthi`** ("tree"/"stick") started wrongly resolving the
  same way once `th` (bare root of `-thi`, "say") was bulk-imported —
  the exact same underlying homonym (`thi` = tree/stick vs. `-thi-` =
  say) that had already caused the `uthi` exception, now recurring on
  two more words in the same root family. `imithi` (plural) and
  `uthando` (love) are unaffected.
- **`imini`** ("day") started splitting as `imi`+`ni` instead of
  `i`+`mini`, not from a vowel-gating gap but from `NOUN_ROOT_LEXICON`
  simply growing large enough that `imi` (a completely ordinary,
  unconditional class 4 prefix) now has a coincidental lexicon hit
  (`ni`, bulk-imported as "gender") beating the correct, shorter-prefix
  reading in the longest-match-first search.
- **`kubuxoki`** ("in lies/falsehood") is the one genuinely uncertain
  call — verb-slot resolves it as `ku-`+`bu-`(object)+`xok-`("lie")+`i`,
  which is plausible but likely isn't the intended locative-noun
  reading (`ku-` "in" + the whole noun `buxoki`, the same "locative on
  an already-prefixed noun" pattern lute-shona's `mumunda` exercises,
  not currently modeled here as a 3-layer strip). Included as an
  exception on the "don't guess" principle, but flagged as lower-
  confidence than the others — worth a fluent-speaker check.

All six fixed via `WORD_EXCEPTIONS` (or, for `ubhuti`, an actual engine
fix), not by reverting any part of the bulk import — the coverage win
is worth the handful of collisions it surfaced, and finding them here
means they're documented and protected rather than silently wrong in
front of a reader. **The general lesson for any future lexicon
expansion, in either language**: re-run the existing real-text
validation corpus after growing a lexicon, don't just check that
existing unit tests still pass — unit tests only cover words already
known to matter, and a bigger lexicon's new collisions show up
precisely on words that weren't being tested before.

**Two more found by the user directly**, testing a real self-written
isiXhosa paragraph (a beginner-level self-introduction) rather than
either seed story — same lesson again, a new text finds new
collisions no matter how much validation came before:
- **`molo`** ("hello", a greeting) resolved through the noun branch as
  `m` (bare cl.1/3 prefix, valid before a vowel-initial stem) + `olo`
  (a bulk-imported root) — coincidental lexicon hit, same mechanism as
  `imini`.
- **`apha`** ("here", a locative adverb) resolved through the verb
  branch as `a` (cl.5/6 subject concord — genuinely needed, see
  `adala` "s/he creates") + `ph` (bulk-imported root `-pha-`, "give")
  + terminal vowel `-a` — i.e. read as "s/he gives," a real verb form
  that happens to share a spelling with the unrelated adverb. True
  homonym, same category as `uthi`.

Both fixed via `WORD_EXCEPTIONS`; `adala` and `umntu` (the legitimate
uses of the same prefixes) confirmed still correct.

**Post-import re-validation**: both stories were re-run through the
fixed engine after all six collisions above were resolved. "Ingonyama
nenkawu" went from 7/338 to 56/338 words splitting; "Indoda
engenakhaya" (the second, previously-untested story) went from 4/202
to 34/202. No further un-investigated regressions found in the
spot-check pass. Coverage is still far from complete — most nouns and
verbs in ordinary text are still outside both lexicons — but the
order-of-magnitude jump confirms the bulk-import approach is the right
lever, not just a one-off fix.

## Known gaps, not guessed at

- **Verbal extensions** (causative/applicative/passive/reciprocal) —
  not yet located in Oosthuysen, and isixhosa.click's `words.csv` does
  not encode them either (its verb entries are bare unstacked roots).
  The general CARP ordering principle
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
- **Hyphenated loanwords** (e.g. `i-orenji`, "orange") — the hyphen is
  a real orthographic prefix boundary the engine doesn't parse; excluded
  from the bulk import rather than forced through the plain-prefix
  logic (see above). Falls back safely to whole-word.
- **The locative `e-` prefix is not modeled at all** — flagged by the
  user directly (`eKapa` "in/at Cape Town," `eMzantsi` [Afrika] "in
  [South Africa]"). Currently falls back safely to whole-word, which is
  correct-by-omission but not correct-by-design: no rule has actually
  been written. Not a quick add — isiXhosa locatives are formed several
  ways (bare `e-` + stem for some place names, `e-...-eni` circumfix
  for common nouns with consonant-strengthening at the stem boundary,
  interacting with whether the noun already carries its own class
  prefix, the same "locative on an already-prefixed noun" question
  flagged for `kubuxoki` above) and none of it is confirmed yet from
  Oosthuysen or isixhosa.click. Needs its own sourced design pass
  before writing `NOUN_CLASS_PREFIXES`-style rules — do not guess a
  single `e-` = locative rule, since place names in particular are
  exactly the class most likely to break a generic rule.
- **`NOUN_ROOT_LEXICON`/`VERB_ROOT_LEXICON` are no longer tiny** —
  695 noun roots and 405 verb roots after the isixhosa.click bulk
  import (up from ~30/~9), but still far short of full coverage for
  ordinary running text. Keep growing from real reading text and
  further verified bulk sources, not more reference-grammar mining in
  the abstract, per lute-shona DESIGN.md section 9's calibration
  finding — and re-run the real-text validation corpus (above) every
  time, since a bigger lexicon reliably surfaces new collisions.

## Forking notes for whoever builds the next one

The augment+prefix "solved by data, not code" result (above) is worth
testing again on a third language before treating it as a general
Bantu-fork pattern — one confirmation isn't a rule. The concord-table
divergence (object markers genuinely different from subject markers)
is a good reminder that "looks similar to Shona" is a hypothesis to
verify per-table, not a starting assumption — check the actual data
before assuming reuse, the same discipline used throughout both of
these projects.
