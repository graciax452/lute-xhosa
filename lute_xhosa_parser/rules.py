"""
Data tables for isiXhosa morpheme splitting.

Fork of lute-shona (see that project's DESIGN.md section 10 for the
forking methodology this followed). Unlike the initial scaffold, these
tables are now populated from a real primary source:

J.C. Oosthuysen, "The Grammar of isiXhosa" (SUN PRESS, 2016) -- a
published academic grammar (Stellenbosch University), extracted
directly from the PDF (it's a scanned-image book with no text layer,
so pages were rendered to images and read visually, page references
below are the book's own printed page numbers). Cross-checked in a
couple of places against a furman.edu isiXhosa course page (citing the
Oxford Xhosa-English dictionary) which agrees on all noun-class forms.

One source explicitly REJECTED: a pasted "Understanding Noun Classes"
lesson-page table contradicted every other source (misclassified
"isikolo" into class 5 instead of 7, listed "ocean-" as a literal
prefix, and invented classes 12/13/14 as separate "uku-" classes when
isiXhosa has no classes 12/13 at all). Discarded entirely rather than
reconciled -- see lute-xhosa DESIGN.md for why.

Architectural note that's different from Shona: isiXhosa nouns have a
two-layer prefix (augment vowel + class prefix, e.g. abantu = augment
a- + prefix ba- + root -ntu), and the augment is confirmed to drop
independently in some constructions (vocatives, certain imperatives).
Rather than adding new stripping logic for this, both the augmented
form (e.g. "aba") and the bare class-prefix-only form (e.g. "ba") are
listed as separate entries in NOUN_CLASS_PREFIXES -- the existing
lexicon-gated longest-match engine (unchanged from Shona) handles both
automatically, since it already tries every matching prefix length
tried against the same root lexicon. See morphology.py for how this
plays out; no code changes were needed, only more data.

Deferred, not guessed at (see lute-xhosa DESIGN.md for detail):
- The perfect tense suffix -ile (structurally a suffix near the
  terminal vowel, not a prefix TAM marker -- needs a real change to
  the stem resolver's terminal-vowel contract, not just new data).
- Verbal extensions (causative/applicative/passive/reciprocal) --
  not yet located in the source.
- Most persons' "a-past" tense-concord fusion forms (only class 1's
  "wa-" is confirmed so far, via "wadala").
- The reflexive link -zi- 's exact behavior (confirmed to exist,
  Oosthuysen section 10.4, p.185 -- not yet read in detail).
"""

# Proper nouns / names. Checked first, before anything else, and only
# against the ORIGINAL-cased word (must be capitalized). See lute-shona
# DESIGN.md section 7 for why this table exists (names frequently spell
# identically to ordinary words) -- not yet populated with confirmed
# isiXhosa examples.
PROPER_NOUNS = set()

# Whole-word bypasses. See lute-shona DESIGN.md section 7/9 for the
# three kinds of entries that belong here (mis-fires, confirmed-but-
# ambiguous forms, real branch collisions). Two real collisions found
# by running an actual isiXhosa story ("Ingonyama nenkawu" -- The Lion
# and the Monkey) through split_word, same discipline as lute-shona's
# mudzidzisi/mukanwa/kamba:
#   - "kudala" -- verb-slot wrongly resolves it as ku- (cl.15/17
#     subject concord) + dal- (root "create") + -a, "it creates",
#     because "dal" is a seeded verb root. In the story it's the fixed
#     temporal adverb "long ago"/"for a long time" ("Kudala ndilapha
#     okoko kwakusasa" -- "I've been here a long time, since this
#     morning"), unrelated to the verb.
#   - "uthi" -- the noun branch wrongly resolves it as u- (augment,
#     cl.1a/11) + thi (seeded noun root "tree/stick"), "a stick". In
#     the story it's the verb "you say" (u- + -thi- "say", e.g.
#     "Dibanisa iintupha zakho uthi, '...'" -- "Join your thumbs and
#     say, '...'"). A true homonym -- "thi" isn't even seeded as a verb
#     root, so only the wrong noun reading could ever fire; same
#     category as lute-shona's "kamba" (tortoise vs. small house).
WORD_EXCEPTIONS = {
    "kudala",
    "uthi",
}

