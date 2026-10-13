# English: what separates human from machine text (measured + literature)

Data: LLMTrace (Sber, 2025), test split, **9879 human + 9879 AI texts**,
balanced inside each genre (article, news, review, story, question, factual, short form, paper
abstract, poetry). Generators include GPT-4.1, o3, Gemini 2.0/2.5 Flash, Qwen2.5/Qwen3, Llama 3.3,
Nemotron, Mistral/Magistral, GLM-4, Command-R, DeepSeek-R1 distill, Falcon3, DBRX.
*AUC: 0.5 = coin flip, 1.0 = perfect separation on its own.

## The strongest signals

1. **Long, Latinate words** — average 5.26 letters vs 4.74 (AUC 0.73; in reviews 0.86, Q&A 0.88).
2. **Nominal style** — 46 -tion/-ment/-ness/-ity words per 1000 vs 26 (AUC 0.70).
3. **Too much lexical variety** — MATTR 0.837 vs 0.805: models rotate synonyms ("elegant variation");
   people repeat the plain word.
4. **Even rhythm** — sentence-length CV 0.37 vs 0.48; half as many very short sentences.
5. **No one is speaking** — I/we 9.6 vs 21.5 per 1000 words; "you" 4.3 vs 9.3.
6. **No specifics or asides** — numbers 12.7 vs 26.4 per 1000; brackets 2.9 vs 5.9.
7. **Lists of three** (+68%) and **"not X but Y"** (in 13% of AI texts vs 3% of human ones).

The **em dash** is a weak English signal (1.9 vs 1.0 per 1000 words; present in 18% of AI texts vs
10% of human), and Wikipedia's editors now list it as a *dated* sign (models stopped overusing it in
2026; OpenAI added an instruction-following fix in Nov 2025). Don't stop at it.
Contractions are *not* a reliable human signal in this corpus (models used slightly more, driven by
stories). Use contractions where the register wants them, not as camouflage.

## All measured features

| Feature | Humans (mean) | AI (mean) | How well it separates (AUC*) | Texts that have it: humans / AI |
|---|---|---|---|---|
| average word length | 4.739 | 5.262 | 0.734 (AI higher) | 100% / 100% |
| nominalizations /1k words | 26.488 | 46.441 | 0.703 (AI higher) | 88% / 95% |
| lexical diversity (MATTR) | 0.805 | 0.837 | 0.691 (AI higher) | 100% / 100% |
| sentence-length variation (CV) | 0.482 | 0.368 | 0.668 (humans higher) | 96% / 97% |
| I/we · я/мы /1k | 21.501 | 9.6 | 0.656 (humans higher) | 67% / 42% |
| brackets /1k | 5.884 | 2.896 | 0.627 (humans higher) | 49% / 24% |
| sentence-length SD (words) | 11.588 | 8.714 | 0.621 (humans higher) | 96% / 97% |
| share of sentences ≤6 words | 0.073 | 0.037 | 0.595 (humans higher) | 42% / 24% |
| numbers /1k | 26.426 | 12.684 | 0.593 (humans higher) | 64% / 48% |
| lists of three /1k | 2.815 | 4.716 | 0.592 (AI higher) | 41% / 56% |
| you · ты/вы /1k | 9.3 | 4.294 | 0.582 (humans higher) | 37% / 22% |
| contractions /1k | 12.245 | 15.383 | 0.558 (AI higher) | 71% / 78% |
| "not X but Y" /1k | 0.108 | 0.557 | 0.55 (AI higher) | 2% / 12% |
| "..." /1k | 0.943 | 0.142 | 0.55 (humans higher) | 12% / 2% |
| share of sentences ≥30 words | 0.254 | 0.229 | 0.543 (humans higher) | 81% / 69% |
| em dash — /1k | 0.993 | 1.857 | 0.541 (AI higher) | 10% / 18% |
| sentences starting with And/But · И/Но/А | 0.028 | 0.018 | 0.533 (humans higher) | 22% / 15% |
| " - " used as dash /1k | 1.043 | 0.658 | 0.528 (humans higher) | 11% / 5% |
| ! /1k | 1.674 | 1.135 | 0.525 (humans higher) | 14% / 9% |
| «» /1k | 0.101 | 0.0 | 0.522 (humans higher) | 4% / 0% |
| : /1k | 3.698 | 4.03 | 0.52 (humans higher) | 35% / 31% |
| curly apostrophes /1k | 3.943 | 4.543 | 0.518 (AI higher) | 21% / 25% |
| straight quotes /1k | 8.754 | 6.616 | 0.518 (humans higher) | 30% / 27% |
| " – " /1k | 0.142 | 0.32 | 0.513 (AI higher) | 2% / 4% |
| ? /1k | 1.715 | 1.367 | 0.513 (humans higher) | 17% / 14% |
| share of list lines | 0.005 | 0.018 | 0.51 (AI higher) | 0% / 2% |
| ; /1k | 1.352 | 0.973 | 0.51 (humans higher) | 17% / 15% |

