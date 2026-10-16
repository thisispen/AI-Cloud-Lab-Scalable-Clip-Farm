# Prompt to give Codex in your cloud workspace

Build and run a high-quality video creative workflow for my brand, using this repository as the production environment. Read `AGENTS.md`, `docs/CREATIVE_STUDIO.md` and `docs/EVALUATOR.md` first. Act like a critical producer and editor, not a generic prompt generator.

Objectives: make compelling TikTok, Instagram Reels, Facebook ads, YouTube Shorts and long-form YouTube videos; be able to adapt one concept into platform-specific variants. Prefer authenticity, consistency, useful content and real proof over flashy AI visuals. Never invent performance claims, reviews or scientific facts.

1. Start with the brand's verified offer, audience, goals, assets, available proof, tone and approved visual references. Mark unknown facts as unknown and request evidence when essential.
2. Produce 3 deliberately distinct creative concepts, each with an opening hook, full short script, 5–8 visual beats, on-screen captions, shot list, audio plan and CTA. Critique them under the project's evaluator and recommend one to test.
3. Use the included `python3 -m studio.creative` command to save the chosen storyboard. Maintain assets per shot and a small brand/character continuity bible.
4. Estimate **total generated seconds including retakes** for each possible provider using `python3 -m studio.costs`. No API integration, video generation, credit purchase, GPU rental, social login, autoposting or ad spend without my authorization of vendor, scope, ceiling and unit prices. For a cost-sensitive pilot, render at most a handful of short shots and compare several quality tiers first.
5. Once I provide or authorize footage, perform editing with FFmpeg and appropriate caption/audio timing, then run `python3 -m studio.review`. Use human/actual-media critique to list concrete flaws and fix highest-impact problems within the approved budget.
6. Export 1080×1920 H.264 for TikTok, Reels and Shorts, plus 1920×1080 for YouTube long-form where appropriate. Check every destination's UI safe areas in its current native preview before final delivery. Human approval is required before publishing and ad spend.
7. For finished ads, propose a small controlled experiment: distinct hooks or offers, one variable at a time, metrics aligned to the actual conversion goal, and truthful post-launch analysis rather than claiming a video will 'go viral'.

First deliverable: three annotated concepts and a budget forecast **without spending money**.
