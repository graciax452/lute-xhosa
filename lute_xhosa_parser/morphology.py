"""
isiXhosa morpheme-splitting engine.

Forked from lute-shona's morphology.py as a starting hypothesis, per
that project's DESIGN.md section 10 forking guidance -- copied
structurally unchanged for now, not because the algorithm is assumed
correct for isiXhosa, but because it's a reasonable starting point to
test against real isiXhosa material and adjust from. Expect to revisit
every design choice below once real data is in rules.py; don't treat
this file as settled just because it happens to compile and run
(everything currently resolves to "leave whole" since every rules.py
table is empty).

Not carried over from Shona: _try_negative_have() and
_try_sati_construction() (Shona's confirmed "ha-...-na" and
"[subject]+sati" closed constructions) -- these are specific confirmed
Shona idioms, not assumed to have an isiXhosa equivalent. Add
isiXhosa-specific closed constructions here the same deliberate way
Shona's were added, once confirmed productive with fixed boundaries
(see lute-shona DESIGN.md section 7's closing paragraph for the
deciding question to ask before adding one).

Pure functions, no Lute dependency -- exercised directly by
tests/test_morphology.py without needing Lute installed.

Design: lexicon-gated stripping, not blind string-matching. A candidate
noun-class prefix or verb subject/TAM/object/extension affix is only
accepted if what remains after stripping it resolves to a known root in
NOUN_ROOT_LEXICON / VERB_ROOT_LEXICON. This avoids "overstemming" (a
documented failure mode of naive rule-based agglutinative parsing --
see lute-shona DESIGN.md section 3 for the full rationale and
precedents). The cost is lower split coverage for anything not yet in
the seed lexicons; that's accepted because a wrong split teaches wrong
grammar, which is worse than no split at all.

The verb-slot branch is tried before the noun-prefix branch because
Bantu subject concords and noun class prefixes legitimately share
surface forms -- the branch requiring more structure to succeed (a
validated root *and* a valid terminal vowel) goes first to reduce
cross-contamination between the two guesses.
"""

from typing import List, Optional

from lute_xhosa_parser.rules import (
    NOUN_CLASS_PREFIXES,
    NOUN_PREFIXES_REQUIRE_VOWEL_STEM,
    NOUN_ROOT_LEXICON,
    OBJECT_MARKERS,
    PAST_SUBJECT_PREFIXES,
    PROPER_NOUNS,
    TAM_MARKERS,
    TERMINAL_VOWELS,
    VERB_EXTENSIONS,
    VERB_ROOT_LEXICON,
    VERB_SUBJECT_PREFIXES,
    VOWELS,
    WORD_EXCEPTIONS,
)

_SUBJECT_PREFIXES_BY_LENGTH = sorted(
    set(VERB_SUBJECT_PREFIXES) | set(PAST_SUBJECT_PREFIXES), key=len, reverse=True
)
_NOUN_PREFIXES_BY_LENGTH = sorted(NOUN_CLASS_PREFIXES, key=lambda p: len(p[0]), reverse=True)
_EXTENSIONS_BY_LENGTH = sorted(VERB_EXTENSIONS, key=len, reverse=True)


def split_word(word: str) -> List[str]:
    """
    Split a single space-delimited isiXhosa word into its morphemes.

    Returns a list of substrings of `word` that concatenate back to
    `word` exactly (required by Lute's ParsedToken contract). Falls
    back to `[word]` whenever no branch produces a confident,
    lexicon-backed match.
    """
    if not word:
        return [word]

    if word[0:1].isupper() and word in PROPER_NOUNS:
        return [word]

    lword = word.lower()

    if lword in WORD_EXCEPTIONS:
        return [word]

    infinitive = _try_infinitive(word, lword)
    if infinitive is not None:
        return infinitive

    verb = _try_verb_slot(word, lword)
    if verb is not None:
        return verb

    noun = _try_noun(word, lword)
    if noun is not None:
        return noun

    return [word]


def _try_infinitive(word: str, lword: str) -> Optional[List[str]]:
    "uku- + verb root (class 15 infinitive, confirmed Oosthuysen 2.14 p.43), disambiguated from the identically-spelled class 15/17 noun/locative prefix by requiring a root-lexicon hit, same pattern as Shona's ku-."
    infinitive_prefix = "uku"
    if not lword.startswith(infinitive_prefix):
        return None
    stem_tokens = _resolve_stem(word[len(infinitive_prefix) :])
    if stem_tokens is None:
        return None
    return [word[: len(infinitive_prefix)]] + stem_tokens


