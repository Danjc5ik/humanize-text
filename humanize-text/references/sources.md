# Sources

## Own measurements (this skill)
- LLMTrace classification corpus (Sber / SberDevices, 2025), test + validation splits:
  https://huggingface.co/datasets/iitolstykh/LLMTrace_classification · paper https://arxiv.org/abs/2509.21269
  Balanced by genre; features, lexicons, style model and detector calibration in `data/`.

## Large studies
- Kobak, González-Márquez, Horvát, Lause. *Delving into LLM-assisted writing in biomedical publications
  through excess vocabulary.* Science Advances 11(27), 2025. https://arxiv.org/abs/2406.07016
- Reinhart et al. *Do LLMs write like humans? Variation in grammatical and rhetorical styles.* PNAS, Feb 2025.
  https://arxiv.org/abs/2410.16107
- Liang et al. *GPT detectors are biased against non-native English writers.* Patterns, 2023. https://arxiv.org/abs/2304.02819
- Krishna et al. *Paraphrasing evades detectors of AI-generated text, but retrieval is an effective defense.*
  NeurIPS 2023. https://arxiv.org/abs/2303.13408
- Dugan et al. *RAID: A Shared Benchmark for Robust Evaluation of Machine-Generated Text Detectors.* ACL 2024.
  https://arxiv.org/abs/2405.07940
- Hans et al. *Spotting LLMs With Binoculars: Zero-Shot Detection of Machine-Generated Text.* ICML 2024.
  https://arxiv.org/abs/2401.12070
- Venkatraman, Uchendu, Lee. *GPT-who: An Information Density-based Machine-Generated Text Detector.* NAACL Findings 2024.
  https://arxiv.org/abs/2310.06202
- Dathathri et al. *Scalable watermarking for identifying large language model outputs* (SynthID-Text). Nature, 2024.
- Robustness of SynthID-Text to paraphrase/translation: https://arxiv.org/html/2508.20228v1
- Paech et al. *Antislop: A Comprehensive Framework for Identifying and Eliminating Repetitive Patterns in
  Language Models.* ICLR 2026. https://arxiv.org/abs/2510.15061
- Jabarian & Imas. *Artificial Writing and Automated Detection.* NBER w34223 / BFI WP 2025-116.
  https://www.nber.org/papers/w34223
- Tolstykh et al. *GigaCheck: Detecting LLM-generated Content.* https://arxiv.org/abs/2410.23728
- Batura et al. *AINL-Eval 2025 Shared Task: Detection of AI-Generated Scientific Abstracts in Russian.*
  https://arxiv.org/abs/2508.09622

## Guides and catalogues
- Wikipedia: Signs of AI writing (WikiProject AI Cleanup): https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- Pangram — how it works: https://www.pangram.com/blog/how-does-pangram-work · Claude writing styles:
  https://www.pangram.com/blog/claude-writing-styles
- GPTZero — technology, paraphraser shield, AI vocabulary: https://gptzero.me/technology ·
  https://gptzero.me/ai-vocabulary
- Turnitin AI bypasser detection (Aug 2025): https://www.plagiarismtoday.com/2025/08/27/turnitin-launches-anti-ai-humanizer-feature/
- «Антиплагиат», памятка по сгенерированным текстам: https://antiplagiat.ru/wp-content/uploads/2024/09/ai-manual.pdf
- OpenAI em dash fix (Nov 2025): https://www.techcrunch.com/2025/11/14/openai-says-its-fixed-chatgpts-em-dash-problem/

## Experiments and reviews
- LessWrong: *Pangram AI detection software can be evaded* (2026):
  https://www.lesswrong.com/posts/hrpQxfYvF6CBGWfJX/pangram-ai-detection-software-can-be-evaded
- HackerNoon: *I asked Claude Opus 5 to beat Pangram's AI detector — it failed with a perfect score*:
  https://hackernoon.com/i-asked-claude-opus-5-to-beat-pangrams-ai-detector-it-failed-with-a-perfect-score
- Habr: test of Яндекс Нейродетектор, GigaCheck, Text.ru, GPTZero on Russian texts (2026):
  https://habr.com/ru/articles/1065544/
- vc.ru, Илья Утов: 44 и 55 маркеров нейросетевого текста: https://vc.ru/ai/2856452-kak-raspoznat-neyrosetevoy-tekst ·
  https://vc.ru/ai/2936857-markery-neurosetevogo-teksta
- humanizer-ru (MIT), Russian marker catalogue tested on AINL-Eval 2025 and LLMTrace: https://github.com/ilyautov/humanizer-ru
- blader/humanizer (English skill based on the Wikipedia catalogue): https://github.com/blader/humanizer

## Open detectors used in `scripts/detect.py`
- https://huggingface.co/toiletsandpaper/russian-ai-text-detector-modernbert (Apache-2.0)
- https://huggingface.co/toiletsandpaper/russian-ai-text-detector-mini-frida (MIT)
- https://huggingface.co/desklib/ai-text-detector-v1.01 (MIT)
- https://huggingface.co/Qwen/Qwen2.5-0.5B and -Instruct (Apache-2.0), used as a Binoculars pair
