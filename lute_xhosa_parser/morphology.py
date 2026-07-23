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
    noun = _try_noun(word, lword)

    if verb is not None and noun is not None:
        # Both branches independently resolved -- prefer whichever
        # analysis has fewer tokens (fewer morphemes guessed), the same
        # "shallowest wins" principle _resolve_stem and _try_verb_slot
        # already apply within their own search, extended here across
        # the verb/noun branch split itself. This specifically fixes
        # the systematic case where "a"(cl.5/6 subject)+"ba"(cl.2
        # object) as a verb-slot reading happens to spell out exactly
        # the extremely common "aba-" class-2 noun prefix: any
        # deverbal/agentive noun (root+"i", a fully productive Bantu
        # pattern -- "X-i" from any verb root "-X-" means "one who
        # Xs") was silently unreachable via the noun branch, since the
        # verb branch (tried first, for the usual reason -- see this
        # function's docstring) always resolved to a 3-token subject+
        # object+root reading before the noun branch's simpler 2-token
        # prefix+root reading ever got a chance. Found via
        # scripts/check_collisions.py, which exhaustively checks the
        # whole subject x TAM x object x root x terminal-vowel space
        # against the noun lexicon rather than relying only on
        # real-text sampling -- see that script's docstring.
        if len(noun) < len(verb):
            return noun
        if len(noun) == len(verb):
            # Equal token count -- most of these are harmless (the two
            # analyses happen to land on the identical boundary anyway,
            # e.g. subject "ba" == bare cl.2 noun prefix "ba", same
            # split either way). Where they genuinely conflict, prefer
            # whichever analysis's first token (the matched affix) is
            # longer: a longer match is inherently less likely to be
            # coincidental than a short one, the same reasoning
            # _try_noun already uses to try longer prefixes before
            # shorter ones. This resolves the entire remaining set
            # found by scripts/check_collisions.py after the token-
            # count preference above (e.g. "abanga" -- noun "aba"+"nga"
            # wins over verb "a"+"banga", since "aba" is a much more
            # specific match than the bare 1-letter subject "a").
            if len(noun[0]) > len(verb[0]):
                return noun
        return verb

    if verb is not None:
        return verb

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
    """
    Subject prefix + optional TAM + optional object marker + resolved
    stem. Candidates are tried shallowest-first: no TAM/no object
    before either optional slot is consumed, one optional slot before
    both. This is the same "least-stripped match wins" principle
    _resolve_stem already applies to extensions (see its docstring),
    extended here to the TAM/object slots.

    This matters because the old nested-loop order (tam candidates
    outer, obj candidates inner, both trying real matches before None)
    was actually biased toward consuming *more* optional structure, not
    less -- when a word had *both* a valid "consume this object marker"
    reading and a valid "don't" reading, the old order always picked
    the one that consumed more, even when that was wrong. Found via
    "ibambe" ("it holds," from -bamba-, root "bamb"): the old order
    picked i+ba(object "them")+mb(root "-mba-", "to dig")+e over the
    correct i+bambe (root "bamb", no object) purely because the
    object-marker candidate was tried first -- see rules.py's
    WORD_EXCEPTIONS entry for the fix-at-data-level half of this; this
    is the fix-at-code-level half, for any future instance of the same
    pattern.
    """
    for subj in _SUBJECT_PREFIXES_BY_LENGTH:
        if not lword.startswith(subj):
            continue
        subj_label = word[: len(subj)]
        after_subj = word[len(subj) :]
        lafter_subj = after_subj.lower()

        tam_matches = sorted((t for t in TAM_MARKERS if lafter_subj.startswith(t)), key=len, reverse=True)

        # Priority-ordered (tam, obj) candidates: fewest optional slots
        # consumed first; ties (same number of slots consumed) broken
        # by longest match, TAM-only before object-only at depth 1
        # (arbitrary but deterministic -- no case has needed the
        # opposite tie-break yet).
        candidates = [(None, None)]
        obj_matches_no_tam = sorted((o for o in OBJECT_MARKERS if lafter_subj.startswith(o)), key=len, reverse=True)
        candidates += [(None, obj) for obj in obj_matches_no_tam]
        candidates += [(tam, None) for tam in tam_matches]
        for tam in tam_matches:
            after_tam = after_subj[len(tam) :]
            lafter_tam = after_tam.lower()
            obj_matches = sorted((o for o in OBJECT_MARKERS if lafter_tam.startswith(o)), key=len, reverse=True)
            candidates += [(tam, obj) for obj in obj_matches]

        for tam, obj in candidates:
            after_tam = after_subj[len(tam) :] if tam else after_subj
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
