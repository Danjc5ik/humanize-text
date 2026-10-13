# Russian: what separates human from machine text (measured)

Data: LLMTrace (Sber, 2025), test split, **9358 human + 9358 AI texts**, balanced
inside each genre (article, news, review, story, question/answer, factual, short form, poetry),
60–1200 words. Generators: GigaChat / GigaChat-Max, YandexGPT / YandexGPT-5, GPT-3.5/4/4o, o1, o3,
Qwen2.5/QwQ, Llama 3/3.3, Gemma 1/2, Mistral, Command-R, DeepSeek-R1 distill, Yi, DBRX, ruGPT and more.
*AUC: 0.5 = useless (coin flip), 1.0 = perfectly separates human from AI on its own.

## The five things that give Russian AI text away (in order of strength)

1. **Even rhythm.** Sentence-length variation is the strongest single signal (AUC 0.75; in reviews
   0.85, short posts 0.89). Humans: CV ≈ 0.55, 19% of sentences ≤6 words. Models: CV ≈ 0.38, 9% short.
2. **Канцелярит / nominal style.** 52 verbal nouns (-ание/-ение/-ость/-ация/-ство) per 1000 words
   vs 32 for humans. Longer words overall (5.99 vs 5.61 letters).
3. **No asides, no specifics.** Humans use brackets 3× more, numbers 1.6× more, "..." 7× more,
   semicolons 3× more.
4. **No person.** Humans use я/мы 1.35× and ты/вы 1.7× more often; models write from nowhere.
5. **Template phrases** (below): «подчёркивает важность» appears in 178 AI texts and **0** human ones.

## Myths the data does not support

- **The em dash is NOT a Russian tell.** 5.05 per 1000 words in human texts vs 5.47 in AI (AUC 0.51 —
  a coin flip; 27% vs 29% of texts use it). Russian typography uses тире normally. Removing dashes
  from Russian text does nothing — and the open Russian detectors convert every dash to "-" anyway.
- **«Ёлочки» and ё are not tells** (AUC 0.48 each). Humans in casual genres type " - " instead of
  "—" a bit more often (38% vs 26% of texts) — imitate that only in casual registers.
- **Lexical diversity is the same** (MATTR 0.87 both). Russian models don't over-vary synonyms the way
  English ones do.

## All measured features

| Feature | Humans (mean) | AI (mean) | How well it separates (AUC*) | Texts that have it: humans / AI |
|---|---|---|---|---|
| sentence-length variation (CV) | 0.547 | 0.383 | 0.75 (humans higher) | 98% / 98% |
| sentence-length SD (words) | 8.899 | 6.563 | 0.685 (humans higher) | 98% / 98% |
| share of sentences ≤6 words | 0.186 | 0.086 | 0.678 (humans higher) | 72% / 46% |
| nominalizations /1k words | 32.448 | 52.122 | 0.675 (AI higher) | 90% / 96% |
| brackets /1k | 8.208 | 2.864 | 0.659 (humans higher) | 51% / 20% |
| average word length | 5.613 | 5.986 | 0.644 (AI higher) | 100% / 100% |
| share of sentences ≥30 words | 0.111 | 0.07 | 0.612 (humans higher) | 54% / 30% |
| numbers /1k | 30.68 | 18.855 | 0.611 (humans higher) | 71% / 51% |
| "..." /1k | 4.523 | 0.653 | 0.594 (humans higher) | 23% / 5% |
| sentences starting with And/But · И/Но/А | 0.068 | 0.041 | 0.591 (humans higher) | 45% / 27% |
| I/we · я/мы /1k | 17.112 | 12.722 | 0.582 (humans higher) | 58% / 41% |
| you · ты/вы /1k | 8.48 | 5.016 | 0.575 (humans higher) | 40% / 25% |
| lists of three /1k | 4.78 | 6.83 | 0.572 (AI higher) | 52% / 60% |
| ! /1k | 7.523 | 4.037 | 0.565 (humans higher) | 32% / 19% |
| " - " used as dash /1k | 7.584 | 4.758 | 0.562 (humans higher) | 37% / 26% |
| texts with markdown | 0.009 | 0.126 | 0.559 (AI higher) | 0% / 12% |
| "not X but Y" /1k | 0.236 | 1.061 | 0.549 (AI higher) | 5% / 15% |
| straight quotes /1k | 11.522 | 8.558 | 0.547 (humans higher) | 34% / 25% |
| ; /1k | 2.007 | 0.704 | 0.538 (humans higher) | 11% / 3% |
| lexical diversity (MATTR) | 0.874 | 0.875 | 0.526 (AI higher) | 100% / 100% |
| «» /1k | 4.546 | 3.491 | 0.523 (humans higher) | 25% / 20% |
| share of list lines | 0.014 | 0.035 | 0.522 (AI higher) | 3% / 7% |
| ё per 1000 Cyrillic letters | 1.649 | 1.361 | 0.52 (humans higher) | 39% / 36% |
| ? /1k | 2.099 | 2.467 | 0.513 (humans higher) | 18% / 15% |
| share of questions | 0.018 | 0.016 | 0.511 (humans higher) | 14% / 12% |

