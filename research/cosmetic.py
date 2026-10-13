"""What typical 'humanizers' do: kill dashes, swap AI words for synonyms, drop stock phrases and markdown."""
import re, sys, os
SWAP = {
 'ru': [(r'\bсвидетельствует о том, что\b','говорит о том, что'),(r'\bсвидетельствует о\b','говорит о'),(r'\bсвидетельствуют о\b','говорят о'),
        (r'\bдемонстрирует\b','показывает'),(r'\bдемонстрируют\b','показывают'),(r'\bявляется\b','—'),(r'\bключев(ой|ым|ая|ое|ые|ого|ую)\b',r'главн\1'),
        (r'\bвключая\b','в том числе'),(r'\bтакие как\b','например'),(r'\bзначительн(ые|ый|ая|ое|ых|ую)\b',r'больш\1'),(r'\bуникальн(ый|ая|ое|ые)\b',r'особ\1'),
        (r'\bспособствует\b','помогает'),(r'\bпредставляет собой\b','это'),(r'\bважн(ый|ым|ая|ое|ые|ого) шаг(ом)?\b','шаг')],
 'en': [(r'\bsignificant\b','big'),(r'\benhance\b','improve'),(r'\bcrucial\b','important'),(r'\btestament\b','proof'),(r'\bvibrant\b','lively'),
        (r'\bprofound\b','deep'),(r'\bshowcasing\b','showing'),(r'\bjourney\b','path'),(r'\butiliz(e|ing)\b',r'us\1'),(r'\bseamlessly\b','smoothly'),
        (r'\bbolster\b','boost'),(r'\brevolutionary\b','new'),(r'\bgroundbreaking\b','new'),(r'\binnovative\b','new'),(r'\bpivotal\b','key'),
        (r'\bpitfalls\b','mistakes'),(r'\bstreamline\b','simplify'),(r'\bembrace\b','accept'),(r'\bunprecedented\b','new'),(r'\bintricate\b','complex')],
}
DROP = {'ru': [r'\bТаким образом,\s*', r'\bВ заключение,\s*', r'\bВажно отметить, что\s*', r'\bКроме того,\s*', r'\bСтоит отметить, что\s*'],
        'en': [r'\bAdditionally,\s*', r'\bIn conclusion,\s*', r'\bUltimately,\s*', r'\bIt is worth noting that\s*', r'\bMoreover,\s*']}
for f in sorted(os.listdir('original')):
    lang = 'ru' if '_ru_' in f else 'en'
    t = open('original/'+f).read()
    t = t.replace('**','')
    t = re.sub(r'^\s*\d+\.\s+', '', t, flags=re.M)
    for a in DROP[lang]: t = re.sub(a, lambda m: '', t)
    t = re.sub(r'(?<=[.!?]\s)([а-яa-z])', lambda m: m.group(1).upper(), t)
    for a,b in SWAP[lang]: t = re.sub(a, b, t)
    t = t.replace(' — ', ', ').replace('—', ', ').replace(' – ', ', ')
    open('cosmetic/'+f,'w').write(t)
print('ok')
