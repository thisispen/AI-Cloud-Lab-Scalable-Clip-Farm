# AI Cloud Lab Creative Studio — TikTok, Reels, Ads, YouTube

**Purpose**: Draft, direct, review and assemble polished platform-native videos without buying a GPU or committing to a metered video-generation API. The included creative planner, MP4 assembler, technical reviewer and rate estimator work offline. They **do not** call any AI video model; generated footage/voices still require the user's approved AI service or licensed assets.

## Production method (quality-first)

1. **Creative intake**: Who is watching? Desired action? Claim substantiation? Real product photos? Brand kit? Audience language? Spend cap?
2. **Create 3 hooks** with genuinely different emotional mechanisms, not three synonymous lines. For ads specify the offer, target audience, objections and proof. Never invent reviews, statistics or demonstrations.
3. **Write narrative beats** (promise → conflict → evidence → payoff → next action). Distinct assets for each beat.
4. **Create a visual continuity kit**: reference image per character/product, approved color palette, lens/camera vocabulary, lighting, wardrobe, logos, voice and music. Supply image reference to video generator when available. Test a few seconds before scaling.
5. **Generate draft footage cheaply**: output individual shots. Use a faster/cheaper model for explorations and premium cinematic model only where its extra quality matters. Different scenes may use different models; track provenance and rights. Never call an API before the user sets and approves a project cap.
6. **Editorial assembly**: the supplied `studio.edit` concatenates clips into a 9:16, 16:9 or 1:1 H.264 MP4 at 30fps; optional external voice, music, SRT captions. It crops to fill, so check framing and text manually. Add audio/visual effects in a full editor when needed. Upload MP4 to platform's draft/preview only after review.
7. **Quality evaluator**: objective technical checks + human approval (see `EVALUATOR.md`). No generic AI-generated hook or arbitrary score is evidence of a viral video.
8. **Human release gate**: approve visual realism/brand accuracy, caption timing, audio mix, safe zones, disclaimers, ad policy and rights. No auto-publishing or ad spend in the starter.
9. **Learn from real results**: watch time, 3-second retention, average percentage viewed, saves/shares, clickthrough, conversion and cost per acquisition when legitimately available. Optimize by platform; do not treat views alone as commercial success.

## Platform deliverables

| Platform | Starting master | Story / editing focus |
| --- | --- | --- |
| TikTok | 1080×1920 vertical | fast hook, native storytelling, precise captions, optional platform-native edit |
| Instagram Reels | 1080×1920 vertical | visual polish, clarity without sound, avoid obscured overlays |
| Facebook Reels Ads | 1080×1920 vertical | product/proof/action, audio, safe-zone-aware text, verified claims and Meta ad policy |
| YouTube Shorts | 1080×1920 vertical | immediate payoff, concise structure, clear titles |
| YouTube long | 1920×1080 horizontal | chapters, research, story development, rhythm, chapters and thumbnails |

Safe zones vary with device, ad placement and platform UI. **Do not rely on static margins alone**: always review the export in the destination app before publishing.

## Use it

All commands run from the repository root.

```bash
python3 -m studio.creative \
  --name "Prototype Ad A" --platform facebook_ad --topic "our product" \
  --audience "busy small-business owners" --goal "qualified demo requests" \
  --seconds 30 --offer "Free demo" --cta "Book a demo" \
  --out output/prototype-ad-a
# Edit output/prototype-ad-a/creative.json and CREATIVE_BOARD.md.
# Generate the individual scenes separately in your chosen approved provider;
# drop MP4s into output/prototype-ad-a/clips.

python3 -m studio.costs --model veo31_lite_720 --videos 1000 --seconds 15 --attempts 2
python3 -m studio.costs --model runway_gen4_turbo --videos 1000 --seconds 15 --attempts 2

# For real clips that you already own, use:
python3 -m studio.edit --clips shot1.mp4 shot2.mp4 shot3.mp4 \
  --voice optional-voice.wav --music optional-licensed-track.mp3 \
  --subtitles optional-reviewed-timing.srt --layout vertical --out output/final.mp4

python3 -m studio.review output/final.mp4 --layout vertical --min-seconds 5 \
  --out output/final.qc.json
```

Optional `--width 360 --height 640` on `studio.edit` runs a fast low-resolution test before the high-res render. Input videos are resized and center-cropped; if subjects move off center or the source text must not be cropped, fix shot composition upstream or use your full video editor. Embedded source audio is discarded by this assembler; pass a separate audio track explicitly. Captions require a **real, correctly timed** subtitle file and human alignment check. AI speech recognition/alignment, transitions, avatars and thumbnails are future connectors, not included.

## Choose providers by artistic needs, not marketing

- Veo 3.1: high-quality video with audio through Google's paid Gemini API; Lite and Fast can reduce unit cost, with limitations that must be tested.
- Runway: generative cinematics; Gen-4 Turbo is a lower-cost option, with more capable models for key shots. Its API pricing and web subscription credits differ.
- Your own open weights (LTX, Wan): when high production volume justifies an on-demand GPU, compute/engineering setup is separate; measure GPU time and usable output rate first.
- Voice and music: record your own, use original/licensed tracks, or enable voice/sound APIs only after reviewing voice-identity consent, commercial terms and costs.

Pricing as of October 2026 (subject to change): Google https://ai.google.dev/gemini-api/docs/pricing ; Runway https://docs.dev.runwayml.com/guides/pricing/ . Estimated charges scale with **generated seconds**, not just finished seconds. Retakes are expensive. `studio.costs` is a scenario calculator, not a live quote. API credentials must be entered only into your own provider's secret manager or Codespaces secrets; do not put them in prompts, source control or this ZIP.

## No unattended spending

- No configured video provider, no automatic payments, no GPU rental, no API background calls, no paid export/publishing.
- Review a low-cost **single-shot test** and approve a maximum dollar limit before connecting a metered API.
- Store generated media in a private approved cloud bucket when ready, not the Git repo. Project planning JSON and Markdown can remain in the repository if not private/sensitive.
- Publishing tools and social-account login should be connected via OAuth with minimal scopes, separately and only with user approval.

## Disclosure and compliance

TikTok ads require disclosure of significantly AI-generated advertising media, and YouTube requires disclosure for realistic meaningful AI-altered/generated media. Commercial partnerships and advertising claims require separate disclosures and substantiation as applicable. Review current platform requirements for the actual campaign (they change). Links:
- https://ads.tiktok.com/resources/help/article/tiktok-ads-policy-misleading-and-false-content
- https://support.google.com/youtube/answer/14328491
- https://www.facebook.com/business/ads/facebook-instagram-reels-ads
