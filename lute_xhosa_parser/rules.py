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
# Two more found immediately after the isixhosa.click bulk import (see
# DESIGN.md): "umqhekezi" ("burglar", cl.1) and "isiqhekezi" ("expert
# breaker", cl.7) both end in the valid terminal vowel -i, and the bulk
# import happened to add "qhekez" as a verb root (from the bulk-imported
# verb "-qhekeza", "break in/off") -- so verb-slot now wrongly resolves
# them as subject+object+"qhekez"(root)+i, e.g. u-(you)+m-(him)+qhekez-
# (break)+i = "you break him", instead of the correct noun reading.
# Note "uqhekezo" (cl.11, same derivational family) does NOT need an
# exception -- it ends in -o, not a valid terminal vowel, so verb-slot
# already fails safely on its own.
# The bulk import also added "th" (bare root of "-thi", "say") as a
# verb root -- systemically colliding with the same "thi" (tree/stick)
# noun root that already caused the "uthi" exception above, now also
# breaking "umthi" ("tree": u-+m-(object)+th-+i = "you say it") and
# "uluthi" ("stick": u-+lu-(object)+th-+i = "you [cl.11 obj] say").
# "imithi" (trees, plural) and "uthando" (love) are unaffected --
# neither produces a subject+object+"th"+valid-TV combination.
#
# "imini" ("day") is a different flavor of the same underlying issue:
# not a vowel-gating gap, just the noun branch's longest-match-first
# search finding "imi" (a perfectly legitimate, unconditional class 4
# prefix) before the shorter "i", and "imi"+"ni" ("ni" bulk-imported as
# "gender") happens to also be a valid lexicon hit -- so it wins over
# the correct "i"+"mini" reading purely by being checked first. Found
# running "Ingonyama nenkawu" through the updated engine.
#
# "kubuxoki" ("in lies/falsehood", from "ungakholelwa kubuxoki" -- "you
# shouldn't believe in lies") is a genuine judgment call, not a
# confirmed error: verb-slot resolves it as ku-(subject)+bu-(cl.14
# object)+xok-(root "lie", bulk-imported)+i, which is plausible on its
# own terms but likely isn't the intended locative-noun reading (ku-
# "in" + the whole noun "buxoki", parallel to lute-shona's "whole noun
# as stem" locative pattern -- not currently modeled here, would need
# a 3-layer locative+class-prefix+root strip). Included as an exception
# because the alternative (a specific verb-shaped guess) risks being
# actively wrong, but flagged here as lower-confidence than the others
# -- worth a fluent-speaker check.
#
# "molo" (a greeting, "hello") wrongly resolved through the noun
# branch as "m" (bare class 1/3 prefix, valid before a vowel-initial
# stem) + "olo" (a bulk-imported root) -- a coincidental lexicon hit,
# same category as "imini". Found by the user directly, testing real
# isiXhosa sentences.
#
# "apha" ("here", a locative adverb) wrongly resolved through the verb
# branch as "a" (cl.5/6 subject concord, e.g. "adala" = "s/he
# creates") + "ph" (bulk-imported root, "-pha-" "give") + terminal
# vowel "-a" -- i.e. read as "s/he gives", a real verb form that
# happens to share a spelling with the unrelated adverb. True
# homonym, same category as "uthi". Found by the user directly.
#
# Seven more collisions found running the two validation stories again
# after the Kaikki-Xhosa bulk import (see the "third bulk source"
# comment on NOUN_ROOT_LEXICON) -- same category as "molo"/"apha"
# above, each a common/basic word wrongly resolved through the verb
# branch once the much larger new vocabulary gave it a coincidental
# match:
# - "imithi" ("trees", imi+thi) -- NOT i(cl.9/10 concord)+mith(from
#   "-mitha-", "to be pregnant")+i.
# - "umsila"/"msila"/"kumsila" ("tail") -- NOT u/ku(subject)+m(object,
#   him/her)+sil(from "-sila-", "to brew/grind")+a.
# - "umhlaba" ("earth/world") -- NOT u(subject)+m(object)+hlab(from
#   "-hlaba-", "to stab") -- this one predates the Kaikki-Xhosa round
#   ("hlab" was already seeded from isixhosa.click) but was only found
#   now, testing a real story that happens to use the word.
# - "umzingeli" ("hunter", an agentive noun) -- NOT u(subject)+
#   m(object)+zingel(from "-zingela-", "to hunt")+i. Unlike lute-shona's
#   "mufundisi" (which turned out to be a genuinely correct
#   compositional agentive reading), the verb-branch token boundary
#   here (u|m|zingeli, 3 tokens) doesn't match what the correct
#   noun-branch boundary would be (um|zingeli, 2 tokens) -- these are
#   different splits, not two labels for the same one, so this is a
#   real collision, not a coincidentally-correct alternate parse.
# - "ndiyazi" ("I know [it]") -- NOT ndi+ya(present)+z(from "-za-",
#   "to come")+i. The real root is "-azi-" ("to know"), but its
#   initial vowel elides after the "-ya-" present marker (ya+azi ->
#   yazi) -- an unmodeled vowel-coalescence process (same category as
#   lute-shona's chi-/zvi- + vowel-initial-stem gap), which is what
#   leaves "zi" exposed to a coincidental match against an unrelated
#   short root instead.
# - "amabi" ("bad things", ama-+bi) -- NOT a(cl.5/6 concord)+
#   m(object)+ab(from "-aba-", "to share/distribute")+i.
# - "ibambe" ("it holds"/similar, from "-bamba-", "to hold/catch") --
#   resolves via the verb branch either way, but the *search order*
#   picks the wrong resolution: trying object marker "ba" first
#   leaves "mbe", which also happens to hit a real (different) root
#   ("-mba-", "to dig"), so "i-ba-mbe" wins over the correct
#   "i-bambe" (no object, root "bamb") purely because optional-object
#   candidates are tried before the no-object case. This is a
#   different *kind* of risk than the others -- not a stray
#   coincidental root, but two *both-valid* resolutions where the
#   search order favors the shallower, wrong one. Worth remembering as
#   its own risk category if more instances turn up: a longer lexicon
#   makes it more likely that consuming an optional slot (object
#   marker, TAM) *also* accidentally resolves, not just that skipping
#   it does.
# Three more from the same root family, once "umrhwebi" ("trader",
# singular) confirmed the pattern: "abarhwebi" ("traders", plural) and
# "kubarhwebi" ("to/among the traders", locative on the whole class-2
# noun with the augment elided) both resolve the same wrong way --
# subject/concord + object "ba"(them) + rhweb(from "-rhweba-", "to
# barter/trade") + i, instead of the correct aba-/ku-+aba- + "rhwebi"
# noun reading. Originally "kubarhwebi" was left alone as a lower-
# confidence guess (no sibling to compare against), but with
# "umrhwebi"/"abarhwebi" both confirmed wrong via the identical
# mechanism, the same fix clearly applies here too.
WORD_EXCEPTIONS = {
    "kudala",
    "uthi",
    "umqhekezi",
    "isiqhekezi",
    "umthi",
    "uluthi",
    "imini",
    "kubuxoki",
    "molo",
    "apha",
    "imithi",
    "umsila",
    "msila",
    "kumsila",
    "umhlaba",
    "umzingeli",
    "ndiyazi",
    "amabi",
    "ibambe",
    "umrhwebi",
    "abarhwebi",
    "kubarhwebi",
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
    ("ab", "2"),        # augmented before vowel-initial stem -- see NOUN_PREFIXES_REQUIRE_VOWEL_STEM below
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

# The "before vowel-initial stem" allomorphs above (ab-, am-, is-, iz-,
# ub-) are only real prefixes when the stem itself starts with a vowel
# -- morphology.py enforces this explicitly for these five, since
# without it a word like "ubhuti" ("brother") can wrongly match "ub-"
# (leaving stem "huti", a real root once bulk vocabulary was added)
# instead of "u-" (leaving stem "bhuti", the correct root) purely
# because "ub-" is longer and the longest-match-first search tries it
# first. Found via a real regression after the isixhosa.click bulk
# import (see DESIGN.md) -- harmless when the lexicon was small, since
# there was rarely a lexicon hit for the wrong reading to false-fire
# on, but a real risk once the lexicon got big enough for coincidental
# hits to become likely.
NOUN_PREFIXES_REQUIRE_VOWEL_STEM = {"ab", "am", "is", "iz", "ub"}
VOWELS = set("aeiou")

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
    # From "Indoda engenakhaya" (The Homeless Man) -- second real-text
    # validation story. Extracted by applying the already-confirmed
    # noun-class prefix inventory (not new grammar), so lower-risk than
    # the grammar-rule "don't guess" cases -- but still just one
    # non-fluent pass, worth a fluent-speaker check eventually.
    "ndoda",     # indoda (man/husband, cl.9)
    "ngxowa",    # ingxowa (bag/sack, cl.9)
    "rhwebi",    # umrhwebi (trader/merchant, cl.1) -- agentive "-i" pattern, same as qhekezi/phuli
    "ngqekembe", # ingqekembe, iingqekembe (gold coin/coins, cl.9/10)

    # --- Bulk import from isixhosa.click (words.csv), CC BY-SA 4.0 ---
    # https://github.com/IsiXhosa-click/database -- a UCT/SADiLaR-backed
    # open dictionary project, 2336 entries total. Extracted by matching
    # each entry's stated noun_class against the confirmed
    # NOUN_CLASS_PREFIXES table above and stripping the prefix -- same
    # low-risk extraction method used for the earlier hand-picked
    # entries, just automated at scale. Multi-word phrases, proper
    # nouns, and hyphenated loanwords (e.g. i-orenji) were excluded (see
    # lute-xhosa DESIGN.md). This is machine-extracted, not individually
    # hand-verified line by line the way the Oosthuysen-sourced entries
    # above are -- worth a fluent-speaker spot-check eventually. Some
    # entries are short (2-3 letters) and therefore more collision-prone
    # -- same category as the hand-picked short roots elsewhere in this
    # file, protected the same way (exact-remainder-match gating).
    "abonakude",  # television
    "ahluko",  # difference
    "akazi",  # maternal aunt
    "akhelo",  # matrix
    "akhiwo",  # building
    "alume",  # maternal uncle
    "ama",  # mother
    "ambo",  # rib
    "andi",  # sound
    "andla",  # hand
    "andlalo",  # bed
    "ango",  # entrance
    "angqa",  # circle
    "anyano",  # union
    "avereji",  # mean
    "awo",  # father
    "aziso",  # identity
    "bakala",  # grade
    "bala",  # colour
    "bali",  # story
    "bane",  # electricity
    "banga",  # grade
    "banjwa",  # prisoner
    "befu",  # asthma
    "bele",  # breast
    "beleko",  # vagina
    "bethe",  # dew
    "bhabhatane",  # butterfly
    "bhali",  # writer
    "bhanxa",  # fool
    "bhasi",  # buses
    "bhaxu",  # patch
    "bhayisekile",  # bicycles
    "bhedi",  # bed
    "bhedlele",  # hospital
    "bhegi",  # bag
    "bhengezo",  # advertisement
    "bheno",  # appeal
    "bhere",  # bear
    "bheyile",  # bail
    "bhodi",  # boards
    "bhola",  # balls
    "bhontsi",  # big toes
    "bhotile",  # bottle
    "bhulu",  # Afrikaans
    "bhuthi",  # brothers
    "bilo",  # sweat
    "bindi",  # centre
    "bini",  # second
    "bono",  # idea
    "bumbelo",  # matrix
    "bunzi",  # forehead
    "cala",  # section
    "candelo",  # department
    "cango",  # door
    "caphaza",  # dot
    "catshulwa",  # extract
    "cawe",  # churches
    "cephe",  # spoon
    "chako",  # material
    "chaneka",  # accuracy
    "chapaza",  # dots
    "chaphaza",  # spot
    "chaphuchaphu",  # nausea
    "chiza",  # chemical
    "cici",  # earring
    "cikicane",  # baby toe
    "ciko",  # lid
    "cingo",  # wire
    "copho",  # brain
    "culo",  # music
    "dabi",  # battle
    "dadebawo",  # paternal aunt
    "daka",  # mud
    "dakada",  # spleen
    "dali",  # darling
    "dalwa",  # creature
    "dibaniso",  # addition
    "didi",  # class
    "dla",  # interest
    "dladla",  # home
    "dlala",  # gland
    "dlali",  # actor
    "dlalo",  # game
    "dlele",  # cheek
    "dlelwane",  # friendship
    "dliwo",  # fine
    "dlo",  # meal
    "doda",  # men
    "dolo",  # knee
    "dolophu",  # town
    "donga",  # wall
    "dudu",  # porridge
    "dumbu",  # corpse
    "dyasi",  # condom
    "dywantsi",  # hip
    "ebe",  # branch
    "efundisi",  # pastors
    "ehlandenyuka",  # ups and downs
    "ehlo",  # eyes
    "emere",  # bucket
    "endu",  # speed
    "enzi",  # verb
    "eti",  # set
    "eva",  # thorns
    "eyilotayiphi",  # sellotape
    "eyitroni",  # matron
    "fama",  # farmer
    "fanekiso",  # picture
    "fazi",  # wife
    "fektha",  # factor
    "fele",  # skin
    "festile",  # windows
    "fiva",  # fever
    "flu",  # flu
    "fo",  # guy
    "folokhwe",  # forks
    "formula",  # formulae
    "fuba",  # chest
    "fudo",  # tortoise
    "fundi",  # student
    "fundisi",  # pastor
    "funo",  # vegetable
    "futha",  # oil
    "futhe",  # effect
    "fuzo",  # genetics
    "gaba",  # phase
    "gadi",  # garden
    "galelo",  # contribution
    "gama",  # area
    "ganeko",  # incident
    "gangatho",  # floor
    "garaji",  # garages
    "gathara",  # gutters
    "gazi",  # blood
    "gca",  # line
    "gcisa",  # art
    "gebenga",  # crime
    "gesi",  # x-rays
    "gidi",  # million
    "godi",  # mine
    "goli",  # Johannesburg
    "gongqongqo",  # dragon
    "gonyo",  # vaccine
    "gophe",  # curve
    "gqabi",  # leaf
    "gqala",  # veteran
    "gqi",  # witchcraft
    "gqibelo",  # Saturday
    "gqili",  # Orange River
    "gqirha",  # doctor
    "gqomo",  # bin
    "gqwirha",  # witchcraft
    "gruzuko",  # bruise
    "gubo",  # flour
    "gulana",  # patient
    "gulo",  # illness
    "gumbi",  # room
    "gusha",  # sheep
    "gxa",  # shoulder
    "gxalaba",  # shoulder
    "hambo",  # journey or trip
    "hashe",  # car
    "hayihayi",  # high blood pressure
    "heke",  # gates
    "helikhopta",  # helicopters
    "hempe",  # shirt
    "hiya",  # eyebrow
    "hla",  # date
    "hlaba",  # earth
    "hlabathi",  # world
    "hlahla",  # wrist
    "hlana",  # back
    "hlangu",  # shoe
    "hlathi",  # forest
    "hlawuliso",  # fine
    "hlaza",  # cancer
    "hlekazi",  # mister
    "hlengisi",  # dolphin
    "hleza",  # hip bone
    "hlungu",  # pain
    "hlunu",  # muscle
    "hlwele",  # crowd
    "hlwempu",  # poverty
    "hombiso",  # decoration
    "hontsi",  # big toe
    "huti",  # brother
    "isi",  # milk
    "joni",  # soldier
    "kama",  # combs
    "kamva",  # future
    "kapa",  # Cape Town
    "kati",  # cats
    "kere",  # pair of scissors
    "khabathi",  # cupboards
    "khadi",  # card
    "khadibhodi",  # cardboard
    "khalazo",  # complaint
    "khaya",  # home
    "khefu",  # interval
    "khenkce",  # ice
    "khephe",  # ship
    "khephu",  # snow
    "khethe",  # prejudice
    "khetshi",  # cable car
    "khitshana",  # boat
    "khohlela",  # phlegm
    "khohlokhohlo",  # cough
    "khompyutha",  # computers
    "khondo",  # trunk
    "khonkco",  # link
    "khova",  # owl
    "khuhlane",  # cold
    "khula",  # weeds
    "khulu",  # hundred
    "khuluwa",  # elder brother
    "khumba",  # skin
    "khumbi",  # dock
    "khuni",  # pee stick
    "khwele",  # envy
    "khweli",  # passenger
    "khwenkwe",  # boys
    "klasi",  # classes
    "ko",  # fireplace
    "kofu",  # coffee
    "komityi",  # cups
    "krebe",  # shark
    "krelemnqa",  # perpetrator
    "kwindla",  # autumn
    "lambo",  # river
    "langa",  # sun
    "layi",  # slice
    "lebe",  # lip
    "lenge",  # crane
    "lenze",  # leg
    "levu",  # chin
    "lilo",  # fire
    "limi",  # farmer
    "linganiso",  # measure
    "lingo",  # magic
    "lingwa",  # subject
    "lo",  # beast
    "logaridhimu",  # Logarithm
    "lokhwe",  # dresses
    "loliwe",  # train
    "lomo",  # mouth
    "lovane",  # chameleon
    "loyiko",  # fear
    "lungelelanisi",  # coordinate
    "lungiselelo",  # preparations
    "lungu",  # member
    "lwalamano",  # Proportion
    "lwandle",  # beach
    "lwanyana",  # animal
    "lwesibini",  # Tuesday
    "lwesihlanu",  # Friday
    "lwesine",  # Thursday
    "lwesithathu",  # Wednesday
    "lwimi",  # languages
    "makazi",  # maternal aunts
    "mali",  # money
    "malume",  # maternal uncles
    "mama",  # mothers
    "mandla",  # regions
    "mangalelwa",  # accused
    "mangali",  # plaintiff
    "mbalela",  # drought
    "mbali",  # history
    "mbambo",  # ribs
    "mbangi",  # causes
    "mbewu",  # seeds
    "mbila",  # dassies
    "mbotyi",  # beans
    "mbuso",  # faces
    "meko",  # situations
    "mela",  # knives
    "melabizo",  # pronoun
    "meli",  # representatives
    "memo",  # invitation
    "menemene",  # deceit
    "meyitroni",  # matrons
    "mfazwe",  # war
    "mfene",  # Baboons
    "mfeyesele",  # moss
    "mfihlo",  # secret
    "mfudo",  # tortoises
    "mfundo",  # education
    "milo",  # character
    "mini",  # days
    "miselo",  # terms
    "mntwiso",  # personification
    "mo",  # condition
    "mongikazi",  # nurses
    "moto",  # cars
    "mpahla",  # clothes
    "mpawu",  # symptoms
    "mpazamo",  # mistakes
    "mpelaveki",  # weekends
    "mpendulo",  # answers
    "mpikiswano",  # contradiction
    "mpilo",  # health
    "mpindo",  # river bends
    "mpondo",  # horns
    "mpuku",  # mice
    "mpumlo",  # noses
    "mpundu",  # buttocks
    "mvavanyo",  # exams
    "mviwo",  # exams
    "mvo",  # opinions
    "mvubu",  # hippos
    "mvula",  # rain
    "mvume",  # permission
    "nakwethu",  # brother
    "naliti",  # needles
    "nambuzane",  # bug
    "ncam",  # point
    "ncasa",  # flavour
    "ncedo",  # help
    "ncili",  # excitement
    "ncoko",  # conversation
    "ncopho",  # peak
    "ncwadi",  # books
    "ndaba",  # news
    "ndalo",  # nature
    "ndawo",  # places
    "ndebe",  # trophy
    "ndidi",  # types
    "ndilili",  # average
    "ndima",  # role
    "ndindisholo",  # numbness
    "ndla",  # energy
    "ndlala",  # famine
    "ndlebe",  # ears
    "ndleko",  # expenses
    "ndlovu",  # elephants
    "ndlu",  # houses
    "ndlulamthi",  # giraffes
    "ndonga",  # walls
    "nenekazi",  # lady
    "ngalingani",  # inequality
    "ngalo",  # arms
    "ngca",  # grass
    "ngcali",  # experts
    "ngcangcazelomhlaba",  # shock wave
    "ngcango",  # doors
    "ngcingo",  # wires
    "ngesi",  # English
    "ngingqi",  # area
    "ngoma",  # song
    "ngomeleli",  # weakness
    "ngono",  # nipples
    "ngqele",  # cold
    "ngqina",  # evidence
    "ngqiniba",  # elbows
    "ngqondo",  # brain
    "ngqusho",  # samp
    "ngqwalaselo",  # Observations
    "ngubo",  # blanket
    "ngwenya",  # crocodile
    "ngxaki",  # problems
    "ngxangxasi",  # waterfalls
    "ngxelo",  # reports
    "ngxinano",  # traffic
    "ngxolo",  # noise
    "ngxuma",  # hole
    "ngxunguphalo",  # suffering
    "ngxungxo",  # part-time job
    "ni",  # gender
    "ninawa",  # younger brother
    "ninzi",  # plural
    "nja",  # dogs
    "njeke",  # pancreases
    "njikalanga",  # evening
    "njongosenzi",  # object
    "nkaba",  # navels
    "nkathazo",  # problem
    "nkcubeko",  # culture
    "nkcukacha",  # detail
    "nkolo",  # religion
    "nkomo",  # cows
    "nkonxa",  # tin can
    "nkonyana",  # calves
    "nkonzo",  # services
    "nkosazana",  # princess
    "nkosi",  # chief
    "nkqubo",  # procedures
    "nkuku",  # chickens
    "nkulungwane",  # centuries
    "nkumba",  # snails
    "nkumbulo",  # memory
    "nkundla",  # courts
    "nkuthazo",  # encouragement
    "nkwenkwe",  # boy
    "nobangela",  # cause
    "nokrwece",  # seashells
    "nomathotholo",  # radio
    "nombombiya",  # penguin
    "nomeva",  # wasp
    "nontlalontle",  # social worker
    "nopopi",  # doll
    "nqa",  # hip
    "nqaba",  # castles
    "nqaku",  # point
    "nqanawe",  # ships
    "nqe",  # waist
    "nqindi",  # fist
    "nqongophala",  # shortage
    "nqulo",  # religion
    "nqununu",  # principals
    "nqwazi",  # hat
    "nqwelo",  # wagons
    "nqwelomoya",  # aeroplanes
    "ntaba",  # mountains
    "ntabamkhenkce",  # glaciers
    "ntabamlilo",  # volcanoes
    "ntaka",  # birds
    "ntamo",  # necks
    "ntatheli",  # journalism
    "ntende",  # palms
    "ntengiso",  # advertisements
    "ntlakohlaza",  # spring
    "ntlambo",  # valley
    "ntlango",  # desert
    "ntlanzi",  # fish
    "ntlekele",  # disasters
    "ntliziyo",  # hearts
    "ntlobo",  # kinds
    "ntlobontlobo",  # many types
    "ntloko",  # heads
    "ntlonipho",  # respect
    "ntlugu",  # pains
    "nto",  # things
    "ntolongo",  # jails
    "ntsana",  # babies
    "ntsapho",  # families
    "ntsasa",  # morning
    "ntsholongwane",  # germs
    "ntsiba",  # feathers
    "ntsimbi",  # beads
    "ntsimi",  # field
    "ntsini",  # laughter
    "ntso",  # kidneys
    "ntsuku",  # days
    "ntsusa",  # origin
    "ntwana",  # child
    "ntwasahlobo",  # spring
    "ntyatyambo",  # flowers
    "numzana",  # mister
    "nwe",  # finger
    "nwele",  # hairs
    "nxaninzi",  # polygon
    "nxeba",  # phone
    "nxila",  # drunkard
    "nxulumano",  # association
    "nxweme",  # coast
    "nyaka",  # year
    "nyama",  # rainbow
    "nyana",  # son
    "nyanga",  # months
    "nyango",  # treatments
    "nyaniso",  # truth
    "nyanya",  # ancestors
    "nyawo",  # feet
    "nyembezi",  # tears
    "nyi",  # bladder
    "nyo",  # tooth
    "nyoka",  # snakes
    "nyosi",  # bees
    "nyumereyitha",  # numerator
    "nzi",  # water
    "nzima",  # weight
    "nzipho",  # nails
    "nzulu",  # volume
    "nzuzo",  # profit
    "nzwane",  # toes
    "olo",  # yesterday
    "omi",  # life
    "ona",  # jealousy
    "ongameli",  # archbishop
    "ongezo",  # additive
    "ongikazi",  # nurse
    "ongo",  # nosebleed
    "onka",  # bread
    "ono",  # sin
    "oya",  # fur
    "parabola",  # parabola
    "paseji",  # passages
    "pati",  # parties
    "payina",  # pineapple
    "peni",  # pens
    "phahla",  # roof
    "phambili",  # penis
    "phambuka",  # intersection
    "phando",  # survey
    "phangi",  # mugger
    "phantsi",  # vagina
    "phawu",  # symptom
    "phika",  # shortness of breath
    "phiko",  # wing
    "pho",  # gift
    "pholigoni",  # polygon
    "phondo",  # horn
    "phumo",  # result
    "phunga",  # lung
    "phupha",  # dream
    "pilisi",  # pills
    "pinatshi",  # spinach
    "planga",  # plank
    "poyinti",  # point
    "qabane",  # comrade
    "qala",  # first
    "qalo",  # beginning
    "qamelo",  # pillow
    "qanda",  # egg
    "qatha",  # ankle
    "qathango",  # conditions
    "qela",  # group
    "qeshi",  # employer
    "qhamo",  # fruit
    "qhaqho",  # operations
    "qhelo",  # habit
    "qhinga",  # trick
    "qhoqhoqho",  # windpipe
    "qhuphe",  # short while
    "qina",  # fossil
    "qokobhe",  # shell
    "qolo",  # back
    "quluba",  # calf
    "qunube",  # wild berry
    "qwilikane",  # mumps
    "rayisi",  # rice
    "rediyo",  # radio
    "rhali",  # thread
    "rhamncwa",  # monster
    "rhawuti",  # Johannesburg
    "rhorho",  # pelvis
    "rhulumente",  # government
    "rhwaphilizo",  # corruption
    "rumathizima",  # rheumatism
    "sana",  # baby
    "sango",  # entrances
    "sapho",  # family
    "sebe",  # eyelash
    "sebenzi",  # employee
    "sekelo",  # base
    "sele",  # cell
    "shiya",  # eyebrows
    "shushu",  # temperature
    "siba",  # feather
    "sibali",  # brother-in-law
    "sika",  # winter
    "sila",  # tail
    "simi",  # farm
    "sindo",  # anger
    "sipha",  # ligament
    "sisi",  # sister
    "so",  # face
    "sompempe",  # referee
    "sondeza",  # approximation
    "su",  # intestine
    "suleleko",  # infection
    "sundululu",  # worm
    "tafile",  # tables
    "tapile",  # potatoes
    "tatomncinci",  # paternal uncles
    "tatomncini",  # paternal uncle
    "tena",  # brick
    "tephu",  # step
    "tha",  # ray of light
    "thabazi",  # expanse of water
    "thako",  # ingredient
    "thambo",  # bone
    "thamo",  # volume
    "thandazo",  # prayer
    "thandwa",  # beloved
    "thanga",  # pumpkin
    "thatha",  # nostril
    "thathaka",  # weakness
    "thathaki",  # witchcraft
    "theko",  # party
    "themba",  # hope
    "thende",  # heel
    "thetho",  # rule
    "thili",  # district
    "thombo",  # fountain
    "thondo",  # penis
    "thongo",  # sleep
    "thuba",  # chance
    "thumbu",  # intestine
    "thunzi",  # shade
    "thuthi",  # vehicle
    "thuthu",  # ashes
    "thuthuthu",  # motorbike
    "titshala",  # teacher
    "tiya",  # garden
    "tofu",  # injection
    "tshati",  # charts
    "tshato",  # marriage
    "tshayelo",  # broom
    "tshintshatshintsha",  # Variation
    "tshisa",  # heartburn
    "tshixo",  # key
    "tshomi",  # friend
    "tulo",  # chair
    "tumato",  # tomatoes
    "tv",  # TV
    "tya",  # food
    "tyala",  # case
    "tyalo",  # plant
    "tye",  # stone
    "tyholo",  # charge
    "tywala",  # alcohol
    "va",  # experience
    "vatala",  # watermelons
    "vavanyo",  # exam
    "veki",  # weeks
    "veni",  # van
    "venkile",  # shops
    "vila",  # laziness
    "virasi",  # viruses
    "vivingane",  # moth
    "viwo",  # exam
    "vo",  # opinion
    "vulindlela",  # pioneer
    "vulo",  # Monday
    "vumba",  # smell
    "vumelanisi",  # concord
    "vundla",  # rabbit
    "wele",  # twin
    "wikhi",  # weakness
    "wodi",  # ward
    "wotshi",  # clocks
    "xabiso",  # price
    "xeko",  # city
    "xesha",  # time
    "xhala",  # anxiety
    "xhego",  # old man
    "xhegokazi",  # old woman
    "xhobo",  # tool
    "xhongo",  # shin
    "xhosa",  # Xhosa
    "xoki",  # falsehood
    "xolo",  # peace
    "xube",  # mixture
    "yeni",  # husband
    "yeza",  # medicine
    "yezi",  # dizziness
    "yobisi",  # drug
    "yonke",  # sum
    "yunivesithi",  # universities
    "yure",  # hours
    "za",  # wave
    "zali",  # parent
    "zekelo",  # example
    "zi",  # homestead
    "ziko",  # fireplaces
    "zimba",  # body
    "zimela",  # independence
    "zinyo",  # teeth
    "zipho",  # nail
    "zulu",  # Zulu
    "zuzu",  # minute
    "zuzwana",  # second
    "zwane",  # toe
    "zwe",  # country
    "zwi",  # voice

    # --- Third bulk source: Kaikki.org's isiXhosa Wiktionary extract,
    # CC BY-SA 4.0 (Wiktionary content license) ---
    # https://kaikki.org/dictionary/Xhosa/ -- same organization/format
    # as the Kaikki extracts already used for lute-shona, 3,371 distinct
    # words (bigger raw count than isixhosa.click, though with overlap).
    # Extraction mirrored isixhosa.click's proven method exactly (see
    # the block above): try every prefix in NOUN_CLASS_PREFIXES,
    # longest-first, against every `forms`-listed surface form
    # (singular and plural both, each independently tagged), ignore the
    # source's own class label, gate on the vowel-stem requirement for
    # NOUN_PREFIXES_REQUIRE_VOWEL_STEM, keep the first non-empty
    # remainder. ~283 stub/redirect entries (pages like "bafana" whose
    # only content is "simple plural of umfana", with no `forms` data of
    # their own) and ~28 hyphenated/multi-word forms were skipped, same
    # categories excluded from the isixhosa.click round. Tone-marked
    # diacritics stripped via NFKD, same as every other Kaikki import.
    # Net result: 1,045 new noun roots.
    "abokwe", "abonkolo", "afobe", "agweba", "agwityi", "ahlukaniso",
    "ahombe", "akhi", "akhulu", "akwatsha", "alathiso", "andle",
    "ando", "ani", "antya", "anuse", "aphompolo", "arha",
    "awomkhulu", "azi", "azinge", "azinzulu", "azisi", "ba",
    "babalo", "babazo", "balo", "bamba", "bandezeli", "bandla",
    "bango", "bani", "bawo", "bawomkhulu", "baya", "bhabhathane",
    "bhadi", "bhafrum", "bhafu", "bhakabhaka", "bhaloni", "bhambathiso",
    "bhanana", "bhanki", "bhanti", "bhari", "bhatom", "bhatyi",
    "bhavu", "bhayaskopho", "bhayibhile", "bhayisikile", "bhejane", "bhekile",
    "bheriyam", "bhexeshi", "bhinqa", "bhinqo", "bhiyozo", "bhobho",
    "bhoda", "bhokhwe", "bhokisi", "bhomoyi", "bhono", "bhotolo",
    "bhotwe", "bhulukhwe", "bhunga", "bhungane", "bi", "binzana",
    "bizo", "boko", "bomvu", "bona", "bonda", "bonelelo",
    "bongo", "boniso", "bophelelo", "bubu", "bulala", "bulali",
    "buliso", "bulo", "bululu", "bumbi", "bunu", "butho",
    "buzi", "caka", "cakazana", "camba", "caphucaphu", "cawa",
    "cebo", "celo", "cesina", "chankcatho", "chibi", "chochoyi",
    "chopho", "chotho", "chumisi", "chweli", "chwethezi", "cilikishe",
    "cimbi", "cinezeli", "cingwane", "coci", "cuba", "cula",
    "culi", "cwambu", "cwangciso", "cwecwe", "cwethe", "da",
    "dada", "dade", "damu", "danga", "dayimani", "dayisi",
    "dengwane", "desika", "dikshinari", "dilesi", "diliya", "dinala",
    "dinga", "dingo", "dini", "dlabantu", "dlavu", "dlavuza",
    "dlelo", "dlobha", "dlozi", "dlwengu", "dolophana", "dosha",
    "dudla", "dudo", "duko", "duli", "dumzeli", "dunguli",
    "dungulu", "dyakalashe", "dyarho", "dyokhwe", "dzedze", "ela",
    "ele", "elungu", "elusi", "embe", "emi", "engwitshi",
    "enja", "enzeko", "enzo", "epha", "esuthu", "ezinja",
    "fa", "fana", "fanekiselo", "fanekisozwi", "fani", "feksi",
    "fema", "fi", "finyezo", "fiyo", "flegi", "florini",
    "folo", "fomu", "foni", "fosiforasi", "foti", "fotsholo",
    "fowuni", "fudumezi", "fula", "fundo", "fuyi", "fuziselo",
    "gada", "gaga", "galiyoni", "gandaganda", "gangxa", "gani",
    "gaqa", "gaqo", "gatha", "gaxothi", "gcawu", "gciwane",
    "gcobo", "geza", "gidimi", "gilamkhuba", "ginkci", "gogogo",
    "golide", "gorha", "gosa", "gqibo", "gqomogqomo", "gqubuthelo",
    "gqudu", "gqugula", "gqumo", "gqwetha", "gqwirhakazi", "gramza",
    "gubhu", "gubu", "gunya", "gwala", "gwebu", "gwinya",
    "gxagxa", "gxina", "gxobhozo", "hagu", "hambi", "hange",
    "hayidrojini", "heji", "helegu", "hendi", "henyukazi", "hilihili",
    "hlakulo", "hlali", "hlalo", "hlambi", "hlanga", "hlangala",
    "hlanti", "hlawuli", "hlebo", "hleka", "hleli", "hlelo",
    "hlengesi", "hlodi", "hloko", "hlolo", "hlolokazi", "hlomelo",
    "hlonyane", "hlosi", "hlu", "hluze", "hluzi", "hlwa",
    "hobe", "hogo", "holide", "hotele", "jaji", "jam",
    "jelo", "jezi", "jogo", "kali", "kampu", "kantini",
    "karukwini", "kawusi", "keki", "ketile", "keyiki", "khaba",
    "khabhathi", "khabhoni", "khadbodi", "khala", "khaliso", "khalsiyam",
    "khangati", "khankaso", "khankatha", "khapetshu", "khaphetshu", "khaphi",
    "khasi", "khayithi", "khefi", "khemesti", "khenkethi", "khetha",
    "khetshe", "khewu", "khi", "khitshane", "khitshi", "khiwane",
    "khoba", "khohleli", "khokelo", "khokho", "kholonjane", "khombandlela",
    "khombe", "khonkwane", "khonto", "khonzazana", "khonzi", "khophe",
    "khosana", "khosazana", "khosi", "khosikazi", "khowa", "khozana",
    "khozi", "khuba", "khukhu", "khuko", "khukukazi", "khululo",
    "khupha", "khuseleko", "khuthala", "khwapha", "khwe", "khwebu",
    "khwenene", "khwenkxe", "khwepha", "khwetha", "kirikitsi", "kogina",
    "koma", "komiti", "komkhulu", "kona", "kopolo", "korokoro",
    "kratshi", "krele", "krelekrele", "kriwi", "kro", "kroba",
    "krokro", "kroti", "krwala", "krweqe", "kunzi", "kwere",
    "lahle", "lali", "lambi", "lamuni", "landelayo", "lantshi",
    "lanya", "lanyakazi", "laphu", "lawu", "lawulo", "layisensi",
    "lekese", "leko", "lenga", "lengalenga", "leyi", "leyiti",
    "lima", "limo", "lingane", "lisela", "lobi", "lokishi",
    "lolo", "londa", "londolozo", "longwe", "lonji", "lonwabo",
    "lori", "lothe", "lozi", "lulwane", "lumko", "lunda",
    "lungelo", "lungiso", "luphala", "lusi", "lwa", "lwakhiwo",
    "lwaluko", "lwane", "lwazi", "m", "mabonakude", "magneziyam",
    "makhulu", "mamba", "mamva", "mangaliso", "mango", "maphambili",
    "mazi", "mbabala", "mbaleki", "mbalelwano", "mbalisi", "mbalo",
    "mbambano", "mbandezelo", "mbangwa", "mbeko", "mbeleko", "mbiza",
    "mbizo", "mbola", "mbombo", "mbona", "mbongi", "mbongolo",
    "mbovane", "mbubhane", "mbuzi", "melika", "melwana", "melwane",
    "mfele", "mfundiso", "mfuyo", "mhemhe", "mi", "mozulu",
    "mpala", "mpambano", "mpangele", "mpangelo", "mpatho", "mpembelelo",
    "mpempe", "mpendlo", "mpepho", "mpi", "mpicotho", "mpindaphindo",
    "mpisi", "mpofu", "mpompi", "mpuhliso", "mpukane", "mpumalanga",
    "mpumelelo", "mpungulu", "mpungutye", "mpunzi", "mpuphuma", "muncumuncu",
    "mvelaphi", "mvu", "mvumi", "mvuyo", "nakwe", "nama",
    "nandi", "natha", "ncanca", "ncanda", "ncinda", "nciniba",
    "ncumo", "ncuthu", "ncutshe", "ndaka", "ndeni", "ndi",
    "ndibaniso", "ndlalifa", "ndle", "ndlwana", "ndondolo", "ndongomane",
    "ndongwe", "nduku", "ndulana", "nduli", "ndumiso", "ndumo",
    "nduna", "ndwe", "ndwendwe", "ndyebo", "nene", "nenga",
    "nga", "ngabangaba", "ngada", "ngcaciso", "ngcamango", "ngcamba",
    "ngcambu", "ngcatshi", "ngcebiso", "ngcelo", "ngcinga", "ngcobo",
    "ngcola", "ngcombolo", "ngcongconi", "ngcongolo", "ngcuka", "ngculaza",
    "ngcungcu", "ngcungela", "ngcuntsu", "ngcwaba", "ngcwabo", "ngcwambu",
    "ngcwangciso", "ngcwele", "ngelosi", "ngeniso", "ngobozi", "ngolwane",
    "ngonyama", "ngozi", "ngqala", "ngqalo", "ngqaphu", "ngqatha",
    "ngqeqesho", "ngqesho", "ngqibo", "ngqikelelo", "ngqiniseko", "ngqiqo",
    "ngqolowa", "ngqongqo", "ngqoqosho", "ngqosha", "ngqukuva", "ngqula",
    "ngqumba", "ngqumbo", "ngquphantsi", "ngququzelelo", "ngqushu", "ngulube",
    "ngunda", "ngungane", "nguqulelo", "nguqulo", "ngwane", "ngweletshetshe",
    "ngwenkala", "ngwevu", "ngxabano", "ngxabela", "ngxande", "ngxanduva",
    "ngxobo", "ngxothi", "ngxoxo", "ngxube", "ngxwabangxwaba", "nhanha",
    "nina", "nini", "njengele", "njineli", "njingalwazi", "njoli",
    "njongilanga", "njongo", "nkabi", "nkamela", "nkangeleko", "nkanyamba",
    "nkawu", "nkcani", "nkcaso", "nkcazelo", "nkcazo", "nkcitho",
    "nkcochoyi", "nkedama", "nkenketho", "nkewu", "nkitha", "nkohlakalo",
    "nkokeli", "nkoko", "nkomfa", "nkonyane", "nkophe", "nkosana",
    "nkosikazi", "nkozana", "nkozi", "nkozo", "nkqantosi", "nkqayi",
    "nkqekezo", "nkqubela", "nkqwala", "nkratya", "nkrwebo", "nkubabulongwe",
    "nkukho", "nkukhu", "nkuko", "nkula", "nkulu", "nkululeko",
    "nkulumbuso", "nkungu", "nkuni", "nkunkuma", "nkunzi", "nkuphiswano",
    "nkwakhwa", "nkwalimanzi", "nkwenkwezi", "nkxaso", "nkxwaleko", "nobhala",
    "nodladla", "nogqaza", "nomadudwane", "nomanxezane", "nomatse", "nomyani",
    "noncwadi", "nondlwane", "nondyebo", "nongendi", "nonkala", "noposi",
    "nosilarha", "nothi", "nqamlezo", "nqanawa", "nqantloko", "nqatha",
    "nqathe", "nqawa", "nqenerha", "nqina", "nqoba", "nqonqo",
    "nqoza", "nqu", "nqugwala", "nqundu", "nqwela", "nqweno",
    "ntakumba", "ntakwethu", "ntambane", "ntambo", "ntango", "ntase",
    "ntente", "ntethe", "ntetho", "nti", "ntili", "ntla",
    "ntlabathi", "ntlalo", "ntlama", "ntlanga", "ntlanganiso", "ntlanti",
    "ntlantla", "ntlaselo", "ntlawulo", "ntlekisa", "ntlohlo", "ntlola",
    "ntloni", "ntlontlo", "ntlu", "ntlutha", "ntlwathi", "ntolo",
    "ntombazana", "ntonga", "ntotho", "ntothoviyane", "ntru", "ntrwana",
    "ntsalela", "ntshaba", "ntshatsheli", "ntshebe", "ntshicilelo", "ntshili",
    "ntshintsho", "ntsho", "ntsholo", "ntshonalanga", "ntshontsho", "ntshukumo",
    "ntshulube", "ntshumayelo", "ntsika", "ntsikelelo", "ntsikizi", "ntsikrobana",
    "ntsindiso", "ntsingiselo", "ntsizwa", "ntsokolo", "ntsomi", "ntsuleleko",
    "ntsulelo", "ntsumantsumane", "ntsumpa", "ntswazi", "ntswidi", "ntuku",
    "ntuli", "ntuthu", "ntwala", "ntyabontyi", "ntyafo", "ntywenka",
    "nweba", "nxagu", "nxala", "nxalenye", "nxano", "nxantathu",
    "nxanxadi", "nxaxheba", "nxele", "nxibamxhaka", "nyamakazi", "nyameko",
    "nyangi", "nyani", "nyathelo", "nyathi", "nyazi", "nyhadala",
    "nyholoba", "nyhweba", "nyibiba", "nyilo", "nyithi", "nyoko",
    "nyonga", "nyongo", "nyoni", "nyonyovu", "nyulo", "nyushu",
    "nzala", "nzame", "nzolo", "nzondo", "nzululwazi", "nzwakazi",
    "ofa", "oji", "oldathi", "ongololo", "opholo", "osala",
    "paji", "paki", "pala", "palamente", "palana", "papa",
    "pasi", "peki", "peliti", "pensile", "pere", "pesika",
    "petroli", "peyinti", "pha", "phakamiso", "phako", "phanda",
    "phandle", "phango", "phaphu", "phathi", "phathiswa", "phefumlo",
    "pheki", "phela", "phelo", "phepha", "phephamvume", "phephandaba",
    "phezulu", "phini", "pholishi", "phosiso", "phupho", "phuthi",
    "pili", "pleyiti", "polisa", "porho", "posi", "potaziyam",
    "potyi", "pulazi", "qaba", "qadi", "qakamba", "qambelo",
    "qaqa", "qaqaqa", "qaqawuli", "qaqoba", "qashiso", "qendu",
    "qeqeshi", "qeshwa", "qhagi", "qhakuva", "qhalo", "qhaphu",
    "qhawe", "qhayi", "qhekeza", "qhina", "qhiya", "qholo",
    "qhosha", "qhubi", "qhude", "qhumiso", "qhwala", "qili",
    "qingatha", "qinisekiso", "qithi", "qobokhe", "qokolo", "qolomba",
    "qondiso", "qondo", "qonga", "qongqothwane", "qosho", "qu",
    "qula", "qulu", "ququ", "ququzeleli", "qwane", "qwarhashe",
    "qwayitho", "qwayito", "randi", "reki", "resiphi", "restyu",
    "rhafu", "rhalarhume", "rhamba", "rhanisi", "rhanuga", "rharnate",
    "rhasi", "rhatya", "rhewu", "rhofu", "rhubuluzi", "rhudo",
    "rhumo", "rhwebo", "rozi", "sa", "sadlunge", "salfari",
    "sarha", "sasazi", "sekela", "seko", "sela", "seli",
    "sengwitshi", "sepha", "sesane", "sheko", "shishini", "shumi",
    "shunqulelo", "shwa", "shwankathelo", "sibalikazi", "sibonda", "siko",
    "silayi", "silivere", "sizi", "sodolophu", "sofa", "soldathi",
    "somashishini", "sombululo", "somfazi", "songololo", "sonto", "sopholo",
    "sosala", "sundulu", "suphu", "suthu", "suzo", "swazi",
    "swekile", "sweleka", "takane", "talato", "tali", "tampu",
    "tawuli", "tayala", "teknoloji", "teksi", "teps", "thafa",
    "thambeko", "thamsanqa", "thana", "thandazwe", "thango", "thathi",
    "the", "thembiso", "thengisi", "thetha", "thethe", "thintitha",
    "thium", "thiyelo", "thokazi", "thole", "thombe", "thonyama",
    "thoyilethi", "thsaba", "thuko", "thukuthezi", "thuli", "thulu",
    "thunga", "thunywa", "thwa", "thwalo", "thwane", "tikoloshe",
    "tipoti", "tishi", "toliki", "tolofiya", "tora", "toti",
    "tovu", "trato", "tshaba", "tshakazi", "tshala", "tshana",
    "tsheke", "tsheki", "tshintshi", "tshizi", "tsotsi", "tswele",
    "tyathanga", "tyeba", "tyebi", "tyeleli", "tyhakala", "tyhefu",
    "tyuthu", "tyuwa", "ulu", "vakalisi", "valo", "vatho",
    "vili", "vimba", "vingco", "voti", "vumelwano", "vuno",
    "vuthuvuthu", "vuyo", "vuzo", "wa", "wayini", "wulu",
    "xa", "xam", "xande", "xetsha", "xhadi", "xhalanga",
    "xoxo", "xoxozi", "xwebhu", "yalelo", "yalezo", "yelenqe",
    "yezo", "yihlo", "yise", "zabalazo", "zala", "zalwane",
    "zamo", "zantsi", "zathu", "zekeliso", "zembe", "ziba",
    "zibulala", "zim", "zingeli", "zo", "zobo", "zukulwana",
    "zwana",
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
    "bal",     # ukubala - count, from "Indoda engenakhaya" story (ukubala, "the counting")

    # --- Bulk import from isixhosa.click (words.csv), CC BY-SA 4.0 ---
    # Same source/methodology as the noun bulk import above -- see
    # NOUN_ROOT_LEXICON's header comment and lute-xhosa DESIGN.md for
    # full provenance. Verb roots derived by stripping the final vowel
    # from the CSV's already-bare (infinitive-marker-free) xhosa column,
    # cross-checked against the infinitive column where present.
    "balek",  # run
    "balulek",  # be important
    "bamb",  # catch
    "band",  # be cold
    "bang",  # claim
    "bek",  # put
    "bekelis",  # move
    "beth",  # hit
    "bethw",  # lose
    "bhaf",  # bathe
    "bhafis",  # wish happy birthday
    "bhak",  # bake
    "bhal",  # write
    "bhalis",  # register
    "bhatal",  # pay
    "bhek",  # travel towards
    "bhengez",  # advertise
    "bhity",  # become thin
    "bhiyoz",  # celebrate
    "bhodl",  # burp
    "bhomboloz",  # shout
    "bhotis",  # greet
    "bhubh",  # pass away
    "bil",  # sweat
    "bilis",  # boil
    "biz",  # call
    "bonis",  # show
    "boph",  # bandage
    "bukel",  # watch
    "bulal",  # kill
    "bulel",  # thank
    "bulis",  # greet
    "buy",  # return
    "buyis",  # bring back
    "buz",  # ask
    "cacis",  # explain
    "cand",  # chop
    "caphuk",  # become irritated
    "caphukis",  # irritate
    "caphul",  # extract
    "cebis",  # advise
    "cel",  # ask politely
    "cham",  # urinate
    "chaphazel",  # affect
    "chaz",  # describe
    "cheb",  # cut
    "chith",  # destroy
    "chol",  # pick up
    "cim",  # extinguish
    "cimel",  # close eyes
    "cinezel",  # press down on
    "cing",  # think
    "coc",  # clean
    "cof",  # click
    "cothis",  # slow down
    "cul",  # sing
    "cwangcis",  # plan
    "dad",  # swim
    "dan",  # become disappointed
    "danis",  # dance
    "dek",  # lay table
    "diban",  # meet
    "dibanis",  # add
    "diliz",  # demolish
    "ding",  # need
    "dinw",  # become tired
    "dlal",  # play
    "dlul",  # pass
    "dlulis",  # pass on
    "dumb",  # swell up
    "fak",  # put in
    "fan",  # be like
    "fanelek",  # become suitable
    "fihl",  # hide
    "fik",  # arrive
    "fikelelek",  # be affordable
    "fol",  # queue
    "fudukel",  # move
    "fudumal",  # become warm
    "fuman",  # find
    "fumanek",  # be achievable
    "fun",  # look for
    "fundis",  # teach
    "funek",  # be necessary
    "fung",  # take an oath
    "gabh",  # vomit
    "galel",  # add (an ingredient)
    "gcin",  # keep
    "gcwal",  # become full
    "gcwalis",  # fill
    "gez",  # be naughty
    "gibisel",  # throw
    "giny",  # swallow
    "gob",  # bend over
    "godol",  # be cold
    "goduk",  # go home
    "gony",  # vaccinate
    "gqabhuk",  # burst
    "gqib",  # decide
    "gqibezel",  # complete
    "gqith",  # pass
    "grumb",  # dig
    "gruzuk",  # bruise
    "gug",  # become old
    "gul",  # be sick
    "guq",  # bend
    "guquk",  # turn
    "gwayimb",  # strike
    "gweb",  # judge
    "gxininis",  # emphasise
    "hlab",  # inject
    "hlafun",  # chew
    "hlal",  # live
    "hlaluty",  # analyse
    "hlamb",  # wash
    "hlasel",  # attack
    "hlawul",  # pay
    "hlek",  # laugh
    "hlikihl",  # rub
    "hlinz",  # operate
    "hlis",  # lower
    "hloniph",  # respect
    "hlum",  # flourish
    "hombis",  # decorate
    "hoy",  # pay attention
    "jik",  # turn
    "jikelez",  # turn around
    "jing",  # hang
    "jol",  # date
    "jong",  # look
    "jov",  # inject
    "jul",  # throw
    "kam",  # comb
    "kh",  # ever
    "khab",  # kick
    "khal",  # cry out
    "khalaz",  # complain
    "khalis",  # ring
    "khamis",  # open mouth
    "khangel",  # look for
    "khaph",  # accompany
    "khawulez",  # hurry
    "khaziml",  # shine
    "kheth",  # choose
    "khohlakal",  # become cruel
    "khohlel",  # cough
    "kholelw",  # believe
    "khomb",  # point
    "khonkoth",  # bark
    "khonz",  # serve
    "khul",  # grow
    "khulul",  # take off
    "khumbul",  # miss
    "khumbuz",  # remind
    "khuph",  # take out
    "khusel",  # protect
    "khuthaz",  # encourage
    "khwaz",  # shout
    "khwel",  # get on
    "krazuk",  # tear apart
    "krob",  # peep
    "krunek",  # become sprained
    "krwemp",  # scratch
    "kwelet",  # owe money
    "lahl",  # dump
    "lahlek",  # become lost
    "lal",  # sleep
    "lalan",  # have sex
    "lamb",  # become hungry
    "landel",  # follow
    "lawul",  # control
    "layit",  # light
    "libal",  # forget
    "lil",  # cry
    "lind",  # wait
    "lingan",  # be equal
    "lob",  # fish
    "lolong",  # exercise
    "lum",  # bite
    "lung",  # become OK
    "lungis",  # fix
    "lungiselel",  # prepare
    "lw",  # fight
    "mamel",  # listen
    "manyanis",  # integrate
    "mem",  # invite
    "munc",  # suck
    "ncamathisel",  # stick on
    "nced",  # help
    "nciphis",  # reduce
    "ncokol",  # chat
    "ncom",  # praise
    "ncothul",  # weed
    "ncum",  # smile
    "ncwel",  # bully
    "neth",  # rain
    "ngcaml",  # taste
    "ngcangcazel",  # shake
    "ngcolis",  # make dirty
    "ngongoz",  # beat
    "ngqengq",  # lie down
    "ngqish",  # stamp
    "ngqong",  # crowd
    "ngxam",  # become hurried
    "ngxamisek",  # become urgent
    "ngxol",  # make noise
    "ngxolis",  # scold
    "nik",  # give
    "nikezel",  # submit
    "nith",  # knit
    "nkcenkceshel",  # water
    "nqab",  # become scarce
    "nqunq",  # chop
    "nqwenelel",  # wish for
    "ntlontlozel",  # stare
    "ntshul",  # sprout
    "nuk",  # smell
    "nxib",  # wear
    "nxil",  # become drunk
    "nyamezel",  # persevere
    "nyang",  # cure
    "nyangek",  # get well
    "nyuk",  # ascend
    "nyus",  # lift
    "pet",  # dig
    "peyint",  # paint
    "ph",  # give
    "phak",  # serve
    "phakam",  # stand up
    "phakamis",  # lift
    "phangel",  # be employed
    "phath",  # afflict
    "phathel",  # bring
    "phawul",  # characterise
    "phazam",  # make a mistake
    "phefuml",  # breathe
    "phek",  # cook
    "phel",  # end
    "phendul",  # answer
    "phengulul",  # search
    "phil",  # live
    "phind",  # repeat
    "phindaphind",  # Multiply
    "phindez",  # exact revenge
    "phol",  # cool down
    "phosis",  # lie
    "phox",  # disappoint
    "phucuk",  # improve
    "phucul",  # improve
    "phulul",  # massage
    "phum",  # come from
    "phumelel",  # succeed
    "phuml",  # rest
    "phung",  # drink
    "phuph",  # dream
    "phuz",  # kiss
    "pul",  # rinse
    "qab",  # spread
    "qal",  # start
    "qaphel",  # notice
    "qaqamb",  # ache
    "qengqelek",  # rolling
    "qhankqalaz",  # protest
    "qhaqh",  # operate
    "qhath",  # trick
    "qhayis",  # boast
    "qhekez",  # break into
    "qhel",  # become used to
    "qhub",  # drive
    "qhubek",  # continue
    "qhubekek",  # continue
    "qhushek",  # tuck
    "qhwab",  # clap
    "qhwanyaz",  # blink
    "qhwesh",  # escape
    "qin",  # become strong
    "qinisek",  # become sure
    "qinisekis",  # determine
    "qiq",  # Rationalise
    "qokelel",  # collect
    "qond",  # understand
    "qumb",  # become angry
    "rhalel",  # long for
    "rhol",  # earn
    "rhubuluz",  # crawl
    "rhuq",  # drag
    "s",  # take to
    "sal",  # remain
    "sandul",  # just
    "sarh",  # saw
    "sasaz",  # spread
    "sebenzis",  # use
    "sebez",  # whisper
    "sel",  # drink
    "shawut",  # shout
    "shiy",  # leave
    "shiyek",  # be left
    "shukum",  # move
    "shukumis",  # move
    "shumayel",  # preach
    "shush",  # drink heavily
    "sik",  # cut
    "sol",  # blame
    "sondel",  # come closer
    "song",  # fold
    "suk",  # come from
    "sul",  # wipe
    "sus",  # remove
    "swel",  # lack
    "swelek",  # pass away
    "th",  # say
    "thabath",  # subtract
    "thamb",  # become soft
    "thand",  # like
    "thandabuz",  # doubt
    "thandaz",  # pray
    "thath",  # take
    "thelekel",  # compute
    "thelekis",  # compare
    "themb",  # hope
    "thembis",  # promise
    "thengis",  # sell
    "theth",  # speak
    "thiml",  # sneeze
    "thob",  # lower
    "thobel",  # obey
    "thuk",  # swear
    "thul",  # be quiet
    "thum",  # send
    "thung",  # sew
    "thuthuzel",  # calm
    "thwal",  # carry
    "tof",  # inject
    "tsal",  # pull
    "tsalel",  # call
    "tsh",  # burn
    "tshabalalis",  # destroy
    "tshat",  # marry
    "tshay",  # smoke
    "tshintsh",  # change
    "tshis",  # burn
    "tshitshiz",  # hiss
    "tshix",  # lock
    "tshon",  # set
    "tsib",  # jump
    "twez",  # stretch
    "tyal",  # owe
    "tyand",  # operate
    "tyeb",  # become fat
    "tyhutyh",  # spread
    "v",  # feel
    "val",  # close
    "vamb",  # tattoo
    "vel",  # come from
    "velis",  # produce
    "vuk",  # wake up
    "vul",  # open
    "vum",  # agree
    "vumel",  # allow
    "vuy",  # be happy
    "w",  # fall
    "wis",  # drop
    "xaban",  # argue
    "xabis",  # cost
    "xelel",  # tell
    "xhakamful",  # grab
    "xhaphak",  # become common
    "xhaphaz",  # abuse
    "xhas",  # support
    "xhents",  # dance
    "xhokonx",  # provoke
    "xhomekek",  # depend
    "xhum",  # jump
    "xilong",  # examine
    "xobul",  # peel
    "xok",  # lie
    "xolel",  # forgive
    "xonx",  # carve
    "y",  # go to
    "yal",  # advise
    "yalel",  # command
    "yek",  # give up
    "yel",  # sink
    "zal",  # become full
    "zalis",  # fill
    "zam",  # try
    "zamis",  # stir
    "zimel",  # be independent
    "zimisel",  # intend
    "zingel",  # hunt
    "ziqhelis",  # practise
    "zis",  # bring
    "zithemb",  # be confident
    "zob",  # draw
    "zol",  # calm down
    "zul",  # wander

    # --- From Kaikki.org's isiXhosa Wiktionary extract, CC BY-SA 4.0 --
    # see the matching comment above NOUN_ROOT_LEXICON for source and
    # methodology. Verb word field is already the bare citation root
    # (no uku- prefix, unlike Shona's Kaikki data), so extraction was
    # just: strip diacritics, lowercase, strip the final vowel. A
    # handful of very short (1-letter) roots came out of this --
    # 'b'/'m'/'n'/'z', from the common 2-letter verbs -ba- (be/
    # become), -ma- (halt/stop), -na- (rain), -za- (come) -- flagged as
    # the same collision-risk category as the existing 1-letter 'w'/'y'
    # entries above; not preemptively fixed, watch for collisions the
    # same way the Shona short-root additions were checked (see
    # tests/test_morphology.py and lute-shona's equivalent).
    # Net result: 674 new verb roots.
    "ab", "agwenx", "ahluk", "ahlukanis", "ahlul", "akh", "akham", "al",
    "alaman", "alath", "alathis", "alel", "aluk", "alus", "ambath", "amkel",
    "and", "andis", "andlal", "anek", "anel", "anelisek", "aphuk", "aphul",
    "az", "azis", "b", "babaz", "balis", "balul", "bandezel", "banek",
    "bas", "bax", "bebulul", "belek", "bengezel", "bethelel", "bhabh", "bhabhazel",
    "bhadl", "bhadul", "bhanxek", "bhanyabhany", "bhaq", "bhatalis", "bhed", "bhej",
    "bhentsis", "bhexesh", "bhid", "bhinq", "bhod", "bhol", "bhox", "bhuc",
    "bhud", "bhudl", "bhukuq", "bhul", "bhuqabhuq", "bik", "bol", "bolek",
    "bonakal", "bond", "bong", "bongoz", "bonisis", "bothoz", "buk", "bukek",
    "bukekel", "bul", "bumb", "bun", "busis", "buth", "buyekez", "buyel",
    "cac", "cacel", "calul", "camang", "cambalal", "ceb", "ceng", "cengcelez",
    "chach", "chan", "chas", "chiz", "chokoz", "chong", "choph", "chub",
    "chukumis", "chum", "chunub", "chwechwel", "chwel", "chwethez", "cik", "col",
    "coth", "cothisis", "cukucez", "cuphul", "dakumb", "damb", "dambis", "dandaphis",
    "danduluk", "dangalis", "del", "dend", "dilik", "dilishan", "dingek", "dinis",
    "dl", "dlalis", "dlamk", "dlob", "dlokov", "dlwengul", "donts", "dubul",
    "dud", "dudul", "dudum", "dumis", "dumzel", "dwelis", "dyarh", "dyibh",
    "dyobh", "eb", "elus", "end", "enz", "enzakal", "enzakalis", "enzek",
    "fanel", "fanis", "fef", "feketh", "fez", "fezekis", "finyez", "fot",
    "fowun", "fowunel", "fuduk", "fudumez", "fukam", "fumb", "fumbath", "fundel",
    "funquk", "funqul", "funx", "futh", "fuy", "gabadel", "gaq", "gawul",
    "gcad", "gcagc", "gcakamel", "gcob", "gculel", "gcum", "gcwek", "gebhul",
    "gibis", "gigithek", "gil", "giy", "godus", "gox", "gqats", "gqibel",
    "gqithis", "gqobhok", "gqobhoz", "gqogq", "gqugul", "gqum", "gqush", "gqwes",
    "gqweth", "gragram", "gray", "greny", "gubungel", "gudl", "guqul", "guqulel",
    "gush", "gutyul", "gwaz", "gwencel", "gwint", "gxaban", "gxalek", "gxek",
    "gxobh", "gxoth", "gxum", "hambel", "hambelan", "hend", "hl", "hlahlamb",
    "hlakul", "hlambulul", "hlangan", "hlangul", "hlanz", "hlaz", "hlazek", "hlaziy",
    "hlaziyek", "hleb", "hlehl", "hlekis", "hlel", "hlohloz", "hloml", "hlonel",
    "hlub", "hlukuhl", "hlungis", "hluph", "hluphek", "hluth", "hluz", "hlwabis",
    "hlwayel", "hlwempuz", "homb", "jaj", "jal", "jayiv", "jij", "jikel",
    "jiwul", "jiy", "joj", "jolis", "jongan", "jongek", "jongis", "kats",
    "kekel", "kel", "khahlel", "khaliph", "khand", "khangelek", "khankany", "khanuk",
    "khany", "khanyel", "khas", "khathal", "khathalel", "khathalisek", "khathaz", "khathazek",
    "khawul", "khawulel", "khenkcis", "khenketh", "khithik", "khohlis", "khohlw", "khokel",
    "khol", "kholis", "kholisek", "kholw", "khony", "khoth", "khub", "khubek",
    "khuhl", "khulis", "khululek", "khumsh", "khuphel", "khuphisan", "khuthal", "khuz",
    "khwenc", "khwezel", "khwitsh", "korobh", "kral", "krazul", "krikriz", "krokr",
    "kroz", "krun", "kruquk", "krwel", "lalis", "land", "langaz", "layish",
    "leng", "leq", "leth", "lethis", "lim", "lindel", "ling", "linganis",
    "lol", "londoloz", "lulek", "lumk", "lumkis", "luml", "luphal", "lus",
    "luz", "m", "mangal", "mangalis", "many", "matanis", "mb", "mel",
    "mhemhek", "mhomh", "mil", "mis", "mith", "mk", "monel", "mosh",
    "mpompoz", "n", "nab", "nabis", "nak", "nakekel", "nambith", "nambuz",
    "nath", "ncam", "ncamathel", "ncamis", "ncanc", "ncancis", "ncedis", "ncwin",
    "ndiyakuthand", "ndwendwel", "ngcilez", "ngcol", "ngcwab", "ngcwal", "ngen", "ngenis",
    "ngqal", "ngqaman", "ngqamanis", "ngqib", "ngqub", "ngqush", "nikel", "nityilik",
    "nkcunkc", "nkqonkqoz", "nqakul", "nqand", "nqanqathek", "nqanqaz", "nqen", "nqeth",
    "nqik", "nqom", "nqul", "nqum", "nquml", "nqwal", "nqwem", "nqwen",
    "nqwenel", "ntam", "ntlont", "ntshontsh", "ntsonkoth", "ntyiloz", "ntywil", "nwabulul",
    "nwenw", "nxakam", "nxanw", "nxul", "nyamek", "nyanis", "nyany", "nyanzel",
    "nyanzelis", "nyathel", "nyathelis", "nyel", "nyhamnyhek", "nyibilik", "nyibilikis", "nyinyithekis",
    "nyobulul", "nyul", "nyusel", "ohlway", "oj", "olul", "om", "omelel",
    "omelez", "on", "onak", "onakalis", "ondl", "onel", "ong", "ongamel",
    "ongez", "onqen", "onwab", "onwabel", "oph", "ophul", "oth", "othuk",
    "othukulul", "othus", "oyik", "oyis", "ozel", "pakish", "penapen", "phal",
    "phalal", "phalaz", "phamban", "phambuk", "phand", "phang", "phaph", "phazamis",
    "phekezel", "phelek", "phelel", "phemb", "pheph", "pheth", "phikis", "pholis",
    "phos", "phuhlis", "phumez", "phuncul", "phuphum", "phuthum", "pos", "pulush",
    "qabaqabaz", "qabul", "qaj", "qalekis", "qamb", "qaqawul", "qash", "qengq",
    "qeqesh", "qesh", "qhabalak", "qhagamshelan", "qhakaz", "qhal", "qham", "qhamuk",
    "qhawuk", "qhawul", "qhekek", "qhelek", "qhin", "qhobosh", "qhomf", "qhosh",
    "qhothoz", "qhots", "qhul", "qhum", "qhuqh", "qhwalel", "qhwith", "qikelel",
    "qinis", "qinisel", "qondis", "qoqosh", "qub", "qubud", "qubul", "quk",
    "qukumbel", "ququzel", "qwalasel", "qwel", "qweng", "rhabul", "rhal", "rharhaz",
    "rhawuzel", "rhintyel", "rhogol", "rhon", "rhoxis", "rhweb", "ripoth", "sabel",
    "sayin", "saz", "sek", "seng", "sez", "shenx", "shenxis", "shicilel",
    "shishin", "shukux", "shwaban", "shwaq", "sikelel", "sil", "sin", "sind",
    "sindis", "sing", "singath", "sombulul", "sukel", "sulel", "sungul", "suz",
    "thakath", "thakazelel", "thambis", "thandek", "thelekelel", "thez", "thimb", "thingaz",
    "thintel", "thiy", "thobek", "thoth", "thumel", "thuntubal", "thus", "thuth",
    "thuthuz", "thwas", "thwes", "tolik", "tshabalal", "tshayel", "tshic", "tshisek",
    "tshitshilizel", "tshiz", "tsho", "tshutshis", "tshwez", "tsibatsib", "tswin", "tswitswiz",
    "twabulul", "twezek", "tyabul", "tyekez", "tyel", "tyelel", "tyesh", "tyeshel",
    "tyhaf", "tyhafis", "tyhal", "tyhil", "tyhiliz", "tyhoboz", "tyhol", "tyhuth",
    "tyibilik", "tyis", "tyumb", "tyumz", "tywin", "vakal", "valel", "vavany",
    "vez", "vik", "vimb", "vingc", "visis", "vith", "viv", "vot",
    "votel", "vun", "vund", "vus", "vuselel", "vuth", "vuthulul", "vuthuz",
    "vuthw", "vuz", "wahl", "wel", "win", "wol", "wulul", "xabel",
    "xabisek", "xak", "xakek", "xax", "xel", "xelegwis", "xhabh", "xhal",
    "xhaml", "xhaph", "xhel", "xhol", "xhom", "xhumaxhum", "xhuth", "xhuzul",
    "xhwalek", "xhwil", "xhwith", "xing", "xol", "xov", "xox", "xoz",
    "xub", "xubh", "xukux", "xway", "yalez", "yelenq", "yol", "yolis",
    "z", "zabalaz", "zaml", "zekelel", "zel", "zinz", "zolis", "zum",
    "zungul", "zuz",
}

# Terminal vowels. Never emitted as their own token -- see lute-shona
# DESIGN.md section 5 for the reasoning (a lone Latin letter is
# low-value/noisy as a standalone token), confirmed to apply here too.
TERMINAL_VOWELS = {"a", "e", "i"}
