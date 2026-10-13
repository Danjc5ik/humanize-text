# How AI-text detectors work — and what actually moves them

Read this before promising anyone anything. Sources are in `sources.md`.

## Three families of detectors

| Family | Examples | What it looks at | What moves it |
|---|---|---|---|
| **Trained classifiers** (most products today) | Pangram, GPTZero (since autumn 2023), Turnitin, Originality.ai, Copyleaks, GigaCheck (Sber), «Антиплагиат», Яндекс Нейродетектор, Текст.ру; open: desklib DeBERTa, RuModernBERT detectors | A neural network trained on millions of paired human/AI texts learns the whole "voice": word choice, syntax, rhythm, stance, structure — hundreds of thousands of weak signals at once | Deep rewriting of voice and structure; a real author's style and content. Surface swaps barely move strong ones |
| **Zero-shot statistics** | perplexity/burstiness (early GPTZero), DetectGPT, Fast-DetectGPT, **Binoculars** (ICML 2024), GPT-who (information density) | How predictable each token is for a language model, and how evenly that predictability is spread | Less predictable but still natural word choice; uneven information density; varied rhythm |
| **Watermarks** | Google SynthID-Text (in Gemini since 2024, Nature 2024); OpenAI built one but did not ship it | A secret statistical bias in token choice, checkable only by the provider | Paraphrasing, translation and heavy editing break it (detection "drops sharply even under light paraphrasing") |

Plus **retrieval**: a provider can keep its own outputs and look for near-copies (Krishna et al. 2023 proposed this as the defense against paraphrase). Rewriting the ideas in new words beats it; light edits do not.

## What the evidence says

- **Surface edits don't fool good classifiers.** On LessWrong (2026) a Claude-written dialogue scored 94% AI on Pangram; replacing em dashes gave 83%; removing "AI phrases" gave **100%**. Claude "has difficulty escaping its characteristic voice."
- **What did work there:** (1) iterative rewriting with the detector's feedback (63% → 20% → 0% AI); (2) giving the model real samples of a human author and a human-written opening — the middle passage scored 100% human.
- **Modern classifiers normalise typography before reading.** The open Russian detectors trained on Sber's LLMTrace map every dash to "-", every quote to `"`, `ё`→`е`, `…`→`...`, strip markdown, invisible characters and soft hyphens. So "replace the em dash", zero-width spaces and homoglyphs are literally invisible to them.
- **Character tricks are an attack signature.** RAID (ACL 2024) tested homoglyphs, zero-width spaces, misspellings, whitespace, synonym swaps: weak detectors break, but such text is trivially normalised, and Turnitin (Aug 2025) trained a dedicated "AI bypasser" detector on the output of popular humanizer tools. Never use them.
- **Humanizer tools mostly fail against the strongest detector.** NBER/BFI study (Jabarian & Imas 2025): Pangram kept near-zero false negatives on StealthGPT-humanized text; GPTZero missed 50%+. Independent tests: QuillBot output stayed flagged in 15 of 18 runs.
- **Paraphrasing does break many detectors.** DIPPER (NeurIPS 2023) dropped DetectGPT from 70.3% to 4.6% detection at 1% FPR. Statistical detectors are fragile; trained ones less so.
- **Length matters.** Pangram is unreliable under ~200 words; a 2026 Habr test of Yandex, GigaCheck, Text.ru and GPTZero on Russian found many errors at 25–35 and 90–110 words, almost none at 220–260.
- **Detectors make mistakes on humans.** GPT detectors flagged most TOEFL essays by non-native writers as AI (Liang et al., Patterns 2023) — constrained vocabulary looks "predictable". GigaCheck labelled a 2018 UN report as AI. The open RoBERTa detector had 30–78% false positives in the NBER study.
- **Model matters.** In the Habr test, Claude Opus 5 text fooled half the detectors, DeepSeek V4 was caught by all. Instruction-tuned models are *less* human than base models (Reinhart et al., PNAS 2025).

## Our own test (held-out LLMTrace texts, 2026-10)

Six texts by GigaChat-Max, YandexGPT-5, GPT-4.1 and Gemini 2.5; probability "AI" on the open classifiers:

| Variant | RU classifiers (ModernBERT / FRIDA) | EN classifier (desklib) |
|---|---|---|
| Original | 0.50–1.00 / 0.99–1.00 | 0.99–1.00 |
| "Cosmetic" (dashes → commas, synonym swaps, stock phrases removed) | 0.47–1.00 / 0.99–1.00 | 0.96–1.00 |
| Rewritten with this skill | **0.005–0.08 / 0.002–0.006** | **0.09–0.30** |

Cosmetic edits did not move a single classifier verdict. The skill's rewrite moved all six; two
needed a second round, where the fix was matching the genre's texture, not changing words.
Texts are in the repository's `experiment/` folder.

## What this means for rewriting

1. You are changing a **distribution**, not deleting words. A strong classifier needs the text to look like it came from the human distribution as a whole: rhythm, syntax, word choice, stance, specificity, structure — together.
2. The most human thing about a text is **content only that person has**: their facts, numbers, places, opinions, mistakes they made, what they actually did. Models can't invent this without lying; ask for it.
3. **Voice beats rules.** A sample of the author's writing is the strongest single lever (it worked against Pangram). Match its rhythm, punctuation habits, connectors and level of formality.
4. **Measure, don't guess.** Run `scripts/scan.py` and `scripts/detect.py` after each pass. Iterate on the strongest remaining signals.
5. **Be honest about limits.** No one can promise "undetectable by every detector": providers can watermark or retrieve, classifiers are retrained on new humanizers, and detectors are noisy in both directions. What can be promised: text that reads like a person wrote it and scores human on the open detectors we can run.

## The local panel in `scripts/detect.py`

| Detector | Language | Type | Calibration on held-out LLMTrace texts |
|---|---|---|---|
| ru-modernbert (RuModernBERT-small, trained on LLMTrace) | RU | classifier | AUC 1.00; flags 3.6% of human texts at 0.5 |
| ru-frida (rubert-mini-frida, trained on LLMTrace) | RU | classifier | AUC 0.98; flags 12.5% of human texts |
| en-desklib (DeBERTa-v3-large, top open model on RAID) | EN | classifier | AUC 0.95; flags 18% of human texts — 0.5–0.7 is uncertain |
| binoculars (Qwen2.5-0.5B base/instruct), optional `--binoculars` | any | zero-shot | weak at this size: AUC 0.87 RU / 0.73 EN |

These are proxies. Commercial detectors are trained on more and newer data; passing this panel is necessary, not sufficient. Treat a clean result as "no obvious machine signal left", never as proof.
