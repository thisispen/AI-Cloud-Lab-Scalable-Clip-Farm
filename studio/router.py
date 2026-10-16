#!/usr/bin/env python3
"""Conservative, read-only tool selector; NO video generation or money spent.

Rank *known pricing*, show gaps, and require human judgment for quality. Do not
claim a vendor is the best without comparable blind creative benchmarks.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_data(catalog_path=None, policy_path=None):
    c = json.loads(Path(catalog_path or ROOT / "catalog.json").read_text(encoding="utf-8"))
    p = json.loads(Path(policy_path or ROOT / "policy.json").read_text(encoding="utf-8"))
    return c, p


def plan(platform, ai_seconds=5.0, attempts=2.0, catalog=None, policy=None):
    if ai_seconds < 0 or attempts < 1:
        raise ValueError("ai_seconds must be >= 0 and attempts >= 1")
    catalog, policy = (catalog, policy) if catalog is not None and policy is not None else load_data()
    if platform not in catalog["platforms"]:
        raise ValueError("Unsupported platform")
    spec = catalog["platforms"][platform]
    workflow = spec["workflow"]
    models = []
    for x in catalog["generation_models"]:
        if workflow not in x["capabilities"]:
            continue
        rate = x["usd_per_generated_second"]
        est = None if rate is None else round(ai_seconds * attempts * rate, 2)
        models.append({"id":x["id"], "price_usd_per_second":rate,
                       "estimated_generation_usd_per_video":est,
                       "requires_connection":not x["connected"],
                       "blocked_until_approval":bool(x["requires_paid_approval"] and not policy["paid_apis_enabled"]),
                       "creative_quality":"NOT BENCHMARKED — human review required",
                       "source":x["official_pricing"]})
    models.sort(key=lambda x:(x["estimated_generation_usd_per_video"] is None,
                              x["estimated_generation_usd_per_video"] if x["estimated_generation_usd_per_video"] is not None else float("inf"), x["id"]))
    editors = [{"id":x["id"], "monthly_usd_published":x["monthly_usd"],
                "automation":x["automation"],
                "included_in_codespace":x["included_in_codespace"],
                "requires_approval":bool(x.get("requires_paid_approval",False))}
               for x in catalog["editors"] if workflow in x["best_for"] or "batch" in x["best_for"]]
    editors.sort(key=lambda x:(x["monthly_usd_published"],not x["included_in_codespace"],x["id"]))
    return {"platform":platform,"layout":spec["layout"],"workflow":workflow,
            "ai_seconds_per_video":ai_seconds,"retake_multiplier":attempts,
            "generation_candidates_lowest_listed_price_first":models,
            "editing_candidates_lowest_subscription_first":editors,
            "plan_recommendation":"FFmpeg automation first; creative review and finishing by human or licensed GUI editor",
            "permission_state":{"paid_apis_enabled":policy["paid_apis_enabled"],
                                "automated_purchases_enabled":policy["automated_purchases_enabled"],
                                "production_auto_publish_enabled":policy["production_auto_publish_enabled"]},
            "warning":"Cheapest published price is not the best quality. Revalidate pricing and run controlled output tests."}


def main():
    c, p = load_data()
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--platform", choices=sorted(c["platforms"]), default="tiktok")
    ap.add_argument("--ai-seconds", type=float, default=5)
    ap.add_argument("--attempts", type=float, default=2)
    ap.add_argument("--out", help="Optional path for the read-only decision report")
    args=ap.parse_args()
    try: result=plan(args.platform,args.ai_seconds,args.attempts,c,p)
    except ValueError as ex: ap.error(str(ex))
    data=json.dumps(result,indent=2)
    if args.out:
        dst=Path(args.out);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(data+"\n",encoding="utf-8")
    print(data)


if __name__ == "__main__":main()
