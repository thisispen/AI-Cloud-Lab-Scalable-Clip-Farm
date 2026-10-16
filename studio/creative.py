#!/usr/bin/env python3
"""Generate an editable, claim-safe creative brief and shot plan. No paid API calls."""
import argparse
import json
import re
from pathlib import Path

PROFILES = {
    "tiktok": {"ratio": "9:16", "width": 1080, "height": 1920, "default_seconds": 25, "label": "TikTok"},
    "instagram_reels": {"ratio": "9:16", "width": 1080, "height": 1920, "default_seconds": 25, "label": "Instagram Reels"},
    "facebook_reels": {"ratio": "9:16", "width": 1080, "height": 1920, "default_seconds": 25, "label": "Facebook Reels"},
    "facebook_ad": {"ratio": "9:16", "width": 1080, "height": 1920, "default_seconds": 30, "label": "Facebook Reels Ad"},
    "youtube_short": {"ratio": "9:16", "width": 1080, "height": 1920, "default_seconds": 30, "label": "YouTube Short"},
    "youtube_long": {"ratio": "16:9", "width": 1920, "height": 1080, "default_seconds": 360, "label": "YouTube long-form"},
}

# Editing guidance, not algorithmic claims about retention.
HOOKS = {
    "curiosity": "Show a surprising result first, then pose a question about {topic}.",
    "problem": "Open with a recognizable frustration involving {topic}; don't exaggerate.",
    "demonstration": "Begin with a verifiable visual demonstration of {topic}.",
}


def safe_name(value):
    v = re.sub(r"[^a-z0-9-]+", "-", value.lower().strip()).strip("-")
    return (v[:64] or "untitled")


def plan(name: str, platform: str, topic: str, audience: str, goal: str,
         seconds: int, offer: str = "", proof: str = "", cta: str = "Learn more", style: str = "cinematic-realistic") -> dict:
    if platform not in PROFILES:
        raise ValueError("Unknown platform")
    if seconds < 5 or seconds > 3600:
        raise ValueError("Duration must be between 5 and 3600 seconds")
    if any(not x.strip() for x in [name, topic, audience, goal]):
        raise ValueError("Name, topic, audience and goal cannot be empty")
    profile = PROFILES[platform]
    if platform == "youtube_long":
        beats = [("cold_open", 0, .04), ("promise", .04, .09), ("setup", .09, .22),
                 ("development", .22, .72), ("payoff", .72, .92), ("next_step", .92, 1)]
    else:
        beats = [("hook", 0, .14), ("context", .14, .32), ("evidence", .32, .75),
                 ("payoff", .75, .88), ("cta", .88, 1)]
    shots = []
    for index, (purpose, start, end) in enumerate(beats, 1):
        shots.append({
            "number": index,
            "beat": purpose,
            "start_s": round(start * seconds, 1),
            "end_s": round(end * seconds, 1),
            "visual_intent": f"Show a concrete, relevant {purpose.replace('_',' ')} for {topic}.",
            "ai_video_prompt": (
                f"{style} visual about {topic}. Beat: {purpose.replace('_', ' ')}. "
                "One clear action, consistent subject identity and setting, deliberate camera movement, "
                f"composition for {profile['ratio']}. No fake logos, no unrequested on-screen text. "
                "Preserve realistic object physics and continuity across shots."
            ),
            "source": "GENERATE_OR_SUPPLY", "asset_path": "", "approved": False
        })
    project = {
        "schema_version": "1.0",
        "title": name, "platform": platform, "dimensions": [profile["width"], profile["height"]],
        "duration_seconds": seconds, "topic": topic, "audience": audience, "goal": goal,
        "offer": offer, "proof_supplied": proof, "cta": cta, "style": style,
        "hooks": [{"angle": k, "copy_direction": v.format(topic=topic)} for k, v in HOOKS.items()],
        "claims_policy": "Do not fabricate product performance, outcomes, reviews, endorsements or statistics. Verify claims and usage rights.",
        "shots": shots, "status": "CREATIVE_DRAFT_REQUIRES_REVIEW",
        "distribution": {"publish_automatically": False, "paid_ads_enabled": False},
        "references_needed": ["Brand kit", "Verified product facts", "Approved reference images", "Asset/music permissions"],
    }
    return project


def render_board(p: dict) -> str:
    lines = [f"# {p['title']} — {PROFILES[p['platform']]['label']}", "",
             f"Audience: {p['audience']}", f"Goal: {p['goal']}",
             f"Length: {p['duration_seconds']} s; export {p['dimensions'][0]}×{p['dimensions'][1]}",
             f"Offer: {p['offer'] or '[not supplied]'}", f"CTA: {p['cta']}",
             f"Evidence / substantiation: {p['proof_supplied'] or '[NOT SUPPLIED; no claims may be invented]'}", "",
             "## Alternative hooks (choose one)", ""]
    lines.extend(f"- **{h['angle']}** — {h['copy_direction']}" for h in p['hooks'])
    lines.extend(["", "## Shot list (draft; artistic timings are editable)", ""])
    for s in p['shots']:
        lines.extend([f"### Shot {s['number']}: {s['beat']} ({s['start_s']}–{s['end_s']} seconds)",
                      f"Visual objective: {s['visual_intent']}",
                      f"Video prompt: {s['ai_video_prompt']}", ""])
    lines.extend(["## Release gate", "", "- [ ] Story makes sense with audio off",
                  "- [ ] First seconds deliver an authentic reason to watch",
                  "- [ ] Facts, statistics, testimonial claims, and offers are substantiated",
                  "- [ ] Character/product consistency is maintained between shots",
                  "- [ ] Captions are accurate and not obscured by platform controls",
                  "- [ ] Brand/logo usage, music, voice, likeness, and imagery are licensed or authorized",
                  "- [ ] Ad disclosures / AI labels are applied where required",
                  "- [ ] Reviewed on the destination platform's mobile preview",
                  "- [ ] Human reviewed before publication or advertising spend", ""])
    return "\n".join(lines)


def save(project: dict, directory: Path) -> tuple[Path, Path]:
    if directory.exists() and any(directory.iterdir()):
        raise FileExistsError("Output directory must be new or empty (protects prior work)")
    directory.mkdir(parents=True, exist_ok=True)
    draft = directory / "creative.json"
    board = directory / "CREATIVE_BOARD.md"
    draft.write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    board.write_text(render_board(project), encoding="utf-8")
    (directory / "clips").mkdir(exist_ok=True)
    return draft, board


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--platform", choices=sorted(PROFILES), required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--audience", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument("--seconds", type=int)
    parser.add_argument("--offer", default="")
    parser.add_argument("--proof", default="")
    parser.add_argument("--cta", default="Learn more")
    parser.add_argument("--style", default="cinematic-realistic")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    seconds = args.seconds or PROFILES[args.platform]["default_seconds"]
    try:
        result = plan(args.name, args.platform, args.topic, args.audience, args.goal,
                      seconds, args.offer, args.proof, args.cta, args.style)
        dest = args.out or (Path("output") / safe_name(args.name))
        paths = save(result, dest)
    except (ValueError, FileExistsError) as exc:
        parser.error(str(exc))
    print("Creative plan created (not AI-generated footage):", *paths, sep="\n - ")

if __name__ == "__main__":
    main()
