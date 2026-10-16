"""Optional local automatic subtitles: user installs faster-whisper separately."""
import json
from pathlib import Path

def stamp(seconds):
    ms=int(seconds*1000)
    h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def transcribe_file(path,*,model='tiny',device='cpu',language=None):
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError('Run pip install faster-whisper separately to enable optional captions') from exc
    engine=WhisperModel(model,device=device,compute_type='int8' if device=='cpu' else 'float16')
    segments, _=engine.transcribe(str(path),beam_size=3,language=language,word_timestamps=True,vad_filter=True)
    output=Path(path).with_suffix('.srt')
    with output.open('w',encoding='utf8') as fp:
        i=0
        for segment in segments:
            words=[w for w in (segment.words or []) if w.word.strip()]
            if words:
                # Dynamic 3-word groups are a readable editable starting point.
                for j in range(0,len(words),3):
                    group=words[j:j+3]
                    i+=1
                    fp.write(f'{i}\n{stamp(group[0].start)} --> {stamp(group[-1].end)}\n'
                             +''.join(w.word for w in group).strip()+'\n\n')
            else:
                i+=1
                fp.write(f'{i}\n{stamp(segment.start)} --> {stamp(segment.end)}\n{segment.text.strip()}\n\n')
    return str(output)
