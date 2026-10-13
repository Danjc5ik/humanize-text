# Rewriting playbook

The order matters: the first moves change the text's distribution the most; the last ones polish.
Each move says *why* (which measured signal it fixes). Examples are in Russian and English.

Contents: 0 ground rules · 1 content · 2 voice · 3 structure · 4 rhythm · 5 syntax · 6 words ·
7 stance · 8 punctuation & format · 9 the edit loop · 10 worked examples

---

## 0. Ground rules

- **Rewrite, don't paraphrase sentence by sentence.** A sentence-by-sentence paraphrase keeps the
  model's structure, paragraph shape and argument order — exactly what classifiers read. Extract the
  content (facts, claims, examples), close the original, and write it again in the target voice.
- **Never invent the human part.** No made-up personal stories, quotes, numbers, sources or
  experiences. Ask the author for them; if they can't give any, write a plainer text without them.
  Invented specifics are the first thing a teacher, editor or Антиплагиат reviewer checks.
- **No tricks.** No homoglyphs, zero-width characters, deliberate typos, random synonym swaps.
  Detectors normalise them away and newer ones (Turnitin, GPTZero) are trained to catch them.
- **Keep the meaning.** After the rewrite, check every fact and number against the source.

## 1. Content: put back what only a person has

Strongest lever, because models leave it out: numbers are 2× rarer and first person 1.4–2.2× rarer in
AI text than in human text of the same genre.

- Specifics: who, where, when, how much, how long, what exactly. "Some time later" → "через две
  недели"; "significantly faster" → "from 40 to 9 minutes".
- A position: what does the author actually think? One clear opinion beats three balanced views.
- One example only this author would pick (from their reading, their job, their city).
- A small honest limitation or doubt in the author's words ("не уверен, что это сработает у всех").
- Cut what has no content: significance claims, summaries of what was just said, "it is important".

## 2. Voice: anchor to a real author

If you have samples of the author's writing, run `scripts/voice.py` and match the card: sentence
range, short-sentence share, how they open sentences, dash and quote habits, brackets, ellipses,
person, connectors. This was the move that beat Pangram in public experiments; style *presets*
without real samples did not.

No samples? Pick the voice the genre implies (a student's essay, a tired reviewer, an engineer's
email) and keep it consistent. A real person has one voice, not a neutral average.

## 3. Structure: break the template

Models build every piece the same way: opener that sets the scene → 3 balanced points → tidy
closing summary. Paragraphs of equal length that each end with a mini-conclusion.

- Start with the point, a fact, a scene or a question you actually answer — not with context.
- Unequal paragraphs: one long, one of a single sentence. Not every paragraph needs a closing line.
- Don't give three of everything. Keep the one that matters, or two, or four.
- Drop the final "in conclusion" paragraph; end on the last real thought or a concrete detail.
- Let the order follow the author's thinking (sometimes the conclusion comes first), not a template.
- Headings, bold, bullet lists in prose → turn into sentences unless the genre needs them.

## 4. Rhythm: the strongest single statistic

Sentence-length variation is the best single separator in Russian (AUC 0.75; up to 0.89 in reviews)
and among the best in English. Humans: CV ≈ 0.5, about one sentence in five is ≤6 words (RU).
Models: CV ≈ 0.37, few short sentences, few very long ones.

- Mix: a 3–5-word sentence after a long one. An occasional long sentence with an aside in brackets.
- Short sentences must carry content ("Не помогло.", "It broke twice.") — not dramatic punchlines
  ("And that matters.", "Here's the thing."), which are a 2025–26 model habit of their own.
- Don't make the rhythm regular in a new way (long-short-long-short). Uneven means uneven.
- Target: `scan.py` shows CV and short-sentence share inside the human band for the language.

## 5. Syntax: verbs, not nouns

- Nominalizations: AI uses 1.6× (RU) to 1.75× (EN) more. «Осуществление контроля за выполнением»
  → «проверять, сделано ли»; "the implementation of the solution" → "we implemented it".
- Present-participle tails (EN, 2–5× in models, PNAS 2025): "…, highlighting the need for…",
  "…, ensuring that…" → a separate sentence or cut. RU equivalent: chains of причастные/деепричастные
  обороты → split into clauses with a verb.