## Every modern model shares the profile

| Source | sentence-length variation (CV) | share of sentences ≤6 words | nominalizations /1k words | average word length | brackets /1k | numbers /1k |
|---|---|---|---|---|---|---|
| **humans** | 0.55 | 0.19 | 32.45 | 5.61 | 8.21 | 30.68 |
| Yi-1.5-34B-Chat | 0.35 | 0.07 | 55.35 | 6.07 | 1.45 | 23.5 |
| c4ai-command-r-08-2024 | 0.32 | 0.06 | 55.19 | 5.95 | 0.52 | 11.04 |
| GigaChat-Max | 0.35 | 0.08 | 59.93 | 6.38 | 2.43 | 13.94 |
| Meta-Llama-3-8B-Instruct | 0.45 | 0.09 | 46.18 | 5.89 | 3.73 | 20.87 |
| Phi-3-mini-128k-instruct | 0.47 | 0.1 | 50.27 | 5.96 | 2.71 | 25.68 |
| QwQ-32B | 0.38 | 0.11 | 48.47 | 6.02 | 5.17 | 23.67 |
| Qwen2.5-72B-Instruct | 0.35 | 0.09 | 51.21 | 6.02 | 2.17 | 19.73 |
| WizardLM-2-7B | 0.46 | 0.09 | 57.89 | 6.03 | 3.95 | 20.42 |
| dbrx-instruct | 0.36 | 0.09 | 44.97 | 5.8 | 1.92 | 19.31 |
| DeepSeek-R1-Distill-Qwen-32B | 0.36 | 0.09 | 44.85 | 5.83 | 1.71 | 19.43 |
| gemma-1.1-7b-it | 0.62 | 0.14 | 74.03 | 6.25 | 3.85 | 18.23 |
| gigachat | 0.32 | 0.05 | 51.27 | 5.91 | 2.53 | 9.3 |
| gemma-2-27b-it | 0.37 | 0.1 | 48.49 | 5.92 | 2.25 | 16.75 |
| gpt-3.5 | 0.36 | 0.05 | 63.72 | 6.17 | 4.92 | 19.5 |
| llama-7b | 0.49 | 0.15 | 38.25 | 5.9 | 8.5 | 28.79 |
| Ministral-8B-Instruct-2410 | 0.35 | 0.1 | 49.78 | 5.95 | 2.6 | 22.13 |
| ruGPT | 0.59 | 0.14 | 40.88 | 5.8 | 5.93 | 39.42 |
| Llama-3.3-70B-Instruct | 0.31 | 0.04 | 50.23 | 5.97 | 1.02 | 15.36 |
| yagpt | 0.33 | 0.05 | 57.59 | 6.12 | 3.79 | 16.38 |
| YandexGPT-5-Lite-8B-instruct | 0.38 | 0.11 | 49.18 | 5.88 | 2.04 | 20.68 |

Older/base-like generators (ruGPT, llama-7b) sit closer to humans; instruction-tuned chat models
(GigaChat-Max, YandexGPT-5, Qwen2.5, Llama-3.3) are the most uniform and the most nominal.
This matches Reinhart et al. (PNAS 2025): instruction tuning makes output *less* human.

## Words and phrases models overuse (× = how many times more texts contain it, same genres)

Lemmas (dictionary forms) for words and pairs; surface forms for three-word phrases.