def _try_verb_slot(word: str, lword: str) -> Optional[List[str]]:
    "subject prefix + optional TAM + optional object marker + resolved stem."
    for subj in _SUBJECT_PREFIXES_BY_LENGTH:
        if not lword.startswith(subj):
            continue
        subj_label = word[: len(subj)]
        after_subj = word[len(subj) :]
        lafter_subj = after_subj.lower()

        tam_matches = [t for t in TAM_MARKERS if lafter_subj.startswith(t)]
        for tam in sorted(tam_matches, key=len, reverse=True) + [None]:
            after_tam = after_subj[len(tam) :] if tam else after_subj
            lafter_tam = after_tam.lower()

            obj_matches = [o for o in OBJECT_MARKERS if lafter_tam.startswith(o)]
            for obj in sorted(obj_matches, key=len, reverse=True) + [None]:
                after_obj = after_tam[len(obj) :] if obj else after_tam
                stem_tokens = _resolve_stem(after_obj)
                if stem_tokens is None:
                    continue
                tokens = [subj_label]
                if tam:
                    tokens.append(after_subj[: len(tam)])
                if obj:
                    tokens.append(after_tam[: len(obj)])
                tokens.extend(stem_tokens)
                return tokens
    return None


def _try_noun(word: str, lword: str) -> Optional[List[str]]:
    """
    longest-matching noun class prefix, gated on the remaining stem
    being a known root. A handful of prefixes (NOUN_PREFIXES_REQUIRE_VOWEL_STEM)
    are only valid before a vowel-initial stem -- enforced explicitly,
    since without it a coincidental lexicon hit for the wrong reading
    (e.g. "ub-" + "huti" for "ubhuti", when the correct split is "u-" +
    "bhuti") would win purely by being the longer candidate. See
    rules.py for how this was found.
    """
    for prefix, _class_id in _NOUN_PREFIXES_BY_LENGTH:
        if not lword.startswith(prefix):
            continue
        stem = word[len(prefix) :]
        if not stem:
            continue
        if prefix in NOUN_PREFIXES_REQUIRE_VOWEL_STEM and stem[0].lower() not in VOWELS:
            continue
        if stem.lower() in NOUN_ROOT_LEXICON:
            return [word[: len(prefix)], stem]
    return None


def _resolve_stem(remainder: str) -> Optional[List[str]]:
    """
    Resolve a verb stem (root + optional extensions + terminal vowel).

    Tries direct root match first, then one stripped extension, then
    two (capped -- see lute-shona DESIGN.md section 6 for why depth 2
    and why direct-match-first matters, with the kuisa/kuiswa/kuisiswa
    worked example). The terminal vowel is never emitted as its own
    token -- merged onto whichever morpheme ends up last.
    """
    if len(remainder) < 2:
        return None
    lremainder = remainder.lower()
    if lremainder[-1] not in TERMINAL_VOWELS:
        return None

    tv = remainder[-1]
    body = lremainder[:-1]
    orig_body = remainder[:-1]

    if body in VERB_ROOT_LEXICON:
        return [orig_body + tv]

    for ext in _EXTENSIONS_BY_LENGTH:
        if not body.endswith(ext):
            continue
        root = body[: -len(ext)]
        if root and root in VERB_ROOT_LEXICON:
            orig_root = orig_body[: len(root)]
            orig_ext = orig_body[len(root) :]
            return [orig_root, orig_ext + tv]

    for ext1 in _EXTENSIONS_BY_LENGTH:
        if not body.endswith(ext1):
            continue
        mid = body[: -len(ext1)]
        for ext2 in _EXTENSIONS_BY_LENGTH:
            if not mid.endswith(ext2):
                continue
            root = mid[: -len(ext2)]
            if root and root in VERB_ROOT_LEXICON:
                orig_root = orig_body[: len(root)]
                orig_ext2 = orig_body[len(root) : len(root) + len(ext2)]
                orig_ext1 = orig_body[len(root) + len(ext2) :]
                return [orig_root, orig_ext2, orig_ext1 + tv]

    return None
