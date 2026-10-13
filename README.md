# humanize-text

**Скил для нейросетей, который переписывает ИИ-текст так, чтобы он читался как написанный человеком, и сам проверяет результат настоящими детекторами.** Работает с русским и английским.

[English below](#english)

## Почему обычные «очеловечиватели» не работают

- Сильные детекторы (Pangram, GPTZero, Turnitin, GigaCheck, «Антиплагиат») — это нейросети-классификаторы. Они оценивают весь «голос» текста: ритм, синтаксис, позицию автора, конкретику. В публичном эксперименте 2026 года текст Claude после удаления тире и «ИИ-фраз» стал выглядеть для Pangram **ещё более машинным**: было 94%, стало 100%.
- Детекторы сами нормализуют текст перед проверкой: все тире превращают в дефис, все кавычки — в одинаковые, «ё» — в «е», а невидимые символы и разметку вычищают. Типографские хитрости им просто не видны.
- Turnitin (с августа 2025) и GPTZero специально обучены на выходе популярных «очеловечивателей».
- Сработало в экспериментах другое: **голос реального автора** и **цикл «переписал → проверил детектором → переписал»**.

## Что сделано

1. **Измерено на данных.** 38 тысяч текстов людей и нейросетей из корпуса Сбера LLMTrace: 30+ моделей, включая GPT-4.1, o3, Gemini 2.5, GigaChat-Max и YandexGPT-5. Тексты сравнивались внутри одного жанра.
2. **Собраны исследования:** Science Advances (15 млн научных статей), PNAS, руководство Википедии по признакам ИИ-текста, RAID, NBER, опыты с Pangram, тесты русских детекторов.
3. **Сделаны инструменты:** сканер с нормами из корпуса, «отпечаток голоса» автора и локальная панель открытых детекторов для цикла проверки.

### Что выдаёт ИИ-текст (ИИ против людей, одни и те же жанры)

| | Русский | Английский |
|---|---|---|
| Разброс длины предложений (самый сильный признак в русском) | 0,38 против **0,55** | 0,37 против **0,48** |
| Короткие предложения (≤6 слов) | 9% против **19%** | 4% против **7%** |
| Отглагольные существительные на 1000 слов | **52** против 32 | **46** против 26 |
| «Я / мы» на 1000 слов | 13 против **17** | 10 против **22** |
| Числа на 1000 слов | 19 против **31** | 13 против **26** |
| Скобки на 1000 слов | 2,9 против **8,2** | 2,9 против **5,9** |
| Длинное тире | почти одинаково (5,5 против 5,1) — **в русском не признак** | слабый признак |
| Шаблоны | «подчёркивает важность»: 178 текстов ИИ, 0 у людей | «a testament to»: 688 против 2 |

Главный развенчанный миф: **в русском длинное тире не отличает ИИ от человека.** Сила различия 0,51 — уровень подброшенной монетки. Убирать тире из русского текста бесполезно.

## Эксперимент: до и после

Шесть текстов современных нейросетей из части корпуса, которую навык не видел. Каждый в трёх вариантах:
- **исходный**;
- **«косметика»** — что делают типичные очеловечиватели: тире → запятые, синонимы вместо «ИИ-слов», удаление «Таким образом» и разметки;
- **по навыку** — переписан по его методике, до двух кругов с проверкой.

Вероятность «это ИИ» по открытым детекторам (1,0 = точно ИИ, порог 0,5):

| Текст | Детектор | Исходный | «Косметика» | По навыку |
|---|---|---|---|---|
| RU статья (GigaChat-Max) | RuModernBERT / FRIDA | 1,00 / 1,00 | 1,00 / 1,00 | **0,08 / 0,002** |
| RU отзыв (YandexGPT-5) | RuModernBERT / FRIDA | 1,00 / 1,00 | 1,00 / 1,00 | **0,02 / 0,006** |
| RU заметка (YandexGPT-5, уже «очеловеченная» самой моделью) | RuModernBERT / FRIDA | 0,50 / 0,99 | 0,47 / 0,99 | **0,005 / 0,002** |
| EN статья (GPT-4.1) | DeBERTa (desklib) | 1,00 | 1,00 | **0,29** |
| EN отзыв (Gemini 2.5) | DeBERTa (desklib) | 0,99 | 0,96 | **0,30** |
| EN новость (Gemini 2.5) | DeBERTa (desklib) | 1,00 | 1,00 | **0,09** |

Дополнительно проверяли «нулевым» детектором Binoculars на маленьких моделях Qwen. Он слабый (сила различия 0,87 на русском и 0,73 на английском) и не поймал даже исходные тексты, поэтому в итог не входит; в панели он включается флагом `--binoculars`. Качество остальных детекторов на отложенной выборке: RuModernBERT 1,00 (ложно обвиняет 3,6% человеческих текстов), FRIDA 0,98 (12,5%), DeBERTa 0,95 (18% — его 0,5–0,7 считаем «не уверен»).

«Косметика» не сдвинула классификаторы ни на один текст. Переписывание по навыку перевело в «человека» все 6 текстов на всех классификаторах. Два текста потребовали второго круга. Исходники, косметика и результат лежат в `experiment/`.

**Честно о границах.** Это открытые детекторы, которые можно запустить у себя. Коммерческие (Pangram, Turnitin, GPTZero) обучены на большем объёме данных, и отдельно против них навык не проверялся. Гарантий «ни один детектор никогда» не даёт никто. У провайдеров бывают водяные знаки (Google SynthID) и логи, детекторы переобучаются, а на коротких текстах (меньше ~200 слов) ошибаются в обе стороны. Навык обещает то, что можно измерить.

## Что внутри

```
humanize-text/
├── SKILL.md                — порядок работы: опрос → диагностика → переписывание → цикл проверки → сдача
├── references/
│   ├── playbook.md         — все приёмы переписывания по порядку важности, с примерами до/после
│   ├── russian.md          — замеры по русскому, 160 «ИИ-слов» с множителями, что пишут люди, жанры
│   ├── english.md          — замеры по английскому + Science Advances, PNAS, Википедия, Pangram
│   ├── detectors.md        — как устроены детекторы и что на них реально влияет
│   └── sources.md          — все источники со ссылками
├── scripts/
│   ├── scan.py             — почему текст выглядит машинным: нормы, слова в контексте, две оценки
│   ├── voice.py            — «отпечаток голоса» автора по его старым текстам
│   ├── detect.py           — локальная панель детекторов (RU ×2, EN; Binoculars по флагу)
│   └── textstats.py        — общие признаки (те же, что в исследовании)
└── data/                   — нормы, словари, модели стиля, калибровка детекторов
research/                    — скрипты исследования (анализ корпуса, обучение, калибровка, эксперимент)
experiment/                  — тексты эксперимента: original / cosmetic / skill
```

## Установка

**Claude Code** — скопируй папку `humanize-text` в `~/.claude/skills/`:
```bash
cp -r humanize-text ~/.claude/skills/                                        # macOS / Linux
xcopy /E /I humanize-text "%USERPROFILE%\.claude\skills\humanize-text"      # Windows
```
**Claude.ai** — заархивируй папку `humanize-text` в zip и загрузи в настройках, в разделе навыков (Skills).
Другие агенты с поддержкой `SKILL.md` — положи папку в их каталог навыков.

Сканеру и «отпечатку голоса» ничего не нужно, кроме Python; для точной оценки русского поставь
`pip install pymorphy3 razdel` (нормы измерены с ними). Детекторы: `pip install onnxruntime tokenizers huggingface_hub`
для русского (модели ~75 МБ) и дополнительно `pip install torch transformers sentencepiece protobuf safetensors`
для английского (~1,7 ГБ). Модели скачаются при первом запуске.

## Как пользоваться

> Очеловечь этот текст, это эссе для блога, вот мои старые посты для стиля: …

> Rewrite this cover letter so it doesn't sound like ChatGPT

Отдельно:
```bash
python3 humanize-text/scripts/scan.py text.txt              # что выдаёт ИИ и где
python3 humanize-text/scripts/voice.py my_old_posts.txt     # голос автора
python3 humanize-text/scripts/detect.py text.txt            # что скажут детекторы
```

## Правила навыка

- Ничего не выдумывать: личные истории, цифры, цитаты и источники берутся только у автора.
- Никаких трюков с невидимыми символами, подменой букв и нарочными опечатками: детекторы их вычищают и специально ловят, а текст они портят.
- Где школа, журнал или работодатель требуют раскрывать использование ИИ, навык этого не отменяет.

## Данные и лицензии

Корпус LLMTrace (Sber, Apache-2.0) — https://huggingface.co/datasets/iitolstykh/LLMTrace_classification. Отсюда статистика, словари, модели стиля и тексты эксперимента. Детекторы: `toiletsandpaper/russian-ai-text-detector-*` (Apache-2.0 / MIT), `desklib/ai-text-detector-v1.01` (MIT), Qwen2.5-0.5B (Apache-2.0). Полный список источников — в `humanize-text/references/sources.md`.

---

<a id="english"></a>
## English

**humanize-text** is an Agent Skill (`SKILL.md`) that rewrites AI-generated text so it reads like a person wrote it — Russian and English — and checks the result with real open AI detectors in a rewrite–measure loop. Its rules come from measuring ~38k human vs AI texts (Sber's LLMTrace corpus, 30+ models, compared within the same genres) plus the research literature (Kobak et al. Science Advances 2025, Reinhart et al. PNAS 2025, Wikipedia's Signs of AI writing, RAID, NBER detector study, Pangram experiments).

Key findings:
- Surface edits don't move strong classifiers, and detectors normalise dashes, quotes and invisible characters anyway.
- What separates the two is rhythm (sentence-length variation), nominal style, missing first person, missing numbers and asides, and template phrases.
- The em dash is **not** a Russian tell (AUC 0.51) and only a weak English one.

In a held-out test, cosmetic "humanizing" left every open classifier at 0.96–1.00 AI; rewriting with the skill brought all six texts under 0.5 (0.002–0.30), two of them after a second detector-guided round.

Tools:
- `scan.py` — explains what reads as machine-made, against measured human norms, with two transparent scores (held-out AUC 0.92/0.95);
- `voice.py` — fingerprints the author's own writing;
- `detect.py` — runs two Russian classifiers and the top open English RAID model locally (Binoculars optional; weak at small size).

No guarantees against commercial detectors, watermarks or provider logs. The skill never invents personal facts and never uses character tricks.

## License

MIT
