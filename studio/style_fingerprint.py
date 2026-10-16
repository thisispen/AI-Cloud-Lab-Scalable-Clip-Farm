#!/usr/bin/env python3
"""Read-only analysis of a LOCAL video you own/have permission to study.

Computes rough edit cadence with FFmpeg scene-change detection; never downloads,
clones, strips DRM, reconstructs source projects or captures protected streams.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path
from .edit import media_info


def fingerprint(source, sample_seconds=90, scene_threshold=0.35):
    source=Path(source)
    if not source.is_file():raise FileNotFoundError(source)
    if sample_seconds<=0 or not 0<scene_threshold<1:raise ValueError('Invalid sample/threshold')
    meta=media_info(source)
    seconds=min(meta['duration_seconds'],sample_seconds)
    # Showinfo returns a line for each selected scene-change frame.
    cmd=['ffmpeg','-nostdin','-hide_banner','-i',str(source),'-t',str(seconds),
         '-vf',f"select='gt(scene,{scene_threshold})',showinfo",'-an','-f','null','-']
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=180,check=False)
    if proc.returncode:raise RuntimeError('Scene analysis failed: '+proc.stderr[-250:])
    timestamps=[float(m.group(1)) for m in re.finditer(r'\bpts_time:([0-9]+(?:\.[0-9]+)?)',proc.stderr)]
    cuts=len(timestamps)
    return {'source':str(source),'duration_seconds':round(meta['duration_seconds'],2),
            'analyzed_seconds':round(seconds,2),
            'aspect_ratio':round(meta['width']/meta['height'],3),
            'width':meta['width'],'height':meta['height'],
            'audio_track_present':meta['audio'],
            'approximate_detected_scene_cuts':cuts,
            'approximate_mean_shot_seconds':round(seconds/(cuts+1),2),
            'cut_timestamps_seconds':[round(x,2) for x in timestamps[:200]],
            'warning':'Scene threshold is heuristic: dissolves, motion, flashes and compression can distort cut counts. This does not measure creative quality, hook, rights, watch time or conversions.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('local_video');p.add_argument('--sample-seconds',type=float,default=90)
    p.add_argument('--threshold',type=float,default=0.35)
    p.add_argument('--out')
    a=p.parse_args()
    x=json.dumps(fingerprint(a.local_video,a.sample_seconds,a.threshold),indent=2)
    if a.out:
        f=Path(a.out);f.parent.mkdir(parents=True,exist_ok=True);f.write_text(x+'\n',encoding='utf-8')
    print(x)
if __name__=='__main__':main()
