"""
Sanity checks for lute_xhosa_parser.morphology.split_word.

Run with: python tests/test_morphology.py (or `python -m pytest tests/`
if pytest is installed).

Every check here was dry-run against the actual code before being
written down (see lute-shona's DESIGN.md for why that discipline
matters -- several hand-traced expectations turned out wrong there
until verified this way). Source for all confirmed examples: J.C.
Oosthuysen, "The Grammar of isiXhosa" (SUN PRESS, 2016), plus
furman.edu/Oxford dictionary derivational examples -- see rules.py and
DESIGN.md for full citations.
"""

from lute_xhosa_parser.morphology import split_word


def check(word, expected):
    actual = split_word(word)
    assert actual == expected, f"{word!r}: expected {expected!r}, got {actual!r}"
    assert "".join(actual) == word, f"{word!r}: tokens {actual!r} do not reconstruct the original word"


def test_noun_classes_singular_plural_pairs():
    # cl.1/2 (um-/aba-)
    check("umntu", ["um", "ntu"])  # person
    check("abantu", ["aba", "ntu"])  # people
    # cl.1a/2a (u-/oo-) -- no separate class-prefix consonant, augment only
    check("ubhuti", ["u", "bhuti"])  # brother
    check("oobhuti", ["oo", "bhuti"])  # brothers
    check("utata", ["u", "tata"])  # father
    check("ootata", ["oo", "tata"])  # fathers
    # cl.3/4 (um-/imi-)
    check("umvubu", ["um", "vubu"])  # hippo
    check("imivubu", ["imi", "vubu"])  # hippos
    check("umthi", ["um", "thi"])  # tree
    check("imithi", ["imi", "thi"])  # trees
    # cl.5/6 (ili-/ama-)
    check("ilifu", ["ili", "fu"])  # cloud
    check("amafu", ["ama", "fu"])  # clouds
    # cl.7/8 (isi-/izi-)
    check("isikolo", ["isi", "kolo"])  # school
    check("izikolo", ["izi", "kolo"])  # schools
    check("isidenge", ["isi", "denge"])  # fool
    check("izidenge", ["izi", "denge"])  # fools
    # cl.9/10 (i(N)-/ii-) -- class 9's nasal fuses into the stem, no
    # separate bare-consonant-prefix layer like the other classes
    check("ingwe", ["i", "ngwe"])  # leopard
    check("iintombi", ["ii", "ntombi"])  # girls (singular "intombi" covered below)
    check("intombi", ["i", "ntombi"])  # girl
    check("indlela", ["i", "ndlela"])  # path/road/way
    # cl.11 (ulu-/u-)
    check("uluthi", ["ulu", "thi"])  # stick -- shares root "thi" with umthi/imithi (tree)
    check("uthando", ["u", "thando"])  # love


def test_cross_class_shared_roots():
    # Same root, different noun class, different meaning -- direct
    # isiXhosa parallel to Shona's kadzi/nhu cross-class roots.
    check("umhlobo", ["um", "hlobo"])  # friend (cl.1/3)
    check("uhlobo", ["u", "hlobo"])  # type (cl.11) -- same root, different sense
    check("ubuntu", ["ubu", "ntu"])  # humanity (cl.14) -- same root as umntu/abantu (person/people)


def test_derivational_noun_examples():
    # Same verb root (-qhekeza "break in/off", -phula "break") forming
    # different nouns across classes -- source: furman.edu/Oxford
    # dictionary. Consonant-mutated forms (e.g. class 9 "inkqekezo")
    # deliberately not seeded -- see rules.py.
    check("umqhekezi", ["um", "qhekezi"])  # burglar (cl.1)
    check("umqhekezo", ["um", "qhekezo"])  # event of breaking off (cl.3)
    check("isiqhekezi", ["isi", "qhekezi"])  # expert breaker (cl.7)
    check("uqhekezo", ["u", "qhekezo"])  # state of breaking (cl.11)
    check("umphuli", ["um", "phuli"])  # person who breaks things (cl.1)
    check("umphulo", ["um", "phulo"])  # event/manner of breaking (cl.3)
    check("uphulo", ["u", "phulo"])  # act of breaking (cl.11)
    check("ubuphuli", ["ubu", "phuli"])  # state of breaking (cl.14)


def test_verb_infinitives():
    # uku- (cl.15 infinitive), disambiguated from the identically-
    # spelled cl.15/17 noun/locative prefix by requiring a root-
    # lexicon hit, same mechanism as Shona's ku-.
    check("ukutya", ["uku", "tya"])  # to eat / food
    check("ukufa", ["uku", "fa"])  # to die / death -- 1-letter root "f", same collision-risk category as Shona's "d"
    check("ukubona", ["uku", "bona"])  # to see
    check("ukuthenga", ["uku", "thenga"])  # to buy
    check("ukudala", ["uku", "dala"])  # to create


def test_present_tense_ya_infix():
    check("ndiyasebenza", ["ndi", "ya", "sebenza"])  # I work/am working
    check("bayahamba", ["ba", "ya", "hamba"])  # they walk/are walking


def test_a_past_tense():
    # Only class 1's a-past fusion ("wa-") is confirmed so far --
    # other persons' forms are NOT guessed, see rules.py.
    check("wadala", ["wa", "dala"])  # he/she created


def test_perfect_tense_not_yet_modeled():
    # -ile is a suffix near the terminal vowel, not a prefix TAM
    # marker -- deliberately NOT modeled yet (needs a real change to
    # the stem resolver's terminal-vowel contract, not just new data).
    # Must stay whole rather than mis-split.
    check("bahambile", ["bahambile"])  # they have walked/gone
    check("ndifundile", ["ndifundile"])  # I have learnt / I am educated


def test_empty_and_minimal_input():
    check("", [""])
    check("a", ["a"])


if __name__ == "__main__":
    import sys
    import traceback

    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError:
            failures += 1
            print(f"FAIL {t.__name__}")
            traceback.print_exc()
    if failures:
        print(f"\n{failures}/{len(tests)} test functions failed")
        sys.exit(1)
    print(f"\nAll {len(tests)} test functions passed")
