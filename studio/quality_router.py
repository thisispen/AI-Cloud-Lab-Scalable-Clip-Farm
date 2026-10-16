#!/usr/bin/env python3
"""Controlled, evidence-based recommendation from manually scored paired trials.

Uses *common test cases* to avoid comparing unequal creative briefs. It never
changes defaults or executes any provider. If no sufficient evidence, say so.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def propose(csv_path, min_common_cases=10, min_mean_score=7.0, goal='lowest_cost'):
    if goal not in ('lowest_cost','highest_quality'):raise ValueError('Unknown goal')
    if min_common_cases<1 or not 1<=min_mean_score<=10:raise ValueError('Invalid thresholds')
    samples=defaultdict(dict)
    with Path(csv_path).open(newline='',encoding='utf-8') as f:
        for r in csv.DictReader(f):
            try:
                row={'score':float(r['score_1_to_10']),
                     'accepted':int(r['accepted']),'usd':float(r['usd_charged'])}
                if not 1<=row['score']<=10 or row['accepted'] not in (0,1) or row['usd']<0:
                    raise ValueError('Malformed benchmark observation')
            except (ValueError, KeyError) as ex:raise ValueError(f'Malformed benchmark row: {ex}') from ex
            # A repeat for the same model / test case is treated as an attempt and
            # charged in the accumulated cost, not a replacement for a poor attempt.
            samples[r['model']].setdefault(r['test_case_id'],[]).append(row)
    ids=set.intersection(*(set(s) for s in samples.values())) if samples else set()
    if len(samples)<2 or len(ids)<min_common_cases:
        return {'proposal':None,'reason':'At least 2 models and enough COMMON creative test cases are required',
                'models':len(samples),'common_cases':len(ids),'automatic_switch':False}
    results=[]
    for model,tests in samples.items():
        all_attempts=[a for i in ids for a in tests[i]]
        mean=sum(x['score'] for x in all_attempts)/len(all_attempts)
        accepted=sum(x['accepted'] for x in all_attempts)
        cost=sum(x['usd'] for x in all_attempts)
        cost_per_accepted=cost/accepted if accepted else None
        results.append({'model':model,'matched_cases':len(ids),'attempts':len(all_attempts),
                        'mean_score':round(mean,2),
                        'acceptance_rate':round(accepted/len(all_attempts),3),
                        'usd_per_accepted_output':round(cost_per_accepted,4) if cost_per_accepted is not None else None,
                        'passes_quality_floor':mean>=min_mean_score and accepted>0})
    eligible=[x for x in results if x['passes_quality_floor']]
    if goal=='lowest_cost':
        eligible.sort(key=lambda x:(x['usd_per_accepted_output'], -x['mean_score'], x['model']))
    else:
        eligible.sort(key=lambda x:(-x['mean_score'],x['usd_per_accepted_output'],x['model']))
    return {'proposal':eligible[0]['model'] if eligible else None,
            'objective':goal,'quality_floor':min_mean_score,
            'matched_creative_test_cases':len(ids), 'model_comparisons':results,
            'automatic_switch':False,
            'must_review':'Statistical noise, actual content performance, licensing, capabilities, privacy, provider costs, resolution and human approval before switching.',
            'warning':'Mean human rating is not measured conversion or virality; price only includes the manually logged attempts.'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--file',default='data/creative_benchmarks.csv')
    ap.add_argument('--min-paired-prompts',type=int,default=10)
    ap.add_argument('--minimum-score',type=float,default=7.0)
    ap.add_argument('--goal',choices=('lowest_cost','highest_quality'),default='lowest_cost')
    args=ap.parse_args()
    print(json.dumps(propose(args.file,args.min_paired_prompts,args.minimum_score,args.goal),indent=2))

if __name__=='__main__':main()
