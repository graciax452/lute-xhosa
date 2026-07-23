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
    # "imithi" (trees) is now ALSO a WORD_EXCEPTIONS collision, same as
    # "umthi" the singular -- see test_verb_noun_branch_collision_exceptions
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
    # cl.11 (ulu-/u-) -- "uluthi" (stick) is a WORD_EXCEPTIONS collision,
    # see test_verb_noun_branch_collision_exceptions
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
    # deliberately not seeded -- see rules.py. "umqhekezi"/"isiqhekezi"
    # are WORD_EXCEPTIONS collisions (see test_verb_noun_branch_collision_exceptions).
    check("umqhekezo", ["um", "qhekezo"])  # event of breaking off (cl.3)
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


def test_real_story_correct_splits():
    # From "Ingonyama nenkawu" (The Lion and the Monkey) -- confirms
    # the engine generalizes to real narrative text it wasn't built
    # against, same validation method as lute-shona's grandpa-tortoise
    # story. Of note: "kufa" here comes from "ndiza kufa" ("I am going
    # to die") -- the periphrastic future construction (auxiliary
    # "za" + infinitive with the augment dropped) that the pre-
    # Oosthuysen research flagged but hadn't verified; this is the
    # first real-text confirmation of it, and it splits correctly even
    # though the engine gets there via the class 15/17 subject-concord
    # path rather than a dedicated augment-dropped-infinitive rule --
    # same token output either way.
    check("indlela", ["i", "ndlela"])  # the way/manner
    check("kufa", ["ku", "fa"])  # (going) to die -- periphrastic future, augment dropped
    check("ndihambe", ["ndi", "hambe"])  # that I may go (subjunctive, root "hamb" + -e)
    check("ukubona", ["uku", "bona"])  # the seeing / to see
    check("ukutya", ["uku", "tya"])  # food / to eat


def test_real_story_collisions():
    # Two more real collisions from the same story, both protected via
    # WORD_EXCEPTIONS -- see rules.py for the exact mechanism.
    check("Kudala", ["Kudala"])  # "long ago" -- NOT ku(cl.15/17 concord)+dal(create)+a
    check("kudala", ["kudala"])
    check("uthi", ["uthi"])  # "you say" -- NOT u(augment)+thi(seeded noun root "tree/stick")


def test_verb_noun_branch_collision_exceptions():
    # Collisions surfaced immediately after the isixhosa.click bulk
    # import (see rules.py/DESIGN.md for the exact mechanism of each) --
    # both from newly-added verb roots colliding with existing noun
    # roots on words ending in a valid terminal vowel.
    check("umqhekezi", ["umqhekezi"])  # burglar (cl.1) -- NOT u+m+qhekez(break)+i
    check("isiqhekezi", ["isiqhekezi"])  # expert breaker (cl.7) -- NOT i+si+qhekez(break)+i
    check("umthi", ["umthi"])  # tree (cl.3) -- NOT u+m+th(say)+i
    check("uluthi", ["uluthi"])  # stick (cl.11) -- NOT u+lu+th(say)+i
    check("imini", ["imini"])  # day -- NOT imi(cl.4, legitimate but wrong here)+ni("gender")
    check("kubuxoki", ["kubuxoki"])  # in lies/falsehood -- lower-confidence judgment call, see rules.py
    check("molo", ["molo"])  # hello (greeting) -- NOT m(cl.1/3, before vowel stem)+olo
    check("Molo", ["Molo"])
    check("apha", ["apha"])  # here (adverb) -- NOT a(cl.5/6 concord)+ph(give)+a
    # Seven more from the Kaikki-Xhosa bulk import round -- see rules.py
    # for the exact mechanism of each.
    check("imithi", ["imithi"])  # trees -- NOT i+mith(be pregnant)+i;
    # note this used to be a *correct* split before this round (see
    # below), now needs the exception like its singular "umthi" already did
    check("umsila", ["umsila"])  # tail -- NOT u+m+sil(brew/grind)+a
    check("msila", ["msila"])
    check("kumsila", ["kumsila"])
    check("umhlaba", ["umhlaba"])  # earth/world -- NOT u+m+hlab(stab)+a
    check("umzingeli", ["umzingeli"])  # hunter -- NOT u+m+zingel(hunt)+i
    check("ndiyazi", ["ndiyazi"])  # I know [it] -- NOT ndi+ya+z(come)+i
    check("amabi", ["amabi"])  # bad things -- NOT a+m+ab(share)+i
    check("ibambe", ["ibambe"])  # it holds -- NOT i+ba(object)+mb(dig)+e;
    # the correct reading (root "bamb", no object) also resolves on its
    # own, but search order tries the object-marker reading first
    # since both happen to succeed -- see rules.py for the general risk
    # this points at.
    check("umrhwebi", ["umrhwebi"])  # trader -- NOT u+m+rhweb(barter)+i
    check("abarhwebi", ["abarhwebi"])  # traders (plural)
    check("kubarhwebi", ["kubarhwebi"])  # to/among the traders
    # Same derivational/root families, but NOT exceptions -- these
    # correctly resolve on their own since they don't end in a valid
    # terminal vowel (verb-slot's stem resolver requires one):
    check("uqhekezo", ["u", "qhekezo"])
    # "a" and "m" are genuinely useful prefixes elsewhere -- confirm the
    # exceptions above didn't collaterally break them:
    check("adala", ["a", "dala"])  # s/he creates (cl.5/6 concord "a" + root "dal" + -a)
    check("umntu", ["um", "ntu"])  # person


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