- Use is/are (есть/это) instead of "serves as / stands as / boasts / features", «является».
- Plain connectors humans use: because, so, but, then, anyway · потому что, так что, но, а потом, кстати.
- Some agentless passive and downtoners are human ("it got fixed", "a bit", "somewhat", «вроде», «довольно»).

## 6. Words

- Remove AI-favoured vocabulary: run `scan.py`; it lists every hit with how many times more often it
  appears in AI text of the same genre. Lists are in `russian.md` and `english.md`.
- Don't replace them with fancier synonyms — replace with the plain word a person in this genre
  would use, or delete the phrase.
- **Repeat the plain word** instead of rotating synonyms (EN models have higher lexical variety:
  MATTR 0.84 vs 0.81 — "elegant variation").
- Shorter words: EN average 5.26 → aim near 4.7–4.9; RU 5.99 → near 5.6.
- Add the human connective tissue that fits the register: RU particles and links (ну, же, вот,
  вообще, кстати, причём, то есть, наверное, вроде) in informal text; EN "a lot", "probably",
  "I think", "kind of", "anyway" in informal text. Formal text gets fewer, but never zero specifics.

## 7. Stance

- One voice with an opinion, not "on the one hand… on the other hand" for everything.
- Hedges where a person is unsure, not everywhere ("strategic hedging" is a Claude tell).
- No reassurance ("и это нормально", "you're not alone"), no cheerleading, no moral at the end.
- No questions asked only to be answered ("Why does this matter? Because…").

## 8. Punctuation and format

- **Russian**: dashes are normal Russian typography — keep them where grammar wants them. In casual
  genres people often type " - " instead of "—", use "...", brackets, straight quotes; in formal
  texts «ёлочки» and "—" are correct. Detectors normalise all of these anyway; this is about looking
  like the genre to a human reader.
- **English**: em dashes are a weak, dated tell; 1–2 per text is fine. Brackets and numbers are
  human. Curly vs straight quotes don't matter to detectors.
- Remove markdown, emoji bullets, "**Label:** text" lists and Title Case headings from prose.

## 9. The edit loop

```
scan.py draft.txt            → fix the top signals (rhythm, nominal style, AI words, patterns)
detect.py draft.txt          → which detectors still say AI?
repeat 2–4 times, each time on the strongest remaining signal, not all at once
```
When the scan says human but a classifier still says AI, the text is too clean for its genre. Real
reviews have "))" and "...", asides in brackets, a complaint next to praise, odd specific details
("в среду", "минут 20", "2 порции"); real blog posts wander a little. Look at 2–3 genuine texts of the
genre and match their texture (never by adding typos). That move fixed both texts that survived the
first round in our experiment (RU review 0.83 → 0.006, EN article 0.68 → 0.29 on the classifiers).

Stop when: style and structure scores are in the human range, the open detectors say human, the
facts match the source, and it reads like the author. If a detector still flags it after 4 rounds,
the problem is usually structure or voice (sections 2–3), not words.

Length: under ~150–200 words every detector is unreliable in both directions — don't chase scores
on very short texts; make them read well.

## 10. Worked examples

**RU, essay paragraph — before (GPT-style):**
> В современном мире технологии играют ключевую роль в образовании. Важно отметить, что цифровые
> инструменты не просто облегчают обучение, а открывают новые возможности для каждого ученика.
> Таким образом, внедрение технологий способствует повышению качества образования.

Signals: stock opener, «играют ключевую роль», «важно отметить», «не просто…, а…», «где каждый»-type
universal, «Таким образом», 4 nominalizations in 3 sentences, three sentences of 12–14 words (flat rhythm).

**After (student voice, content supplied by the author):**
> В нашем классе электронный дневник появился в пятом классе, а нормальные онлайн-тесты — только
> в девятом. Честно, первые полгода от них было больше путаницы, чем пользы. Зато потом стало
> видно, кто реально понял тему, а кто списал: учительница по алгебре так и сказала. Так что польза
> есть. Но не сама по себе.

**EN, product description — before:**
> Nestled in the heart of the city, our café serves as a vibrant hub where coffee lovers can
> embark on a journey of flavor. It's not just coffee — it's an experience that fosters connection.

**After (owner's voice, facts from the owner):**
> We're the small place on Pine Street with six tables and a roaster in the back window. We roast
> twice a week, so the beans you buy are never older than four days. Come early on Saturdays —
> the cinnamon buns are gone by eleven.
