"""Offline-first batch video downloader and clipper CLI."""
import argparse
import json
from pathlib import Path
from .core import probe, suggest
from .fetch import fetch
from .render import render_manifest
from .captions import transcribe_file
from .accounts import export_account_queue
from .highlights import rank_srt

def main():
    p=argparse.ArgumentParser(description='Cloud Lab Clip Farm: licensed long-form video to shorts')
    sub=p.add_subparsers(dest='cmd',required=True)
    q=sub.add_parser('download',help='Stream authorized direct MP4/HTTP(S) media to disk')
    q.add_argument('--url',required=True);q.add_argument('--out',required=True)
    q.add_argument('--max-gb',type=float,default=10);q.add_argument('--rights-confirmed',action='store_true')
    q=sub.add_parser('inspect');q.add_argument('--input',required=True)
    q=sub.add_parser('suggest');q.add_argument('--input',required=True)
    q.add_argument('--out',default='data/clip-plan.json');q.add_argument('--min-seconds',type=float,default=15)
    q.add_argument('--max-seconds',type=float,default=45);q.add_argument('--count',type=int,default=12)
    q=sub.add_parser('rank-srt',help='Rank editable clip candidates from a transcript SRT (heuristics)')
    q.add_argument('--input',required=True);q.add_argument('--srt',required=True)
    q.add_argument('--seconds',type=int,default=30);q.add_argument('--count',type=int,default=12)
    q.add_argument('--out',default='data/highlight-plan.json')
    q=sub.add_parser('render');q.add_argument('--plan',required=True);q.add_argument('--outdir',default='exports/clipfarm')
    q.add_argument('--profile',choices=['shorts','reels','tiktok','horizontal','square'],default='shorts')
    q.add_argument('--mode',choices=['pad','crop'],default='pad')
    q.add_argument('--workers',type=int,default=1);q.add_argument('--threads',type=int,default=2)
    q.add_argument('--preview',action='store_true')
    q.add_argument('--fast-copy',action='store_true',help='Near-instant keyframe cuts; preserves original resolution/aspect and may be inexact')
    q=sub.add_parser('captions');q.add_argument('--input',required=True);q.add_argument('--model',default='tiny');q.add_argument('--language')
    q=sub.add_parser('accounts');q.add_argument('--manifest',required=True);q.add_argument('--accounts',required=True)
    q.add_argument('--out',default='exports/account-upload-queue.csv')
    args=p.parse_args()
    if args.cmd=='download':data={'downloaded':fetch(args.url,args.out,max_gb=args.max_gb,assert_rights=args.rights_confirmed)}
    elif args.cmd=='inspect':data=probe(args.input)
    elif args.cmd=='suggest':
        data=suggest(args.input,minimum=args.min_seconds,maximum=args.max_seconds,count=args.count)
        dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(data,indent=2),encoding='utf8')
        data={'plan':str(dest),'candidate_clips':len(data['clips']), 'review_required':True}
    elif args.cmd=='rank-srt':
        data=rank_srt(args.input,args.srt,seconds=args.seconds,count=args.count)
        dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(data,indent=2),encoding='utf8')
        data={'plan':str(dest),'highlight_candidates':len(data['clips']),'human_review_required':True}
    elif args.cmd=='render':
        data=render_manifest(args.plan,args.outdir,profile=args.profile,mode=args.mode,workers=args.workers,threads=args.threads,
                             preview=args.preview,require_approval=not args.preview,fast_copy=args.fast_copy)
    elif args.cmd=='captions':data={'srt':transcribe_file(args.input,model=args.model,language=args.language)}
    else:data={'queued_drafts':export_account_queue(args.manifest,args.accounts,args.out),'csv':args.out,'published':False}
    print(json.dumps(data,indent=2))

if __name__=='__main__':main()