## Every modern model shares the profile

| Source | sentence-length variation (CV) | share of sentences ≤6 words | nominalizations /1k words | average word length | brackets /1k | numbers /1k |
|---|---|---|---|---|---|---|
| **humans** | 0.48 | 0.07 | 26.49 | 4.74 | 5.88 | 26.43 |
| c4ai-command-r-08-2024 | 0.32 | 0.03 | 48.93 | 5.24 | 1.37 | 9.04 |
| Qwen2.5-72B-Instruct | 0.34 | 0.03 | 45.25 | 5.14 | 2.45 | 10.37 |
| Qwen3-32B | 0.35 | 0.05 | 51.35 | 5.42 | 3.7 | 13.93 |
| dbrx-instruct | 0.35 | 0.03 | 43.62 | 5.11 | 2.55 | 16.22 |
| DeepSeek-R1-Distill-Qwen-32B | 0.33 | 0.02 | 49.6 | 5.26 | 2.47 | 12.61 |
| gemini-2.0-flash | 0.42 | 0.08 | 46.0 | 5.34 | 2.7 | 11.31 |
| gemini-2.5-flash | 0.41 | 0.05 | 46.87 | 5.47 | 2.12 | 9.91 |
| gpt-4.1-2025-04-14 | 0.37 | 0.03 | 44.27 | 5.3 | 2.26 | 10.11 |
| Magistral-Small-2507 | 0.36 | 0.04 | 38.74 | 5.01 | 2.53 | 13.25 |
| Ministral-8B-Instruct-2410 | 0.35 | 0.03 | 46.02 | 5.18 | 3.83 | 15.82 |
| Llama-3.1-Nemotron-70B-Instruct-HF | 0.49 | 0.05 | 55.04 | 5.5 | 9.9 | 22.55 |
| o3-2025-04-16 | 0.4 | 0.05 | 34.94 | 5.25 | 2.19 | 15.82 |
| Falcon3-10B-Instruct | 0.34 | 0.02 | 52.82 | 5.39 | 2.15 | 10.2 |
| Llama-3.3-70B-Instruct | 0.34 | 0.02 | 44.46 | 5.07 | 0.85 | 8.12 |
| GLM-4-32B-0414 | 0.34 | 0.04 | 46.0 | 5.22 | 2.51 | 12.51 |

## Words and phrases models overuse (× = how many times more texts contain it, same genres)

