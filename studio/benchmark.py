#!/usr/bin/env python3
"""Blind/manual quality benchmark log. No paid generation or telemetry collection.

Evaluation set should use identical prompts/reference images, a fixed resolution,
reported seeds/settings and blinded human comparisons. Do not auto-switch models
based on a handful of ratings.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

FIELDS=['model','test_case_id','score_1_to_10','accepted','generated_seconds','usd_charged','notes']


def record(path, model, test_case_id, score, accepted, generated_seconds, usd_charged, notes=''):
    if not model or not test_case_id or not 1 <= score <= 10 or generated_seconds <= 0 or usd_charged < 0:
        raise ValueError('Invalid benchmark rating or cost')
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    add_header=not p.exists() or p.stat().st_size==0
    with p.open('a',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        if add_header:w.writeheader()
        w.writerow({'model':model,'test_case_id':test_case_id,'score_1_to_10':score,
                    'accepted':int(accepted),'generated_seconds':generated_seconds,
                    'usd_charged':usd_charged,'notes':notes})


def summarize(path, minimum_trials=10):
    data=defaultdict(list)
    with Path(path).open(newline='',encoding='utf-8') as f:
        for row in csv.DictReader(f):data[row['model']].append(row)
    stats=[]
    for model,rows in data.items():
        n=len(rows); acc=sum(int(x['accepted']) for x in rows)
        spent=sum(float(x['usd_charged']) for x in rows)
        sec=sum(float(x['generated_seconds']) for x in rows)
        stats.append({'model':model,'tests':n,
                      'ready_for_cost_quality_comparison':n>=minimum_trials,
                      'acceptance_rate':round(acc/n,3),
                      'mean_human_score':round(sum(float(x['score_1_to_10']) for x in rows)/n,2),
                      'total_usd_logged':round(spent,2),
                      'usd_per_accepted_attempt':round(spent/acc,3) if acc else None,
                      'usd_per_generated_second':round(spent/sec,4) if sec else None})
    return {'minimum_trials_per_model':minimum_trials,'models':sorted(stats,key=lambda x:x['model']),
            'warning':'Small or unmatched samples are not evidence a model is best. Prefer blinded paired tests and real retention/conversion on your own channels.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='action',required=True)
    rec=sub.add_parser('record');rec.add_argument('--file',default='data/creative_benchmarks.csv')
    rec.add_argument('--model',required=True);rec.add_argument('--test-case-id',required=True)
    rec.add_argument('--score',type=int,required=True);rec.add_argument('--accepted',action='store_true')
    rec.add_argument('--seconds',type=float,required=True);rec.add_argument('--usd',type=float,required=True)
    rec.add_argument('--notes',default='')
    rpt=sub.add_parser('report');rpt.add_argument('--file',default='data/creative_benchmarks.csv')
    rpt.add_argument('--minimum-trials',type=int,default=10)
    a=p.parse_args()
    if a.action=='record':record(a.file,a.model,a.test_case_id,a.score,a.accepted,a.seconds,a.usd,a.notes)
    else:print(json.dumps(summarize(a.file,a.minimum_trials),indent=2))
if __name__=='__main__':main()