# Confirmed past-tense ("a-past") subject-concord fusions, matched the
# same way as VERB_SUBJECT_PREFIXES. Oosthuysen p.201 (12.8, "The
# a-past tense indicative"): distinguished by a long vowel -a-, e.g.
# wadala ("he/she created") = class 1 concord u- + a-past -a-,
# coalescing to wa-. Only class 1's form is confirmed so far -- other
# persons' a-past fusions (parallel to Shona's nda-/ta-/ma- family) are
# NOT yet confirmed and must not be guessed; add them here once found.
PAST_SUBJECT_PREFIXES = {
    "wa": "cl.1 a-past (confirmed via 'wadala' = wa+dala, Oosthuysen p.201)",
}

# Noun class prefixes: (prefix, class_id) tuples. Both the augmented
# form (augment vowel + class prefix, e.g. "aba") and the bare
# class-prefix-only form (augment dropped, e.g. "ba") are listed
# separately -- see module docstring for why this is safe without any
# engine change. Source: Oosthuysen ch.2 (pp.24-43, table of contents
# gives the exact per-class prefix shorthand), cross-checked against
# furman.edu/Oxford dictionary examples. Locative classes 16/17/18
# (pha-/ku-/mu-, Oosthuysen 2.15 p.43) have no augment at all.
#
# Known ambiguities carried by this table (documented, not "fixed" --
# same category as Shona's mu-/ku- overlaps):
# - "um"/"m" (cl.1 AND cl.3) -- same surface form, different class,
#   doesn't affect splitting, only the semantic label.
# - "ku" (cl.15 infinitive/noun AND cl.17 locative) -- resolved the
#   same way as Shona's ku-: infinitive checked first with a
#   verb-root-lexicon gate, everything else falls through to this
#   noun-prefix table.
NOUN_CLASS_PREFIXES = [
    ("um", "1"),       # augmented, e.g. umntu
    ("m", "1"),         # augment-dropped variant
    ("u", "1a"),        # cl.1a has no separate class prefix, augment only
    ("aba", "2"),       # augmented, e.g. abantu
    ("ab", "2"),        # augmented before vowel-initial stem
    ("ba", "2"),        # augment-dropped variant
    ("oo", "2a"),       # fused augment+prefix, e.g. oobhuti
    ("imi", "4"),       # augmented, e.g. imivubu
    ("mi", "4"),        # augment-dropped variant
    ("ili", "5"),       # augmented, e.g. ilifu
    ("i", "5"),         # alt augment-only form (some cl.5 nouns), also cl.9 -- see below
    ("li", "5"),        # augment-dropped variant
    ("ama", "6"),       # augmented, e.g. amafu
    ("am", "6"),        # augmented before vowel-initial stem
    ("ma", "6"),        # augment-dropped variant
    ("isi", "7"),       # augmented, e.g. isikolo
    ("is", "7"),        # augmented before vowel-initial stem
    ("si", "7"),        # augment-dropped variant
    ("izi", "8"),       # augmented, e.g. izidenge
    ("iz", "8"),        # augmented before vowel-initial stem
    ("zi", "8"),        # augment-dropped variant
    # class 9: augment "i-" only -- the nasal class-prefix component
    # fuses directly into the stem's initial consonant (N-+ngwe stays
    # "ngwe"), so there's no separate bare-consonant-prefix layer to
    # add, unlike the other classes. Same "i" entry as cl.5's alt form
    # above -- ambiguous, doesn't affect splitting.
    ("ii", "10"),       # augmented plural, e.g. iintombi
    ("izi", "10"),      # alt augmented plural form (duplicate string of cl.8 -- fine, same reasoning)
    ("ulu", "11"),      # augmented, e.g. uluthi
    ("u", "11"),        # alt augment-only form (some cl.11 nouns), also cl.1a/15 -- ambiguous, doesn't affect splitting
    ("lu", "11"),       # augment-dropped variant
    ("ubu", "14"),      # augmented, e.g. ubuntu
    ("ub", "14"),       # augmented before vowel-initial stem
    ("bu", "14"),       # augment-dropped variant
    ("uku", "15"),      # augmented, e.g. ukufa (also see _try_infinitive -- checked first)
    ("ku", "15"),       # augment-dropped variant, also cl.17 locative (see ambiguity note above)
    ("pha", "16"),      # locative, no augment
    ("mu", "18"),       # locative, no augment
]

