"""
Data tables for isiXhosa morpheme splitting.

This is a fork of lute-shona (https://github.com/<user>/lute-shona),
following the forking guidance written in that project's DESIGN.md
(section 10) before this fork existed: copy the package, replace
rules.py entirely, keep morphology.py/parser.py as a starting
hypothesis rather than assumed-correct, and only extract a shared
BantuParser base class after this second language is actually working
-- not before.

Every table here is plain data (no matching logic -- see morphology.py
for that). All tables are currently EMPTY placeholders, mirroring the
Shona version's table names/shapes so morphology.py's imports resolve,
but carrying no isiXhosa data yet -- until real entries are added,
split_word() will safely leave every word whole (the same safe-fallback
behavior lute-shona relies on everywhere). Fill these in from real
isiXhosa reference material (noun classes, verb morphology, confirmed
grammar from a fluent speaker) the same way lute-shona's were built --
see that project's DESIGN.md for the full methodology and the specific
mistakes it made and corrected along the way (worth reading before
building this one, not just copying the code).

Not carried over from Shona: NEGATIVE_HAVE_PREFIX/SUFFIX and
SATI_SUFFIX (Shona's "ha-...-na" negative-existential and
"[subject]+sati" constructions) and their matching functions in
morphology.py. Those are specific confirmed Shona idioms, not assumed
to have an isiXhosa equivalent -- if isiXhosa turns out to have
analogous closed constructions, add them the same deliberate way
Shona's were added (confirm productivity and fixed boundaries first,
see lute-shona DESIGN.md section 7), don't assume the same surface
forms apply.
"""

# Proper nouns / names. Checked first, before anything else, and only
# against the ORIGINAL-cased word (must be capitalized). See
# lute-shona DESIGN.md section 7 for why this table exists at all
# (names are frequently spelled identically to ordinary words) --
# expect the same to be true in isiXhosa.
PROPER_NOUNS = set()

# Whole-word bypasses, checked before any splitting is attempted. See
# lute-shona DESIGN.md section 7 for the three kinds of entries that
# belong here (mis-fires, confirmed-but-ambiguous forms, real branch
# collisions) and section 9 for the true-homonym case found there.
WORD_EXCEPTIONS = set()

# Confirmed past-tense (or other tense-marked) subject concord forms
# that differ from the basic subject concord, if isiXhosa turns out to
# have an equivalent to Shona's nda-/wa-/ta-/ma- paradigm. Matched the
# same way as VERB_SUBJECT_PREFIXES.
PAST_SUBJECT_PREFIXES = {}

# Noun class prefixes: list of (prefix, class_id) tuples. isiXhosa has
# its own noun class system (related to but distinct from Shona's --
# different class inventory, different phonology, e.g. click
# consonants that Shona doesn't have). Do not assume Shona's prefixes
# transfer; build this from isiXhosa-specific reference material.
NOUN_CLASS_PREFIXES = []

# Noun roots, gated the same way as lute-shona's: a candidate prefix is
# only stripped if the remaining stem exactly matches an entry here.
# See lute-shona DESIGN.md section 3 for why this lexicon-gating
# matters (overstemming prevention) -- same principle applies here.
NOUN_ROOT_LEXICON = set()

# Closed set of word-initial verbal markers (subject concords). Build
# from isiXhosa-specific personal-pronoun/concord reference material,
# not assumed from Shona.
VERB_SUBJECT_PREFIXES = {}

# TAM (tense/aspect/mood) markers, infixed between subject prefix and
# object marker/root.
TAM_MARKERS = {}

# Object markers, infixed immediately before the root.
OBJECT_MARKERS = {}

# Derivational verb extensions (applicative, causative, passive,
# reciprocal, stative, ...), attach between root and terminal vowel.
# isiXhosa verb extensions are cognate with Shona's but not assumed
# identical in form -- confirm from real material.
VERB_EXTENSIONS = {}

# Verb roots, gated the same way as NOUN_ROOT_LEXICON.
VERB_ROOT_LEXICON = set()

# Terminal vowels. Never emitted as their own token -- see lute-shona
# DESIGN.md section 5 for why (a lone Latin letter is low-value/noisy
# as a standalone token) and the design back-and-forth that confirmed
# this. isiXhosa's terminal vowel system is likely similar (a/e/i,
# Bantu-typical) but confirm rather than assume.
TERMINAL_VOWELS = set()
