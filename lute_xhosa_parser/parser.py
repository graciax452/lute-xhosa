"""
Parsing for isiXhosa.

Forked from lute-shona's parser.py (see that project's DESIGN.md
section 10). isiXhosa is space-delimited (like Shona and English), so
word *boundaries* are already handled correctly by Lute's
SpaceDelimitedParser -- click consonants (c, q, x, and their digraph/
trigraph combinations) are just letters within a word, not separate
tokens, so this doesn't change the tokenizing story at all. What's
missing is morphology: a single space-delimited isiXhosa word is often
several grammatical morphemes glued together, all packed into one
unclickable token. XhosaParser subclasses SpaceDelimitedParser (same
pattern as Lute's own TurkishParser, and as lute-shona's ShonaParser)
and overrides parse_para() so each matched word is run through the
morphology engine and emitted as one ParsedToken per morpheme instead
of one token for the whole inflected word.

Includes classes:

- XhosaParser
"""

import re
from typing import List

from lute.parse.base import ParsedToken
from lute.parse.space_delimited_parser import SpaceDelimitedParser

from lute_xhosa_parser.morphology import split_word


class XhosaParser(SpaceDelimitedParser):
    """
    isiXhosa parser: space-delimited word boundaries (inherited), plus
    a lexicon-gated rule-based morpheme splitter on top of each word.
    """

    @classmethod
    def name(cls):
        return "isiXhosa"

    def parse_para(self, text: str, lang, tokens: List[ParsedToken]):
        """
        Parse a string, appending the tokens to the list of tokens.

        Mirrors SpaceDelimitedParser.parse_para (see that method for
        the canonical version this is based on) -- identical word-
        boundary/punctuation/end-of-sentence handling, except each
        matched word is split into morphemes via split_word() and
        emitted as multiple ParsedTokens instead of one.
        """
        termchar = lang.word_characters.strip()
        if not termchar:
            termchar = SpaceDelimitedParser.get_default_word_characters()

        splitex = lang.exceptions_split_sentences.replace(".", "\\.")
        pattern = rf"({splitex}|[{termchar}]*)"
        if splitex.strip() == "":
            pattern = rf"([{termchar}]*)"

        m = self.preg_match_capture(pattern, text)
        wordtoks = list(filter(lambda t: t[0] != "", m))

        def add_non_words(s):
            if not s:
                return
            splitchar = lang.regexp_split_sentences.strip()
            if not splitchar:
                splitchar = SpaceDelimitedParser.get_default_regexp_split_sentences()
            pattern = f"[{re.escape(splitchar)}]"
            has_eos = False
            if pattern != "[]":
                allmatches = self.preg_match_capture(pattern, s)
                has_eos = len(allmatches) > 0
            tokens.append(ParsedToken(s, False, has_eos))

        pos = 0
        for wt in wordtoks:
            w = wt[0]
            wp = wt[1]
            s = text[pos:wp]
            add_non_words(s)
            for morpheme in split_word(w):
                tokens.append(ParsedToken(morpheme, True, False))
            pos = wp + len(w)

        s = text[pos:]
        add_non_words(s)
