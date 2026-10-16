#!/usr/bin/env python3
"""Technical preflight for a rendered MP4. NOT a substitute for human creative review."""
import argparse
import json
from pathlib import Path
from studio.edit import media_info


def review(path: Path, layout: str, min_seconds=5, max_seconds=None):
    value = media_info(path)
    ratio = value["width"] / value["height"]
    target = {"vertical": 9 / 16, "horizontal": 16 / 9, "square": 1}[layout]
    issues = []
    if abs(ratio - target) > 0.012:
        issues.append("Aspect ratio mismatch")
    if value["duration_seconds"] < min_seconds:
        issues.append("Duration shorter than requested")
    if max_seconds and value["duration_seconds"] > max_seconds:
        issues.append("Duration longer than requested")
    if value["video_codec"] != "h264":
        issues.append("Video is not H.264 MP4")
    if not value["audio"]:
        issues.append("No audio stream; check whether this is intentional")
    return {"file": str(path), "technical_pass": not issues, "issues": issues, "media": value,
            "creative_review": "NOT PERFORMED — verify hook, pacing, brand fidelity, real-world claims, accessibility, captions, safe zones, media licenses, AI labels, and human approval"}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("file",type=Path);p.add_argument("--layout", choices=["vertical","horizontal","square"],default="vertical")
    p.add_argument("--min-seconds",type=float,default=5)
    p.add_argument("--max-seconds",type=float)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    result=review(a.file,a.layout,a.min_seconds,a.max_seconds)
    s=json.dumps(result,indent=2)
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(s+'\n',encoding="utf-8")
    print(s)
    if not result["technical_pass"]:
        raise SystemExit(2)

if __name__=='__main__':main()
