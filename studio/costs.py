#!/usr/bin/env python3
"""Offline price scenario calculator; metered generation is NEVER started."""
import argparse
import json

# Verify directly with the provider before authorizing payment. 2026-10-14 USD per second.
RATES = {
    "veo31_lite_720": 0.05,
    "veo31_fast_720": 0.10,
    "veo31_fast_1080": 0.12,
    "veo31_standard_1080": 0.40,
    "runway_gen4_turbo": 0.05,
    "runway_gen45": 0.12,
}
SOURCES = {
    "veo": "https://ai.google.dev/gemini-api/docs/pricing",
    "runway": "https://docs.dev.runwayml.com/guides/pricing/",
}

def estimate(model, total_final_seconds, attempts_per_accepted=2.0):
    if model not in RATES:
        raise ValueError("Unknown model")
    if total_final_seconds <= 0 or attempts_per_accepted < 1:
        raise ValueError("Seconds must be positive and attempts per accepted video >= 1")
    return round(RATES[model] * total_final_seconds * attempts_per_accepted, 2)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", choices=sorted(RATES), default="veo31_lite_720")
    ap.add_argument("--videos", type=int, default=1000)
    ap.add_argument("--seconds", type=float, default=15)
    ap.add_argument("--attempts", type=float, default=2, help="Mean generated seconds per accepted second, including retakes")
    args = ap.parse_args()
    if args.videos <= 0:
        ap.error("--videos must be positive")
    try:
        cost = estimate(args.model, args.videos * args.seconds, args.attempts)
    except ValueError as exc:
        ap.error(str(exc))
    print(json.dumps({"model": args.model, "videos": args.videos, "finished_seconds_each": args.seconds,
                      "attempts_multiplier": args.attempts, "generation_usd_estimate": cost,
                      "excludes": ["script", "images", "voice", "editing", "upscale", "storage", "tax"],
                      "warning": "Price scenario only; no API invoked. Verify current official prices before purchase.",
                      "sources": SOURCES}, indent=2))

if __name__ == "__main__":
    main()