# Noun roots, gated the same way as lute-shona's: the full remainder
# after a candidate prefix strip must exactly match an entry here.
# Source: Oosthuysen's example nouns (ch.2) and the furman.edu/Oxford
# derivational examples (-qhekeza and -phula forming different nouns
# across classes 1/3/7/11/14 -- direct isiXhosa parallel to Shona's
# cross-class shared roots like "kadzi"/"nhu"). Consonant-mutated
# derivational forms (e.g. class 9 "inkqekezo" from -qhekeza, where the
# root surfaces as "nkqekez-" not "qhekez-") are deliberately NOT
# seeded -- same unmodeled-mutation category as Shona's class 5, see
# DESIGN.md.
NOUN_ROOT_LEXICON = {
    "ntu",       # umntu, abantu, ubuntu (humanity) -- cross-class shared root
    "hlobo",     # umhlobo (friend, cl.1/3), uhlobo (type, cl.11) -- cross-class polysemy
    "bhuti",     # ubhuti, oobhuti (brother)
    "tata",      # utata, ootata (father)
    "vubu",      # umvubu, imivubu (hippo)
    "buzo",      # umbuzo (question)
    "pu",        # umpu, imipu (gun)
    "thi",       # umthi, imithi (tree)
    "fu",        # ilifu, amafu (cloud)
    "kolo",      # isikolo, izikolo (school)
    "denge",     # isidenge, izidenge (fool)
    "ngwe",      # ingwe, izingwe/iingwe (leopard)
    "ti",        # iti (tea)
    "ntombi",    # intombi, iintombi (girl)
    "ndlela",    # indlela (path, road, way)
    "thando",    # uthando (love, from ukuthanda)
    "luthi",     # uluthi (stick)
    "qhekezi",   # umqhekezi (burglar, cl.1), from root -qhekeza (break in/off)
    "qhekezo",   # umqhekezo (event of breaking off, cl.3), uqhekezo (cl.11)
    "phuli",     # umphuli (person who breaks things, cl.1), from root -phula
    "phulo",     # umphulo (event of breaking, cl.3), uphulo (cl.11)
    "buphuli",   # ubuphuli (state of breaking, cl.14)
    "hle",       # ubuhle (beauty)
    "si",        # ubusi (honey) -- NOTE short root, collision-prone, see DESIGN.md
    "suku",      # ubusuku (night)
}

# Closed set of word-initial verbal subject concords. Source:
# Oosthuysen 10.2 (p.175), the full person+class table -- see
# lute-xhosa DESIGN.md for the complete table as extracted. Several
# entries share a surface form across person and class (e.g. "u" is
# 2sg AND cl.1/cl.3-4 concord, "si" is 1pl AND cl.7-8 concord) --
# same category of syncretism already documented for Shona, doesn't
# affect splitting since the lexicon gate still has to confirm the
# stem.
VERB_SUBJECT_PREFIXES = {
    "ndi": "1sg",
    "u": "2sg / 3sg (cl.1) / cl.3,4 concord",
    "si": "1pl / cl.7,8 concord",
    "ni": "2pl",
    "ba": "3pl (cl.2) concord",
    "a": "cl.5,6 concord (also alt cl.1 concord in subjunctive/relative moods, Oosthuysen p.176)",
    "li": "cl.5 concord",
    "i": "cl.9,10 concord (also cl.3,4 plural)",
    "zi": "cl.8,10 concord (plural)",
    "lu": "cl.11 concord",
    "bu": "cl.14 concord",
    "ku": "cl.15,17 concord",
}

