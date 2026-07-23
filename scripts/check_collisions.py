"""
Automated collision detector for lute_xhosa_parser's lexicons.

Scans for words where the verb-slot branch (subject + optional TAM +
optional object + a VERB_ROOT_LEXICON root + terminal vowel) produces
a surface string that exactly matches a noun-slot surface string
(a NOUN_CLASS_PREFIXES prefix + a NOUN_ROOT_LEXICON root). Since
_try_verb_slot always runs before _try_noun in morphology.py, any such
match is a real collision: the noun reading would never be reached.

This exists because relying only on real-text validation (the two
saved stories) means a collision only gets found if the specific
colliding word happens to appear in whatever text was tested -- fine
for catching common words, but it can't prove there ISN'T a rarer
collision sitting unnoticed in the lexicon. This script instead
enumerates the full closed combinatorial space (every subject x every
optional TAM x every optional object x every terminal vowel x every
verb root) and checks each one against every noun surface form
directly, which is exhaustive within that space rather than sample-
based.

Run with: python scripts/check_collisions.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lute_xhosa_parser.rules import (
    NOUN_CLASS_PREFIXES,
    NOUN_PREFIXES_REQUIRE_VOWEL_STEM,
    NOUN_ROOT_LEXICON,
    OBJECT_MARKERS,
    PAST_SUBJECT_PREFIXES,
    TAM_MARKERS,
    TERMINAL_VOWELS,
    VERB_ROOT_LEXICON,
    VERB_SUBJECT_PREFIXES,
    VOWELS,
    WORD_EXCEPTIONS,
)
from lute_xhosa_parser.morphology import split_word


def build_noun_surface_index():
    """word -> list of (prefix, root) pairs that produce it."""
    index = {}
    for prefix, _cls in NOUN_CLASS_PREFIXES:
        for root in NOUN_ROOT_LEXICON:
            if prefix in NOUN_PREFIXES_REQUIRE_VOWEL_STEM and (not root or root[0] not in VOWELS):
                continue
            word = prefix + root
            index.setdefault(word, []).append((prefix, root))
    return index


def find_collisions():
    noun_index = build_noun_surface_index()
    subjects = sorted(set(VERB_SUBJECT_PREFIXES) | set(PAST_SUBJECT_PREFIXES))
    tams = [None] + sorted(TAM_MARKERS)
    objs = [None] + sorted(OBJECT_MARKERS)

    collisions = []
    for subj in subjects:
        for tam in tams:
            for obj in objs:
                prefix_part = subj + (tam or "") + (obj or "")
                for root in VERB_ROOT_LEXICON:
                    for tv in TERMINAL_VOWELS:
                        word = prefix_part + root + tv
                        if word in WORD_EXCEPTIONS:
                            continue
                        if word in noun_index:
                            collisions.append(
                                {
                                    "word": word,
                                    "verb_analysis": (subj, tam, obj, root, tv),
                                    "noun_analyses": noun_index[word],
                                }
                            )
    return collisions


def main():
    collisions = find_collisions()
    seen = {}
    for c in collisions:
        seen.setdefault(c["word"], c)
    collisions = sorted(seen.values(), key=lambda c: c["word"])

    print(f"Scanned {len(VERB_SUBJECT_PREFIXES) + len(PAST_SUBJECT_PREFIXES)} subjects x "
          f"{len(TAM_MARKERS) + 1} TAM options x {len(OBJECT_MARKERS) + 1} object options x "
          f"{len(VERB_ROOT_LEXICON)} verb roots x {len(TERMINAL_VOWELS)} terminal vowels.")
    print(f"{len(collisions)} words have BOTH a valid verb-slot reading and a valid "
          f"noun reading (WORD_EXCEPTIONS entries already excluded).\n")

    # Now check what split_word() actually returns for each -- the
    # verb/noun token-count preference in morphology.py's split_word()
    # already resolves the cases where noun has fewer tokens; only the
    # remainder (still resolving to the verb reading, either because
    # verb has fewer/equal tokens, or a tie) are still open questions.
    resolved_correctly = []
    still_verb = []
    for c in collisions:
        actual = split_word(c["word"])
        subj, tam, obj, root, tv = c["verb_analysis"]
        verb_tokens = [subj]
        if tam:
            verb_tokens.append(tam)
        if obj:
            verb_tokens.append(obj)
        verb_tokens.append(root + tv)
        if actual == verb_tokens:
            still_verb.append((c, actual))
        else:
            resolved_correctly.append(c)

    print(f"Already resolved correctly by the token-count preference: {len(resolved_correctly)}")
    print(f"Still resolving to the verb reading (token-count tie, both branches produce "
          f"2 tokens): {len(still_verb)}\n")

    # Among the ties, split further: does the verb reading's token
    # boundary happen to be IDENTICAL to any valid noun reading's
    # boundary (harmless -- same clickable split either way, doesn't
    # matter which branch "won") vs genuinely DIFFERENT boundaries
    # (a real ambiguity, needs individual judgment).
    harmless_ties = []
    real_ties = []
    for c, actual in still_verb:
        noun_token_sets = [[p, r] for p, r in c["noun_analyses"]]
        if actual in noun_token_sets:
            harmless_ties.append((c, actual))
        else:
            real_ties.append((c, actual))

    print(f"  Of which harmless (verb boundary == some valid noun boundary, doesn't matter "
          f"which branch won): {len(harmless_ties)}")
    print(f"  Of which genuinely conflicting boundaries (real, unresolved ambiguity): {len(real_ties)}\n")

    print("--- Genuinely conflicting ties (sample, first 40) ---")
    for c, actual in real_ties[:40]:
        subj, tam, obj, root, tv = c["verb_analysis"]
        verb_str = f"{subj}+{root}+{tv}"
        noun_str = " / ".join(f"{p}+{r}" for p, r in c["noun_analyses"])
        print(f"{c['word']!r}: verb [{verb_str}] -> actual {actual}, noun would be [{noun_str}]")

    return len(real_ties)


if __name__ == "__main__":
    n = main()
    sys.exit(1 if n else 0)
