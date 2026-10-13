---
name: humanize-text
description: Rewrite AI-generated or AI-assisted text so it reads like a real person wrote it — Russian or English — and verify the result with real open AI detectors instead of guessing. Use whenever the user asks to humanize / очеловечить / "make it not sound like ChatGPT", to remove AI tells, to pass or avoid AI detectors (GPTZero, Turnitin, Pangram, Originality, «Антиплагиат», GigaCheck, Яндекс Нейродетектор, Text.ru), to match their own writing voice, or when an essay, post, review, letter, article or bio "sounds like AI" — even if they never say "humanize". Built on measurements of ~38k human vs AI texts (Sber's LLMTrace corpus, 30+ models) plus published research; ships a scanner, a voice fingerprint tool and a local detector panel for a rewrite-measure loop.
---

# Humanize text

Most "humanizers" swap words and delete em dashes. That does not work against modern detectors,
and the evidence is clear:

- Strong classifiers (Pangram, GPTZero, Turnitin, GigaCheck, «Антиплагиат») read the whole voice —
  rhythm, syntax, stance, specificity. A Claude text went from 94% AI to **100%** AI on Pangram after
  its dashes and "AI phrases" were removed (LessWrong, 2026).
- Detectors normalise typography before reading: every dash becomes "-", every quote `"`, `ё`→`е`,
  markdown and invisible characters are stripped. Dash and quote tricks are invisible to them.
- What did beat a strong classifier: **the voice of a real author** (samples + a human-written opening)
  and **iterating against a detector** with feedback.

So this skill works on what actually separates the two distributions, measured on ~38k texts in
the same genres (see `references/russian.md`, `references/english.md`):

| Signal (AI vs human) | Russian | English |
|---|---|---|
| Sentence-length variation (CV) — strongest in RU | 0.38 vs **0.55** | 0.37 vs **0.48** |
| Very short sentences (≤6 words) | 9% vs **19%** | 4% vs **7%** |
| Nominalizations per 1000 words | **52** vs 32 | **46** vs 26 |
| Average word length (letters) | **6.0** vs 5.6 | **5.3** vs 4.7 |
| I/we per 1000 words | 13 vs **17** | 10 vs **22** |
| Numbers per 1000 words | 19 vs **31** | 13 vs **26** |
| Brackets per 1000 words | 2.9 vs **8.2** | 2.9 vs **5.9** |
| Em dash | ≈ same (5.5 vs 5.1) — **not a Russian tell** | weak (1.9 vs 1.0) |
| Template phrases | «подчёркивает важность» 178 : 0 texts | "a testament to" 688 : 2 texts |

## Workflow

### 1. Intake — ask only for what's missing, in one short message
- **Language, genre, reader** (essay, post, review, email, article, bio…) and the required length.
- **Samples of the author's own writing** (messages, old texts; 300+ words). The single strongest lever.
- **The real specifics**: facts, numbers, names, places, what they did or think, an example only they
  would pick. Never invent these — invented specifics are what teachers and reviewers check first.
If the user just wants it done, proceed with what you have and say what would make it better.

### 2. Diagnose
```bash
python3 <skill>/scripts/scan.py source.txt            # why it reads as machine text, with locations
python3 <skill>/scripts/voice.py my_old_texts.txt     # the author's voice card (if samples exist)
python3 <skill>/scripts/detect.py source.txt          # baseline from local detectors (optional, heavier)
```

### 3. Rewrite — from content, not sentence by sentence
Extract the content (claims, facts, examples), then write it again in the target voice. A
sentence-by-sentence paraphrase keeps the model's structure, which is what classifiers see.
Follow `references/playbook.md` in this order — earlier moves change the distribution most:
1. **Content**: put in the author's specifics and position; cut significance inflation and summaries.
2. **Voice**: match the voice card (rhythm range, punctuation habits, openers, connectors, person).
3. **Structure**: start with the point; unequal paragraphs; no three-of-everything; no tidy ending.
4. **Rhythm**: mix very short and long sentences; target the human CV band in the table above.
5. **Syntax**: verbs instead of nouns; cut "-ing" tails and participle chains; is/are not "serves as".
6. **Words**: remove AI-favoured words that `scan.py` lists; repeat plain words; shorter words.
7. **Stance**: one opinion; hedge only where unsure; no reassurance, no moral, no rhetorical Q+A.
8. **Format**: no markdown or bold in prose; punctuation that fits the genre (see language files).

### 4. Measure and iterate (2–4 rounds)
Run `scan.py` and `detect.py` on the draft. Fix the **strongest remaining signal** each round, not
everything at once. If "style" is clean but "structure" still says machine, the problem is rhythm,
nominal style, person or specifics — not words. If `scan.py` already says human but a detector still
flags the text, it is usually **too tidy for its genre**: read 2–3 real human texts of the same genre
(the user's own, or real reviews/posts/articles) and match their texture — asides in brackets, how
they punctuate, what small details they mention, how unevenly they build paragraphs. In our test this
took a restaurant review from 0.83 to 0.006 on the classifier that still caught it. If detectors still
flag it after four rounds, go back to steps 1–3 (voice and content), not to synonyms.

Done when: both scan scores are in the human range, the local detectors say human, every fact matches
the source, and the text sounds like the author in this genre.

### 5. Hand over
Give the text, then 3–5 lines: what changed and why, before/after scores, and anything the author
should add or check (a fact, a personal example). Be precise about limits (below).

## Hard rules
- **No fabrication**: no invented experiences, quotes, numbers, sources or credentials.
- **No tricks**: homoglyphs, zero-width characters, deliberate typos, random synonym swaps, odd
  spacing. Detectors normalise them, Turnitin and GPTZero are trained to catch them, and they damage
  the text.
- **Keep the meaning** and the author's claims; don't add opinions the author doesn't hold.
- **Be honest about guarantees.** Nobody can promise "no detector will ever flag it": providers can
  watermark (Google SynthID) or keep logs, commercial detectors retrain on new humanizer output, and
  every detector errs on short texts (< ~200 words) in both directions. Promise what you measured.
- Where a school, journal or employer requires disclosing AI use, this skill doesn't change that —
  say so once if the user mentions such a context, then help them edit their own draft.

## Tools
- `scripts/scan.py FILE [--voice SAMPLE]` — measurements vs human norms, AI-favoured words in context,
  structural patterns, two transparent scores (held-out AUC: style RU 0.92 / EN 0.95). No dependencies;
  `pip install pymorphy3 razdel` improves Russian.
- `scripts/voice.py SAMPLE...` — the author's voice card.
- `scripts/detect.py FILE` — local detector panel: two Russian classifiers trained on Sber's LLMTrace
  (held-out AUC 1.00 and 0.98) and the top open English classifier on RAID (desklib DeBERTa-v3, AUC 0.95,
  but it flags ~18% of human texts — read 0.5–0.7 as uncertain). `--binoculars` adds a weak zero-shot
  check. Russian needs `pip install onnxruntime tokenizers huggingface_hub` (~75 MB of models); English
  also `torch transformers sentencepiece protobuf safetensors` (~1.7 GB). Calibration: `data/calibration.json`.
  Passing this panel means no obvious machine signal left — not a guarantee for commercial detectors.

## References
- `references/playbook.md` — every rewriting move with the reason and RU/EN before/after examples. **Read before rewriting.**
- `references/russian.md` — Russian measurements, 160 overused words/phrases with ratios, what humans write instead, register notes, template table.
- `references/english.md` — English measurements + Kobak (Science Advances 2025), Reinhart (PNAS 2025), Wikipedia "Signs of AI writing" by era, Pangram on Claude.
- `references/detectors.md` — how each detector family works, what moves it, what doesn't, the evidence.
- `references/sources.md` — all sources with links.
