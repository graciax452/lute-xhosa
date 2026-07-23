# isiXhosa dataset search notes

Working reference for growing `NOUN_ROOT_LEXICON`/`VERB_ROOT_LEXICON`.
Purpose: avoid re-checking sources that already turned out to be
unusable, and know what's still an open lead. Update this file as new
sources are checked — status markers:

- ✅ Used — merged into `rules.py`, see `DESIGN.md` for the extraction writeup.
- ⚠️ Real, not directly usable — exists and is legitimately licensed, but wrong shape (e.g. sentence pairs, not a lexicon) or needs work we haven't done.
- 🆕 Found, not yet checked — a real lead, but not downloaded/verified yet.
- ❓ Unverified — mentioned somewhere, never actually checked in this project.
- ❌ Rejected — checked and ruled out; the notes column says why, so it doesn't get re-suggested.

| Source | Format / Size | License | Status | Notes |
|---|---|---|---|---|
| **isixhosa.click** (`IsiXhosa-click/database`, GitHub) | CSV (`words.csv`), 2,336 entries | CC BY-SA 4.0 | ✅ Used | UCT/SADiLaR-backed. Primary source so far — took nouns 30→695, verbs 9→405. |
| **Kaikki.org isiXhosa Wiktionary extract** (`kaikki.org/dictionary/Xhosa/`) | JSONL, 3,371 distinct words | not stated on the page (Wiktionary content is CC BY-SA per Wiktionary's own terms, same basis as the Shona extract) | ✅ Used | Took nouns 695→1,740 and verbs 405→1,079 — the biggest single jump so far, roughly 2.5x. Reused isixhosa.click's exact extraction method (try every prefix regardless of label). Also the riskiest round so far: re-testing the two validation stories afterward found 12 new collisions (vs. 2 from the earlier isixhosa.click round) — see `DESIGN.md`. Given the scale, this almost certainly still has more lurking than the two saved stories could surface; treat as **needs more real-text testing**, not "done." |
| **NCHLT isiXhosa Text Corpora** (SADiLaR repo, `repo.sadilar.org`) | unstated format — description explicitly mentions "lexicon, frequency list, named-entity lists" | requires accepting SADiLaR's per-resource terms of use; not yet confirmed how permissive | 🆕 Found, not yet checked | Same government/academic body (SADiLaR) that backed isixhosa.click. Explicitly includes a lexicon + frequency list — the right shape — but the click-through terms haven't been read and nothing's been downloaded yet. |
| **PanLex** (`panlex.org`) | SQLite/CSV/JSON, full multi-GB global dump | CC0 | ⚠️ Real, unassessed | Huge; would need the isiXhosa slice pulled out and quality-checked. No isiXhosa-specific work done yet. |
| **NCHLT isiXhosa Speech Corpus / NE-annotated corpus** (SADiLaR) | audio / NER-tagged text | SADiLaR terms | ❌ Wrong data type | Speech and named-entity data, not a general lexicon. |
| **WAXAL** | audio/documentation project | unknown | ❓ Not checked | Mentioned in a pasted source list; real West African language documentation initiative, but Xhosa coverage and any downloadable lexicon format haven't been confirmed. |
| **AFLAT** | — | — | ❌ Not a dataset | African-language-technology community/conference, not a data source itself. |
| **Archive.org English-Xhosa dictionary** | scanned book | copyrighted scan | ❌ Not tabular | Same problem as Hannan's Shona dictionary — page images, not extractable text, unless OCR'd. |
| **Masakhane dataset family** (MasakhaNER, MasakhaPOS, etc.) | various, HuggingFace | mostly CC-BY / open | ❓ Not checked for Xhosa specifically | Real, legitimate project covering many African languages including Xhosa, but which specific dataset (if any) is a lexicon vs. NER/POS-tagged running text hasn't been checked. |
| **VaShona.com "Project Lexicon Hub"** (claimed 100k+ words) | web dictionary | proprietary | ❌ Rejected | This is a Shona site, not Xhosa — was misfiled into a pasted "Xhosa resources" list. Real site, but explicitly "all rights reserved, do not distribute," no bulk export. Listed here only so it doesn't get re-suggested as an Xhosa source. |

## Biggest open lead

**NCHLT isiXhosa Text Corpora** via SADiLaR — explicitly says it has a
lexicon and frequency list; needs someone to actually read the terms
of use and download it to see what's really there. Given how many
collisions the Kaikki-Xhosa round just surfaced, prioritize *testing
real text against the current lexicon* over adding another bulk source
immediately — more data isn't the bottleneck right now, verification is.
