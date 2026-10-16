#!/usr/bin/env python3
"""Conservative mixed-media cost planner; calculator only, NO billing or API calls."""
import argparse
import json

R2_PER_GB_MONTH=0.015
R2_FREE_GB_MONTH=10

def estimate(videos=1000,final_seconds=30,generated_seconds=5,attempts=2,
             usd_per_ai_second=0.05,storage_gb=100,editor_subscription=0,other_usd=0):
    if (videos < 1 or final_seconds <= 0 or not 0 <= generated_seconds <= final_seconds or
        attempts < 1 or usd_per_ai_second < 0 or storage_gb < 0 or editor_subscription < 0 or other_usd < 0):
        raise ValueError("Invalid inputs (generated seconds cannot exceed finished duration)")
    generation = videos * generated_seconds * attempts * usd_per_ai_second
    storage = max(0, storage_gb - R2_FREE_GB_MONTH) * R2_PER_GB_MONTH
    expenses={"generation_usd":round(generation,2),
              "storage_usd_per_month_estimate":round(storage,2),
              "optional_editor_subscription_usd_per_month":round(editor_subscription,2),
              "other_manual_budget_usd":round(other_usd,2)}
    total=sum(expenses.values())
    return {"videos":videos,"final_seconds_each":final_seconds,
            "unique_ai_seconds_each":generated_seconds,"retake_multiplier":attempts,
            "generated_seconds_to_purchase":round(videos*generated_seconds*attempts,2),
            "expenses":expenses,"illustrative_first_month_total_usd":round(total,2),
            "illustrative_cost_per_finished_video_usd":round(total/videos,3),
            "excluded":"Video subscriptions/credits limitations, actual editing compute, stock licensing, sound/voice, FX, tax, GPU/VM charges, R2 operation charges and approvals. No assets actually generated.",
            "sources":["https://ai.google.dev/gemini-api/docs/pricing", "https://developers.cloudflare.com/r2/pricing/"]}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--videos',type=int,default=1000)
    ap.add_argument('--final-seconds',type=float,default=30)
    ap.add_argument('--generated-seconds',type=float,default=5)
    ap.add_argument('--attempts',type=float,default=2)
    ap.add_argument('--usd-per-ai-second',type=float,default=0.05)
    ap.add_argument('--storage-gb',type=float,default=100)
    ap.add_argument('--editor-subscription',type=float,default=0)
    ap.add_argument('--other-usd',type=float,default=0)
    args=ap.parse_args()
    try: res=estimate(args.videos,args.final_seconds,args.generated_seconds,args.attempts,
                      args.usd_per_ai_second,args.storage_gb,args.editor_subscription,args.other_usd)
    except ValueError as ex:ap.error(str(ex))
    print(json.dumps(res,indent=2))

if __name__=='__main__':main()
