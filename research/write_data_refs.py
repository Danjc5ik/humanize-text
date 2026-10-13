"""Render corpus findings into skill reference files (tables are generated, prose is in the templates)."""
import json, sys, os
F = json.load(open('findings/findings.json'))
SK = sys.argv[1]
LEX_AI = json.load(open(os.path.join(SK, 'data/lexicon_ai_favored.json')))
LEX_HU = json.load(open(os.path.join(SK, 'data/lexicon_human_favored.json')))
NAMES = {'sent_len_cv': 'sentence-length variation (CV)', 'sent_len_sd': 'sentence-length SD (words)', 'short_sent_share': 'share of sentences ≤6 words',
 'nominalizations': 'nominalizations /1k words', 'parentheses': 'brackets /1k', 'word_len': 'average word length', 'long_sent_share': 'share of sentences ≥30 words',
 'digits': 'numbers /1k', 'three_dots': '"..." /1k', 'starts_with_conj': 'sentences starting with And/But · И/Но/А', 'first_person': 'I/we · я/мы /1k',
 'second_person': 'you · ты/вы /1k', 'triads': 'lists of three /1k', 'exclamation': '! /1k', 'hyphen_as_dash': '" - " used as dash /1k', 'markdown': 'texts with markdown',
 'not_x_but_y': '"not X but Y" /1k', 'straight_quotes': 'straight quotes /1k', 'semicolon': '; /1k', 'mattr': 'lexical diversity (MATTR)', 'contractions': "contractions /1k",
 'em_dash': 'em dash — /1k', 'guillemets': '«» /1k', 'yo_per_1k_cyr': 'ё per 1000 Cyrillic letters', 'colon': ': /1k', 'list_lines_share': 'share of list lines',
 'question_mark': '? /1k', 'para_len_cv': 'paragraph-length variation', 'emoji': 'emoji /1k', 'question_sent_share': 'share of questions', 'en_dash_spaced': '" – " /1k',
 'curly_quotes': 'curly quotes /1k', 'curly_apostrophe': 'curly apostrophes /1k', 'ellipsis_char': '… /1k', 'sent_len_mean': 'mean sentence length', 'words': 'words'}
def feats_table(lang):
    rows = ["| Feature | Humans (mean) | AI (mean) | How well it separates (AUC*) | Texts that have it: humans / AI |", "|---|---|---|---|---|"]
    for x in F[f'features_{lang}']:
        if x['feature'] in ('words','para_len_cv','sent_len_mean'): continue
        auc = x['auc_ai_higher']; s = abs(auc-0.5)
        if s < 0.01: continue
        rows.append(f"| {NAMES.get(x['feature'], x['feature'])} | {x['human_mean']} | {x['ai_mean']} | {round(max(auc,1-auc),3)} ({'AI higher' if auc>0.5 else 'humans higher'}) | {int(x['share_human_nonzero']*100)}% / {int(x['share_ai_nonzero']*100)}% |")
    return "\n".join(rows)
def lex_table(lst, n):
    return "; ".join(f"{x['term']} ({x['ratio']}×)" if x['ratio']>=1 else f"{x['term']} ({round(1/x['ratio'],1)}×)" for x in lst[:n])
def models_table(lang):
    m = F[f'models_{lang}']; keys = ['sent_len_cv','short_sent_share','nominalizations','word_len','parentheses','digits']
    keys = [k for k in keys if k in m['HUMAN']]
    rows = ["| Source | " + " | ".join(NAMES[k] for k in keys) + " |", "|---|" + "---|"*len(keys)]
    for k in ['HUMAN'] + sorted(x for x in m if x != 'HUMAN'):
        rows.append(f"| {'**humans**' if k=='HUMAN' else k.split('/')[-1]} | " + " | ".join(str(m[k][c]) for c in keys) + " |")
    return "\n".join(rows)
out = {}
for lang, key in (('ru','ru'),('en','eng')):
    out[lang] = {'features': feats_table(key), 'models': models_table(key), 'ai': lex_table(LEX_AI[key], 160), 'human': lex_table(LEX_HU[key], 110), 'n': F[f'n_{key}']}
json.dump(out, open('findings/rendered.json','w'), ensure_ascii=False)
print(out['ru']['features'][:600]); print(out['en']['n'], out['ru']['n'])
