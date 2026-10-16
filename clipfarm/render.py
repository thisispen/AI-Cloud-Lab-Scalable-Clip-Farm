"""Bulk FFmpeg reframe/encode. Videos are saved privately, never published."""
import concurrent.futures
import json
import os
import re
import subprocess
from pathlib import Path
from .core import probe

PROFILES={
    'shorts':(720,1280), 'reels':(720,1280), 'tiktok':(720,1280),
    'horizontal':(1280,720), 'square':(720,720),
}

def safe(name):
    return re.sub(r'[^a-zA-Z0-9_-]','_',name)[:64]


def render_one(src,clip,out,*,profile='shorts',mode='pad',threads=2,preview=False,fast_copy=False):
    if profile not in PROFILES or mode not in {'pad','crop'}:
        raise ValueError('Unknown profile or framing mode')
    a,b=float(clip['start']),float(clip['end'])
    if a<0 or b<=a:
        raise ValueError('Invalid clip boundaries')
    dest=Path(out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    if fast_copy:
        # Super-cheap keyframe-aligned extraction. Does not resize, caption or
        # promise exact cuts; requires a platform-compatible source already.
        args=['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y',
              '-ss',str(a),'-i',str(src),'-t',str(b-a),
              '-map','0:v:0','-map','0:a:0?',
              '-c','copy','-avoid_negative_ts','make_zero',
              '-movflags','+faststart',str(dest)]
        subprocess.run(args,check=True,capture_output=True,text=True)
        return {'id':clip['id'],'path':str(dest),'size_bytes':dest.stat().st_size,
                'duration_target':round(b-a,2),'fast_copy_keyframe_approximation':True}
    w,h=PROFILES[profile]
    frame=f'scale={w}:{h}:force_original_aspect_ratio={"decrease" if mode=="pad" else "increase"}'
    frame+=f',pad={w}:{h}:(ow-iw)/2:(oh-ih)/2' if mode=='pad' else f',crop={w}:{h}'
    if preview:
        # Cheap non-uploadable preview with smaller output for review.
        w,h=w//2,h//2
        frame=f'scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2'
    args=['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y',
          '-ss',str(a),'-i',str(src),'-t',str(b-a),'-vf',frame,
          '-c:v','libx264','-preset','veryfast','-crf','25' if preview else '23',
          '-pix_fmt','yuv420p','-threads',str(threads),
          '-c:a','aac','-b:a','96k' if preview else '128k',
          '-movflags','+faststart',str(dest)]
    subprocess.run(args,check=True,capture_output=True,text=True)
    return {'id':clip['id'],'path':str(dest),'size_bytes':dest.stat().st_size,'duration':round(b-a,2)}


def render_manifest(manifest,outdir,*,profile='shorts',mode='pad',workers=1,
                    threads=2,preview=False,require_approval=True,fast_copy=False):
    plan=json.loads(Path(manifest).read_text(encoding='utf8'))
    src=plan['source']
    meta=probe(src)
    clips=plan['clips']
    if workers<1 or workers>8 or threads<1 or threads>32:
        raise ValueError('Set workers in 1..8, threads in 1..32')
    if require_approval and not preview and any(not c.get('approved') for c in clips):
        raise PermissionError('Review/edit manifest and set approved: true for each clip before final rendering; or use --preview')
    if any(c['start']<0 or c['end']>meta['duration']+0.2 for c in clips):
        raise ValueError('Clip exceeds source duration')
    output=Path(outdir)
    output.mkdir(parents=True,exist_ok=True)
    def task(c):
        name=safe(c['id'])+('-preview' if preview else '')+'.mp4'
        return render_one(src,c,output/name,profile=profile,mode=mode,threads=threads,preview=preview,fast_copy=fast_copy)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        finished=list(pool.map(task,clips))
    artifact={'profile':profile,'mode':mode,'preview':preview,'fast_copy':fast_copy,'outputs':finished,
              'distribution_status':'not_published','requires_rights_and_human_review':True}
    (output/'manifest.json').write_text(json.dumps(artifact,indent=2),encoding='utf8')
    return artifact