такой как (5.18×); подчёркивать (11.74×); важно (3.4×); несмотря (3.1×); ключевой (5.15×); включая (3.91×); важность (9.29×); уникальный (5.22×); не просто (4.57×); мочь привести (6.77×); это не просто (18.66×); где каждый (19.97×); может привести к (7.96×); стремиться (3.55×); вдохновлять (19.37×); заключение (3.5×); отражать (5.81×); являться важный (18.12×); демонстрировать (5.55×); роль в (4.81×); трудность (4.43×); подчёркивать важность (357.0×); аспект (4.9×); сталкиваться (4.42×); в заключение (10.02×); сталкиваться с (6.01×); мочь стать (4.09×); важный шаг (40.33×); последствие (3.11×); стать настоящий (24.07×); обеспечивать (3.33×); свидетельствовать о (5.75×); подчёркивать что (11.51×); инструмент для (7.71×); способствовать (3.25×); столкнуться с (4.02×); это не только (10.94×); однако несмотря (56.6×); однако несмотря на (56.6×); важно отметить (20.07×); стремление (4.42×); внимание к (6.86×); известный свой (8.38×); являться один (4.15×); незабываемый (8.16×); показывать что (4.76×); важно помнить (17.0×); стремиться к (4.93×); важно отметить что (21.15×); вдохновение (4.62×); стать важный (20.85×); шаг в (6.17×); возможность для (4.62×); важный роль (7.84×); играть важный (17.93×); свидетельствовать (3.35×); важно помнить что (26.11×); стремление к (8.88×); и улучшение (16.6×); мир где (5.98×); в развитие (4.76×); важную роль в (10.26×); разочарование (4.57×); удобство (4.01×); привлекательный (4.45×); комфортный (3.11×); навык (3.78×); эффективность (3.2×); укрепление (4.47×); поделиться свой (6.95×); что делает его (30.43×); кто искать (14.06×); гармония (4.6×); ключевой роль (11.67×); надёжный (3.05×); инновация (7.59×); является одним из (4.59×); приключение (4.41×); каждый шаг (12.26×); исторический контекст (39.0×); и поддержка (5.44×); чтобы избежать (5.06×); мочь иметь (6.42×); это настоящий (7.63×); царить (4.56×); готовый помочь (9.0×); одним из самых (4.1×); предотвращение (5.31×); заботиться о (5.98×); привлекать (3.13×); значимый (3.8×); и безопасность (7.0×); из ключевой (8.85×); последствие для (8.93×); привлечь внимание (6.4×); обеспечение безопасность (9.48×); инновационный (5.24×); включает в себя (5.82×); основный мысль (171.0×); стать один (4.18×); след в (11.21×); стать символ (12.29×); уют (4.01×); ключевую роль в (12.06×); напоминание о (8.56×); захватывать (5.98×); рекомендоваться (3.88×); быть связать (4.31×); играть ключевой (16.64×); наследие (4.09×); привлекать внимание (19.89×); и комфорт (14.38×); эмоциональный (3.84×); новый горизонт (155.0×); спокойствие (3.9×); адаптироваться (12.6×); иметь свой (4.04×); несмотря на все (7.69×); ключ к (7.69×); опыт и (4.74×); предотвратить (3.29×); могут привести к (12.33×); неотъемлемый часть (8.91×); важным шагом в (147.0×); это событие (6.18×); стабильность и (9.48×); о важность (31.0×); чтобы обеспечить (7.34×); уникальный и (22.43×); комфорт и (7.67×); создавать ощущение (17.89×); трудность и (9.1×); забывать о (4.75×); развитие и (5.68×); и эффективный (5.87×); кто ценить (47.0×); разочаровать (3.91×); неотъемлемый (5.77×); заботиться (3.77×); адаптироваться к (17.44×); выразить свой (6.03×); открывать новый (9.42×); и культурный (8.13×); тщательный (4.84×); новый возможность (5.13×); свой путь (4.66×); и профессионализм (14.27×); справедливость (3.14×); свой уникальный (12.38×); и обеспечить (5.28×); забота о (5.13×); сложный и (5.62×); создавать атмосфера (44.33×); для пользователь (5.49×); напоминать о (5.81×); это может привести (7.15×); это позволять (6.03×); выбор для (12.23×); метафора (8.43×); это свидетельствует о (27.4×)

## What humans write that models almost don't

