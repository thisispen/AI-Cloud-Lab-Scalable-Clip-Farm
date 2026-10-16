"""Inspect a source video and suggest non-semantic cut points.

Silence/time based suggestions do not claim a clip is entertaining. For high quality,
review the editable manifest or use an optional transcription/ranking stage.
"""
import json
import re
import subprocess
from pathlib import Path


def command(args):
    return subprocess.run(args, capture_output=True, text=True, check=True)


def probe(path):
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(path)
    raw = command(['ffprobe', '-v', 'error', '-show_entries',
                   'format=duration,size:stream=index,codec_type,width,height',
                   '-of', 'json', str(p)])
    data = json.loads(raw.stdout)
    video = next((s for s in data.get('streams', []) if s['codec_type']=='video'), None)
    if not video:
        raise ValueError('A source with video is required')
    return {'file':str(p.resolve()), 'duration':float(data['format']['duration']),
            'bytes':int(data['format'].get('size',0)),
            'width':video.get('width',0),'height':video.get('height',0),
            'has_audio':any(s['codec_type']=='audio' for s in data.get('streams', []))}


def silence_boundaries(path, *, duration):
    if not probe(path)['has_audio']:
        return []
    proc = subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', '-i', str(path),
         '-vn', '-af', 'silencedetect=noise=-32dB:d=0.45', '-f', 'null', '-'],
         capture_output=True,text=True)
    if proc.returncode:
        return []
    starts=[float(x) for x in re.findall(r'silence_start:\s*([\d.]+)',proc.stderr)]
    ends=[float(x) for x in re.findall(r'silence_end:\s*([\d.]+)',proc.stderr)]
    # Use the boundary inside or at the end of silence as a possible clean edit point.
    candidates = [0.0, duration] + [min(duration,max(0.0,v)) for v in ends+starts]
    return sorted(set(round(x,2) for x in candidates))


def suggest(path, *, minimum=15, maximum=45, count=12):
    meta=probe(path)
    if minimum <=0 or maximum < minimum or count < 1:
        raise ValueError('Expected minimum > 0, maximum >= minimum and count >= 1')
    duration=meta['duration']
    boundaries = silence_boundaries(path,duration=duration)
    results=[]
    if duration<=maximum:
        starts=[0.0]
    else:
        # Evenly sample the timeline. Shift endpoints toward nearby silence to
        # avoid cutting in the middle of sentences whenever possible.
        extent=max(0.0,duration-maximum)
        n=min(count,max(1,int(duration/minimum)))
        starts=[extent*(i/(n-1)) if n>1 else 0.0 for i in range(n)]
    for i,start in enumerate(starts):
        end=min(duration,start+maximum)
        # Bias end toward silences around the target but never too-short clips.
        valid=[v for v in boundaries if start+minimum<=v<=end and abs(v-end)<=4]
        if valid:
            end=min(valid,key=lambda v:abs(v-end))
        if end-start < min(minimum,duration):
            continue
        results.append({'id':f'clip-{i+1:03d}', 'start':round(start,2),
                        'end':round(end,2), 'title':'Review this candidate',
                        'approved':False})
    return {'schema_version':1, 'source':str(Path(path).resolve()),
            'source_metadata':meta, 'rights_note':'Use only videos you own or are licensed to transform.',
            'selection_method':'time-and-silence heuristic; human review required',
            'clips':results}