significant (4.93×); potential (5.04×); testament to (299.4×); testament (41.16×); crucial (10.07×); reminder (33.31×); a testament (277.8×); a testament to (275.4×); a significant (7.28×); highlights (17.46×); profound (23.9×); ensuring (15.6×); particularly (4.85×); underscores (113.89×); testament to the (187.0×); importance of (9.74×); unique (5.3×); importance (6.47×); offering (6.72×); the importance of (9.97×); reminder of (48.68×); the importance (9.38×); highlights the (42.62×); a reminder (50.65×); resilience (50.41×); remains (3.99×); underscores the (255.67×); not just (5.82×); broader (16.43×); the potential (8.55×); landscape (9.67×); serves (7.09×); realm (16.61×); highlighting (28.41×); reminder of the (101.57×); serves as a (17.34×); in conclusion (55.15×); diverse (5.94×); serves as (8.9×); enhance (7.63×); tapestry (75.67×); commitment (8.06×); implications (10.19×); vibrant (23.9×); innovative (12.61×); conclusion (6.3×); intricate (19.97×); commitment to (12.54×); leading to (5.56×); insights (6.82×); enduring (15.26×); offering a (30.81×); sense of (4.5×); ultimately (4.74×); ensure (4.01×); the need for (8.14×); realm of (38.6×); a sense of (9.44×); reminder that (51.0×); additionally (5.19×); need for (4.81×); navigate (12.84×); the need (4.92×); a sense (7.64×); offers a (9.62×); stark (14.26×); is crucial (12.88×); enhancing (13.09×); tapestry of (165.67×); a beacon (164.33×); enabling (8.13×); beacon (25.57×); fostering (30.88×); reflecting (10.63×); emphasizing (21.64×); understanding of (5.46×); this approach (7.36×); deeper (5.7×); comprehensive (5.09×); a powerful (6.46×); ongoing (5.22×); fleeting (24.05×); essence (11.69×); prioritize (25.74×); ensures (10.02×); abstract (11.57×); embrace (6.45×); blend (12.02×); relentless (18.7×); a profound (31.4×); the realm (21.35×); pivotal (19.72×); is a testament (87.0×); complexities (22.43×); a stark (86.2×); strategic (7.35×); lies (3.66×); unwavering (411.0×); the realm of (34.23×); a crucial (12.21×); a unique (7.34×); secrets (8.01×); presence (3.42×); consequences (6.2×); reflects (8.15×); a reminder of (39.0×); potentially (4.39×); mere (6.2×); the power of (5.78×); highlighting the (38.45×); beneath (4.62×); societal (11.74×); a reminder that (81.4×); efficiency (3.96×); connection (3.52×); crucial for (13.74×); particularly in (11.22×); merely (5.33×); enhanced (6.75×); nature of (4.08×); shift (4.39×); amidst (15.9×); maintaining (5.5×); path (3.12×); the challenges (9.98×); chaos (6.28×); vast (4.2×); solace (24.65×); shaping (16.19×); well being (9.78×); integration (7.13×); cultural (3.85×); not merely (43.0×); pursuit (6.51×); blend of (23.82×); of hope (15.96×); inherent (8.17×); growth (3.04×); laughter (7.21×); weight of (8.53×); the article (6.16×); remains a (8.96×); beacon of (118.33×); echoes (19.38×); marked (4.05×); addressing (7.0×); enhances (14.59×); valuable (4.24×); sparked (8.18×); tale of (11.51×); safety (3.01×); boundaries (5.67×); evolving (8.36×); to enhance (7.31×); the complexities (115.0×); influence (3.1×); the enduring (341.0×); experiences (3.69×); findings (4.66×); allowing (3.15×)

## What humans write that models rarely do

because (3.6×); get (3.2×); do (2.6×); i have (5.6×); show (2.7×); have to (5.6×); going (4.2×); know (2.8×); go (2.6×); if you (3.2×); to get (3.8×); want (3.0×); to do (4.3×); have a (3.3×); you are (5.0×); think (2.8×); really (3.1×); that he (3.6×); going to (5.6×); there is (3.3×); am (3.2×); want to (3.4×); he is (4.0×); you have (4.3×); as well (3.0×); say (2.6×); able (3.3×); able to (3.3×); all the (2.7×); goes (4.2×); put (2.9×); in order (7.1×); i am (3.3×); i think (5.0×); in order to (8.3×); all of (5.0×); to go (4.3×); that i (4.0×); order to (6.7×); i don't (7.7×); to have (2.6×); don't (2.5×); there are (2.8×); give (2.6×); i would (4.3×); a lot (3.4×); that you (4.2×); but i (3.4×); lot (3.0×); i was (2.6×); you will (4.5×); a very (6.7×); getting (3.0×); most of (4.5×); of them (3.8×); anything (3.1×); when he (3.3×); because of (4.0×); as well as (2.7×); well as (2.7×); she is (4.2×); went (2.8×); try (2.7×); probably (4.5×); i know (4.5×); gets (3.3×); so i (4.3×); we have (3.3×); did not (2.9×); who is (3.3×); when i (3.0×); some of (3.1×); and is (2.6×); a lot of (3.6×); lot of (3.4×); saying (2.9×); you want (4.2×); wants (3.7×); doing (2.7×); done (2.6×); asks (6.2×); like to (5.3×); ni (50.0×); he has (3.1×); wanted (3.1×); bad (2.9×); go to (3.6×); i had (3.1×); it will (2.9×); i do (4.8×); we show (11.1×); so that (4.5×); propose a (3.7×); a number of (7.1×); is very (9.1×); that she (3.6×); to say (4.0×); out of the (3.2×); they have (3.0×); happy (3.0×); in which (2.8×); please (3.8×); said that (5.3×); if you are (5.6×); try to (3.8×); https (4.8×); a number (5.3×); we present (7.7×); and was (2.9×); have the (3.0×)

