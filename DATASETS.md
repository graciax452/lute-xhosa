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
| **NCHLT isiXhosa Text Corpora** (SADiLaR repo, `repo.sadilar.org/items/f10a5b51-cfbe-460b-b7a7-9f1ad4c502d2`) | zip, 13.8MB, 2,779 files (raw source docs + processed corpora + a `3.Lexica/` folder) | **CC BY 2.5 South Africa** (confirmed on the item page), no login/registration needed to download | ✅ Used (as a validation corpus, not a lexicon source) | Downloaded and inspected directly. Correction to the earlier entry: the "lexicon" component (`FREQ.LEX.NCHLT.xh.txt`) is a **frequency list of raw surface forms** (`word<TAB>count`, 42,874 unique real-world words from government/legal documents), not root/class-tagged entries like Kaikki or isixhosa.click — it can't feed `NOUN_ROOT_LEXICON`/`VERB_ROOT_LEXICON` directly the same way. What it's genuinely excellent for: **the largest real-text validation corpus available by far** (42,874 unique words vs. the two saved stories' combined ~540). Ran it through `split_word()`: 8,380 words (19.5%) split, sanity-checked a sample of the top 50 highest-frequency splits (`ukuba`→uku+ba, `abantu`→aba+ntu, `umhlaba`→um+hlaba, etc.) — all correct. The highest-frequency *unresolved* words are almost entirely closed-class function words (`okanye`="or", `kunye`="together/with", `xa`="when/if", `kwaye`="and", `kodwa`="but"...) — a different, smaller gap (particle/conjunction tables) than the open-class noun/verb root lexicons this project has been growing, not pursued this round. |
| **PanLex** (`panlex.org`) | SQLite/CSV/JSON, full multi-GB global dump | **CC BY-NC-SA 4.0** — corrected: a pasted source claimed CC0; the actual license page says "Attribution-NonCommercial-ShareAlike," commercial use needs written permission. Fine for this noncommercial project, different claim than stated. | ⚠️ Real, unassessed | Huge; would need the isiXhosa slice pulled out and quality-checked. No isiXhosa-specific work done yet. |
| **African Wordnet — isiXhosa** (SADiLaR repo, `repo.sadilar.org`) | XML, via SADiLaR repository or the Lexonomy browsing interface | **CC BY 4.0** (confirmed via search of sadilar.org/africanwordnet.wordpress.com) | 🆕 Found, confirmed real, not yet downloaded | isiXhosa was one of the *original four* languages when this project started in 2010 (with isiZulu, Setswana, Sesotho sa Leboa), not an afterthought — genuinely promising. Exact item URL/download link not yet located (only found the isiZulu item page directly; isiXhosa's should be a sibling item on the same repo). Worth checking next — WordNet entries are inherently headwords/lemmas, which is closer to the shape this project needs than the NCHLT frequency list. |
| **Wikidata Lexemes for isiXhosa** (SPARQL query, `wd:Q13218`) | JSON/CSV via SPARQL | CC0 | ❌ Real infrastructure, no actual data | A pasted source rated this "High" suitability. Ran the actual query directly against Wikidata: **7 lexeme entries total**. Same near-empty result as Shona's equivalent check (3 entries) — not worth building a pipeline around either language's Wikidata lexemes. |
| **NCHLT isiXhosa Speech Corpus / NE-annotated corpus** (SADiLaR) | audio / NER-tagged text | SADiLaR terms | ❌ Wrong data type | Speech and named-entity data, not a general lexicon. |
| **Vuk'uzenzele / Gov-ZA multilingual corpora** (`github.com/dsfsi/vukuzenzele-nlp`, Zenodo 7635168) | CSV/JSON, aligned multilingual government-publication sentences, isiXhosa included | stated as open (not yet independently confirmed) | ❓ Not checked | Real-sounding, plausible (South African government multilingual publishing is a known real corpus source), but not independently verified this session — same "sentence corpus, not lexicon" shape as OPUS-MT560, useful only as more validation text if pursued. |
| **Lwazi ASR corpus / ViXSD** (HuggingFace) | speech + transcripts | unstated | ❌ Wrong data type | Speech data. Only relevant for a future pronunciation feature, not lexicon growth. |
| **CLDF / Lexibank (Nguni branch)**, **CTexT NCHLT Lemmatizer & POS Dictionaries**, **Bantu LexiCausal Database** | various | various, unconfirmed | ❓ Not checked | Real-sounding infrastructure/institutions (MPI-EVA/CLLD for Lexibank, CTexT/North-West University for the lemmatizer), but none independently verified this session — check before trusting claimed sizes/formats, same as everything else on this list. |
| **WAXAL** | audio/documentation project | unknown | ❓ Not checked | Mentioned in a pasted source list; real West African language documentation initiative, but Xhosa coverage and any downloadable lexicon format haven't been confirmed. |
| **AFLAT** | — | — | ❌ Not a dataset | African-language-technology community/conference, not a data source itself. |
| **Archive.org English-Xhosa dictionary** | scanned book | copyrighted scan | ❌ Not tabular | Same problem as Hannan's Shona dictionary — page images, not extractable text, unless OCR'd. |
| **Masakhane dataset family** (MasakhaNER, MasakhaPOS, etc.) | various, HuggingFace | mostly CC-BY / open | ❓ Not checked for Xhosa specifically | Real, legitimate project covering many African languages including Xhosa, but which specific dataset (if any) is a lexicon vs. NER/POS-tagged running text hasn't been checked. |
| **VaShona.com "Project Lexicon Hub"** (claimed 100k+ words) | web dictionary | proprietary | ❌ Rejected | This is a Shona site, not Xhosa — was misfiled into a pasted "Xhosa resources" list. Real site, but explicitly "all rights reserved, do not distribute," no bulk export. Listed here only so it doesn't get re-suggested as an Xhosa source. |

## Biggest open leads

1. **African Wordnet — isiXhosa** (SADiLaR/CC BY 4.0) — confirmed real
   and genuinely lexicon-shaped (headwords, not raw frequency), unlike
   NCHLT. Find the exact isiXhosa item page and check its actual XML
   structure before assuming it slots in cleanly.
2. Re-running `scripts/check_collisions.py` and the NCHLT frequency-list
   validation after any future lexicon growth — the NCHLT list is now
   the standing large-scale validation corpus; consider saving a
   filtered version (e.g. top N unresolved words) for repeatable use.

## A note on this round's research quality

Same lesson as the Shona side: Wikidata's isiXhosa lexeme count was
rated "High" while actually being 7 entries, and PanLex's license was
again mis-stated as CC0. But NCHLT's actual content also turned out to
differ from what every prior round (including this project's own
earlier notes) assumed — "lexicon" in the resource description meant a
frequency list of inflected surface forms, not root-tagged entries.
Worth remembering: even a source that's real, correctly licensed, and
directly downloaded still needs its *actual file contents* opened and
inspected before its shape can be trusted, not just its description.