# TAM (tense/aspect/mood) markers. isiXhosa's tense system is
# genuinely more complex than Shona's simple prefix-TAM slot (see
# module docstring) -- only the imperfect/present -ya- infix is
# confirmed and modeled so far (Oosthuysen 11.3, p.189, e.g.
# "ndiyasebenza" = ndi+ya+sebenza). Perfect tense (-ile suffix) and
# future (periphrastic, "ukuza" + infinitive) are NOT modeled here --
# see DESIGN.md for why each needs different handling than a simple
# TAM_MARKERS entry.
TAM_MARKERS = {
    "ya": "present/imperfect (progressive)",
}

# Object markers, infixed immediately before the root. Source:
# Oosthuysen 10.3 (p.183), the full person+class table. Genuinely
# different strings from VERB_SUBJECT_PREFIXES in several places
# (unlike Shona, where subject/object often literally share forms) --
# e.g. 2sg subject is "u-" but 2sg object is "-ku-"; cl.1 subject is
# "u-"/"a-" but cl.1 object is the syllabic "-m-".
#
# "ku" here means BOTH 2sg object AND cl.15/17 object -- combined with
# "ku" already being cl.15/17 *subject* concord and the cl.15/17 noun
# prefix, this is a four-way overload on one string, more collision-
# prone than anything in Shona. Flagged, not specially handled beyond
# the existing lexicon gate.
OBJECT_MARKERS = {
    "ndi": "me",
    "ku": "you (sg) / cl.15,17",
    "m": "him/her (cl.1) -- short root, watch for collisions, same category as Shona's 1-letter 'd'",
    "si": "us / cl.7 sg",
    "ni": "you (pl)",
    "ba": "them (cl.2)",
    "wu": "cl.3,4 sg object",
    "yi": "cl.3,4 pl object / cl.9,10 sg object",
    "li": "cl.5 sg object",
    "wa": "cl.6 pl object",
    "zi": "cl.7,8,9,10 pl object / possibly also the reflexive link -zi- (Oosthuysen 10.4, p.185 -- not yet read in detail, treat as ambiguous)",
    "lu": "cl.11 object",
    "bu": "cl.14 object",
}

# Derivational verb extensions. NOT YET CONFIRMED for isiXhosa -- left
# empty rather than assuming Shona's forms transfer (the general CARP
# ordering principle likely holds, being a Nguni/Bantu-wide pattern,
# but the exact surface forms need their own isiXhosa-specific source
# before going in a rules table). See DESIGN.md.
VERB_EXTENSIONS = {}

# Seed verb roots, stored WITHOUT the final vowel (_resolve_stem strips
# the terminal vowel before checking against this set -- same
# convention as lute-shona's VERB_ROOT_LEXICON). Only the clearly-
# attested, unambiguous ones from Oosthuysen's example sentences --
# deliberately conservative, since several example forms involve tense
# suffixes/vowel coalescence not yet fully mapped (e.g. "awayeyiphethe"
# might be phath-+-ile with a coalescence, not a clean "phethe" root --
# excluded rather than guessed).
VERB_ROOT_LEXICON = {
    "hamb",    # ukuhamba - walk/go (bayahamba, bahambile)
    "fund",    # ukufunda - learn/study (ndifundile)
    "f",       # ukufa - die -- 1-letter root, same collision-risk category as Shona's "d"
    "ty",      # ukutya - eat
    "sebenz",  # ukusebenza - work (ndiyasebenza)
    "bon",     # ukubona - see (asikaziboni)
    "dal",     # ukudala - create (wadala)
    "theng",   # ukuthenga - buy (bathengile)
}

# Terminal vowels. Never emitted as their own token -- see lute-shona
# DESIGN.md section 5 for the reasoning (a lone Latin letter is
# low-value/noisy as a standalone token), confirmed to apply here too.
TERMINAL_VOWELS = {"a", "e", "i"}