The human side is plain verbs and function words: get, do, go, have to, going to, want to, a lot,
because, probably, I think, I don't, I know, as well as, in order to.

## From the literature

**Kobak et al., Science Advances 2025** (15M PubMed abstracts): ≥13.5% of 2024 abstracts were
LLM-processed; 66% of the excess words are verbs. Top: delves (28×), underscores (13.8×),
showcasing (10.7×); common: additionally, comprehensive, crucial, enhancing, exhibited, insights,
notably, particularly, within. Also: intricate, meticulous(ly), pivotal, realm, seamless, showcase,
garner, bolster, foster(ing), harness, elucidate, multifaceted, nuanced, noteworthy, groundbreaking,
transformative, unparalleled, unveil, underscore, utilize, versatile.

**Reinhart et al., PNAS 2025** (Biber features, GPT-4o & Llama 3): instruction-tuned models use
present participial clauses 2–5× more ("…, highlighting the need…"), that-clauses as subjects
2.6–3.3×, nominalizations 1.5–2×, phrasal coordination 1.4–1.9×; and 37–40% fewer contractions,
40–45% fewer downtoners (a bit, somewhat, fairly), 19–38% fewer first-person pronouns, fewer agentless
passives (GPT-4o −50%). Overused words: camaraderie (~150×), tapestry (~150×), intricate (~120×),
palpable (~100×+), amidst (~90×).

**Wikipedia: Signs of AI writing** (WikiProject AI Cleanup, updated 2026), by era:
- 2023–mid-2024: additionally, boasts, bolstered, crucial, delve, emphasizing, enduring, garner,
  intricate, interplay, key, landscape, meticulously, pivotal, underscore, tapestry, testament, valuable, vibrant
- mid-2024–mid-2025: align with, bolstered, crucial, emphasizing, enhance, enduring, fostering,
  highlighting, pivotal, showcasing, underscore, vibrant
- mid-2025–mid-2026: emphasizing, enhance, highlighting, showcasing
- mid-2026+ (GPT-6 era): challenge, clearer, dependable, echoed, foster, leverage, matters,
  multifaceted, practical, prioritize, quietly, steady, universally
- Structures: significance/legacy inflation ("stands as a testament", "plays a pivotal role",
  "reflects broader trends"); superficial -ing analyses ("…, highlighting/underscoring/ensuring…");
  promotional tone ("nestled", "in the heart of", "boasts", "renowned"); vague attributions
  ("experts argue", "observers have noted"); "Despite its…, faces several challenges" + optimistic
  outlook ending; avoiding is/are ("serves as", "stands as", "features", "offers"); negative
  parallelism ("not just X, but Y"; "it's not X, it's Y"; "no X, no Y, just Z"); rule of three;
  Title Case headings; boldface sprinkled through prose; "**Label:** text" bullet lists; emoji
  headers; curly quotes in otherwise plain text; collaborative chatter ("Certainly!", "I hope this
  helps", "Would you like…"); hedging disclaimers ("While specific details are limited…"; 2026:
  "should be treated as X rather than Y"); placeholders ("[Your Name]", "2025-XX-XX"); tool
  artifacts (oaicite, contentReference, turn0search0, [cite: 1], 【85†L261】, attached_file).

**Pangram on Claude**: "complex and multifaceted" (~700× more common in AI), "intricate interplay"
(~100×), "played a crucial role" (~70×); Claude's writing styles and custom styles built from real
samples were still "clearly identifiable as AI". A 2026 essay by Claude Opus 5 written specifically to
beat Pangram scored 100% AI: balanced claims, triple examples, tidy paragraph closures, strategic
hedging — the "hotel lobby" voice.

## Register notes

- **Academic**: nominal style is partly legitimate. Keep terminology; fix rhythm, cut participial
  "-ing" tails, use "we" for what the authors did, report actual numbers, drop "delve/underscore/
  showcase/notably/crucial".
- **Essays**: one arguable position, a concrete example only this writer would pick, uneven
  paragraphs, no "In today's fast-paced world" opening or "In conclusion" summary.
- **Posts, reviews, emails**: short words, contractions, I/you, numbers, a specific complaint or
  detail, fragments where natural, no headings or bold.