очень (2.9×); ну (6.7×); нет (2.8×); надо (6.2×); раз (2.8×); сказать (2.5×); там (2.9×); тут (4.3×); да (3.1×); ничего (4.0×); потом (4.2×); тоже (3.4×); вообще (6.2×); сейчас (3.0×); какой то (4.2×); много (2.7×); ни (2.6×); про (4.0×); совсем (4.3×); хорошо (3.1×); у мы (3.4×); тот же (3.3×); и так (3.7×); как то (7.1×); таки (9.1×); думать (2.6×); чуть (5.9×); сразу (2.6×); почти (3.2×); уж (4.5×); нибыть (4.5×); у я (2.9×); конечно (2.6×); ходить (4.2×); кстати (9.1×); да и (5.3×); опять (4.8×); причём (11.1×); при это (2.9×); ничего не (4.3×); пойти (3.0×); получиться (5.6×); так к (20.0×); то есть (5.0×); так же (5.6×); всё таки (8.3×); ну и (8.3×); и на (2.9×); посмотреть (3.2×); так что (3.1×); всякий (4.3×); куда (2.9×); понравиться (3.2×); сильно (4.0×); наверное (6.2×); немного (2.6×); а вот (5.0×); не очень (6.2×); мало (3.8×); хоть (2.9×); долго (3.3×); и всё (2.7×); так быть (10.0×); достаточно (2.6×); я и (3.4×); и по (4.8×); тем более (12.5×); видимо (6.2×); сколько (3.0×); а потом (4.2×); бывать (3.3×); а то (10.0×); я в (2.8×); и с (2.6×); не надо (8.3×); а так (20.0×); никак (6.2×); брать (3.0×); вполне (3.7×); вроде (3.4×); у вы (2.9×); в общий (2.8×); то не (5.3×); практически (3.2×); остальной (2.7×); просить (2.6×); так далее (3.4×); ну а (12.5×); поставить (2.7×); что и (4.8×); примерно (3.4×); даже не (3.3×); собственно (20.0×); туда (2.8×); фото (4.8×); и ещё (5.0×); впрочем (7.7×); довольно (3.1×); ещё и (5.3×); р (5.9×); положить (3.8×); вы не (2.9×); в какой (5.0×); естественно (8.3×); зачем (2.9×); в принцип (33.3×); чтоб (2.9×); плохой (2.5×); пол (2.9×); входить (3.0×)

These are the connective tissue of real Russian: particles (ну, же, вот, вообще, таки, уж), hedges
(наверное, видимо, вроде, вполне), colloquial links (кстати, причём, то есть, тем более, а то, так что),
plain verbs (сказать, пойти, взять, посмотреть) and concrete words (час, неделя, три). Use the ones
that fit the register; a formal text gets fewer particles, but still plain verbs and specifics.

## Register notes

- **Formal/academic** (рефераты, статьи, abstracts): human writers also use nominal style here, and
  in AINL-Eval 2025 (35k Russian abstracts) marker lists triggered on 36% of human texts — so don't
  strip all formality. Fix rhythm, remove the template phrases, add concrete data and an author's
  position ("мы показали", "в нашей выборке").
- **Essay/сочинение**: a clear personal position, a concrete example from a book or life, uneven
  paragraph lengths, no «В современном мире…» opening, no «Таким образом…» closing paragraph.
- **Posts, reviews, comments**: short sentences, particles, " - " instead of "—", ellipses, brackets,
  a joke or an irritation, numbers (цены, даты, сколько ждал).
- **Business letters**: plain verbs, one request per paragraph, no «является», «осуществлять», «данный».

## Template phrases and constructions (from corpus + Russian marker studies)

| Pattern | Example | Instead |
|---|---|---|
| Значимость | играет важную/ключевую роль; является важным; подчёркивает важность | say what exactly it changes |
| «Важно отметить» | важно отметить/помнить, стоит отметить, следует подчеркнуть | just state it |
| «Не просто X, а Y» | это не просто инструмент, а партнёр; не только…, но и… | name the thing directly |
| Шаблонное начало | в современном мире, в эпоху, в наше время, на сегодняшний день | start with the point |
| Шаблонный вывод | в заключение, подводя итог, таким образом, итак | end on a concrete thought |
| Размытый авторитет | эксперты считают, исследования показывают | name the source or cut |
| Канцелярит | осуществлять, является, данный, в рамках, в целях, в связи с этим | plain verbs |
| «Где каждый», «мир, где» | создать пространство, где каждый… | concrete scene |
| Однако, несмотря на | однако, несмотря на трудности, … (57×) | но / хотя |
| Риторический вопрос + ответ | Почему это важно? Потому что… | statement |
| Псевдотерапия (2025–26) | и это нормально; ты не одинок; это не слабость | cut |
| Чат-бот | Конечно! Отличный вопрос! Надеюсь, это поможет. Давайте разберёмся | cut |
| Ложный диапазон | от новичков до профессионалов | name the audience |
| Тройки | быстро, удобно и надёжно | one precise word or two |
