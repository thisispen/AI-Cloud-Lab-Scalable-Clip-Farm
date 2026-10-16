"""Transcript-aware suggestions. Scores are heuristics, not evidence of virality."""
import json
import re
from pathlib import Path
from .core import probe

HOOK_TERMS={'how':2,'why':2,'actually':2,'but':1,'never':1,'instead':2,'mistake':3,
            'problem':2,'secret':2,'surprising':2,'nobody':2,'best':1,'worst':1,
            'stop':1,'because':1,'learned':2,'important':1,'truth':2}

def timestamp(s):
    matched=re.fullmatch(r'(\d+):(\d+):(\d+)[,.](\d+)',s.strip())
    if not matched:
        raise ValueError(f'Invalid subtitle timestamp: {s}')
    hours,minutes,sec,ms=matched.groups()
    return int(hours)*3600+int(minutes)*60+int(sec)+int(ms.ljust(3,'0')[:3])/1000

def parse_srt(path):
    content=Path(path).read_text(encoding='utf-8-sig')
    entries=[]
    for group in re.split(r'\n\s*\n',content.strip()):
        lines=group.strip().splitlines()
        if len(lines)<2:continue
        tm=next((line for line in lines if '-->' in line),None)
        if tm is None:continue
        start,end=[s.strip() for s in tm.split('-->')]
        entries.append((timestamp(start),timestamp(end),' '.join(lines[lines.index(tm)+1:])))
    return entries

def rank_srt(video,srt,*,seconds=30,count=12):
    meta=probe(video)
    sentences=parse_srt(srt)
    if seconds < 5 or count < 1:
        raise ValueError('Use at least 5 seconds and 1 candidate')
    if not sentences:
        raise ValueError('No subtitle entries')
    scored=[]
    # Candidate start points at actual word/sentence boundaries; ranking uses
    # language cues, not a made-up claim about probable video performance.
    for start,_,_ in sentences:
        end=min(meta['duration'],start+seconds)
        if end-start < seconds*0.7:
            continue
        words=' '.join(text for a,b,text in sentences if a < end and b>start).lower()
        normalized=re.findall(r"[\w']+",words)
        if not normalized:
            continue
        hits=sum(HOOK_TERMS.get(w,0) for w in normalized)
        first=' '.join(text for a,b,text in sentences if start<=a<start+4).lower()
        first_hits=sum(HOOK_TERMS.get(w,0) for w in re.findall(r"[\w']+",first))
        # Modest density constraint to avoid empty/dead-air candidates.
        density=min(1.0,len(normalized)/(max(end-start,1)*1.8))
        score=round(hits+first_hits*1.5+density*3,2)
        scored.append((score,start,end,first[:100]))
    scored.sort(key=lambda x:(-x[0],x[1]))
    selected=[]
    for score,a,b,preview in scored:
        if any(max(0,min(b,cc['end'])-max(a,cc['start']))/(b-a)>0.5 for cc in selected):
            continue
        selected.append({'id':f'highlight-{len(selected)+1:03d}','start':round(a,2),
                         'end':round(b,2),'title':preview,'heuristic_score':score,'approved':False})
        if len(selected)==count:break
    return {'schema_version':1,'source':str(Path(video).resolve()),'source_metadata':meta,
            'selection_method':'transcript keywords and density; NOT virality prediction; human review required',
            'rights_note':'Only use footage you own or are licensed to repurpose.', 'clips':selected}
