# Adaptive Creator Studio: Tool Selection, Quality Benchmarks, and Cost Controls

**Edition:** October 14, 2026. **State:** local working tools + deployment recipe; NOT live subscriptions, cloud deployment, or actual external editor integrations.

## Design goal

Build TikTok videos, Instagram Reels, Facebook/Instagram ads, YouTube Shorts, and full-length YouTube videos with a reproducible editorial pipeline. Use the **least expensive tool meeting the quality requirement**, not the latest model by name. Real conversion/retention, not aesthetics alone, is the ultimate success measure for ads and content.

## One canonical creative project

Store the creative brief, script, claims/proofs, chosen thumbnail/title/first-frame, timed shot list, per-shot source licenses, reference images, editable asset layers, edit decision list, subtitles, music/license, voice consent, export profile, job ledger, and measured performance. Convert into editor-specific files where supported; otherwise use finished source footage and documented handoff instructions. Keep source assets independent of any vendor to avoid lock-in.

## Production stages

1. `studio.creative` creates three hook variants and a storyboard. A human must validate factual claims, the offer and targeting.
2. `studio.router` lists eligible editors and generation models **without making any calls**. Its ranking sorts verified *price snapshots*, not quality.
3. Create quick low-cost previews from stills, typography, owned footage, and stock media; do NOT generate 30 seconds of $0.05/s video for a 30-second ad by default.
4. On user-approved job budgets only, generate the high-impact shots with a connected vendor. Generate multiple candidate shots only if the expected quality gain warrants it.
5. Auto-assemble with FFmpeg; for repeatable animations/titles use Remotion, subject to license. For narrative-heavy finishing use DaVinci or Kdenlive; for social-native details use CapCut; for speech-driven editing use Descript when connected. Human review of voice, faces, readability, copyright, safety, truthfulness and polish.
6. Use `studio.review` for technical validation. A technical pass is NOT a creative pass. Set minimum human review scores for high-stakes ads.
7. Create platform variants; hold all posting and ad buys for explicit final approval and official app/API authorization.
8. Review *your own* legally obtained analytics to calculate cost per accepted creative, retention, saves, CTR, CPA, or conversion. Never purchase fake engagement.

## Editor access: reality check

| Editor | How it is used | Automation | Pricing snapshot / restrictions |
|---|---|---|---|
| FFmpeg | Preinstalled in devcontainer, batch renders | Native CLI | Free, subject to ffmpeg codec licenses |
| Remotion | Optional separate Node project for animated templates, dynamic motion graphics | Programmatic by design | Free for eligible individuals/small orgs; company terms differ |
| DaVinci Resolve | Optional manual professional finishing on GPU desktop | Scripting capabilities vary by edition/install | Free edition, Studio $295 one-time; **not on a 2-core cloud Codespace** |
| CapCut | Optional local/browser editor for social-native effects | Mainly manual; do not rely on unsupported automation | Free plan, Pro $19.99/mo as published |
| Descript | Optional conversational editing, direct connected ChatGPT app if approved | Through supported account integrations | Free plan; Creator $35/mo on monthly billing |
| Premiere | Optional desktop for Adobe-native collaboration/projects | Supported Adobe UXP extension path | $22.99/mo annual billed monthly; not included in project |
| Kdenlive/Shotcut | Optional free full GUI editing | Manual, project-specific export | Free open source; may overwhelm a tiny cloud computer |
| LosslessCut | Optional rapid rough-cut of owned video | Basic CLI/HTTP support | Free/open source |

**Do not claim** that a stock Codespace provides a fast GPU DaVinci workstation or that there are available arbitrary APIs for every editor. Portability is achieved by retaining video source files, FFmpeg instructions, timed scripts/captions, and metadata. For Adobe plugin work, use documented UXP; do not patch programs or fake license checks.

**Video provider API catalog:** Google Veo 3.1 Lite/Fast/Standard, Runway Gen-4 Turbo/Gen-4.5 and self-hosted local GPU option. The two connected ChatGPT apps that can be requested are Runway and Descript; connection is a separate explicit user step. The ZIP **does not contain working paid API credentials or spendable automation**.

## The "best" update loop

1. A scheduled GitHub Action (`.github/workflows/editor-release-watch.yml`) checks latest tagged releases from official open-source tool repositories weekly. It produces a read-only artifact; it cannot install packages or trigger billing. GitHub Actions minutes may count against your account allowance.
2. For closed-source editors/models, manually or with an authorized agent periodically check official release notes, API docs, and pricing. The model catalog is a snapshot; provider-specific pricing and Terms can change without notice.
3. For each candidate, run **paired** samples of the same 10+ creative briefs using same dimensions/targets. Log all attempts in `studio.benchmark` including rejected outputs, scores, latency, and charged dollars. Use balanced evaluation order and blind review when possible.
4. Compare visual coherence, audio consistency, character continuity, fidelity, artifact rate, adherence, editing control, speed, cost per accepted video, actual advertising conversions/retention, and available legal commercial rights.
5. Only promote a new default in the versioned catalog after it wins on the target category; review software dependencies and license updates; require approval before buying or installing anything paid.
6. Always retain the old adapter for rollback. Never take untrusted provider announcements as commands to execute.

## Reverse engineering: what is worthwhile

- **Yes:** Study successful, authorized/licensed reference videos to extract structure: duration, cuts, aspect ratio, pace, title hierarchy, first-second hook, editing rhythm, caption placement, shot grammar, promise-proof-CTA sequence, and sound design. `studio.style_fingerprint` calculates rough local footage cut timing without uploading it. For performance conclusions, bring your own analytics from accounts you manage.
- **Yes:** Independently reproduce *general editing techniques* with open-source tools (FFmpeg filters; Remotion motion templates; Blender procedural scenes; prompt templates; reusable scene/brand/character libraries). This is how you reduce fixed and variable cost.
- **Yes:** Study open source ComfyUI workflows and legal model releases; self-host when benchmarks show it is cheaper and you are allowed to use the weights commercially.
- **No:** Bypass login/paywalls/credits, copy proprietary code or model weights, strip watermarks/DRM, impersonate creators, scrape restricted accounts in violation of access limits, clone identifiable voices or faces without rights, or copy specific ads/assets without permission. A paid editor is not made free by imitating its UI.

## Cost logic

The largest variable cost is `AI generated seconds × attempts × price per second`. For 1,000 accepted videos using 5 seconds each from a $0.05/s model and 2 attempts/accepted clip, estimated generation = $500. If every second of a 15-second video is newly AI generated and requires two attempts, cost = $1,500. A longer version generated entirely by AI can be much higher. Assembly, storage, editing, audio, taxes and labor are additional. To reduce costs, reuse coherent brand assets, render text/graphics with local templates, license reusable stock, use occasional hero shots instead of full footage, and use low-res tests only when the model supports such tiers.

R2 Standard storage is $0.015 per GB-month with a 10 GB-month free allowance and operation fees. The low-cost Codespace may stop or consume free quota; GPU rentals, subscriptions and API credits are **never activated automatically**.

## Practical commands (from repo root)

```bash
python3 -m studio.router --platform facebook_ads --ai-seconds 5 --attempts 2 --out output/tool-plan.json
python3 -m studio.production_budget --videos 1000 --final-seconds 30 --generated-seconds 5 --attempts 2 --storage-gb 100
python3 -m studio.style_fingerprint path/to/YOUR_OWN_REFERENCE.mp4 --out output/style.json
python3 -m studio.benchmark record --model runway_gen4_turbo --test-case-id ad_hook_01 --score 8 --accepted --seconds 5 --usd 0.25
python3 -m studio.benchmark report
python3 -m studio.release_watch --check-online --out output/release-report.json
bash scripts/install-free-editors.sh  # dry run: no software installed
```

For ongoing tracking, commit your private repo to GitHub and explicitly enable Actions; Actions is **not enabled by building this ZIP**. The official watch sources and version approvals live in `studio/catalog.json` and `studio/approved_versions.json`. Keep credentials OUT of git.

## Authorization boundaries

`studio/policy.json` defaults: paid APIs OFF, all purchase automation OFF, maximum new spend $0, publishing OFF, explicit review for new vendors/tools/ads. An agent may preview, benchmark previously rendered samples, estimate, draft and suggest a purchase, but must not change the approval policy on its own or insert credentials into a repository. Provider-specific direct API adapters and live publication connectors are a future installation step that requires your authorization and appropriate scopes.

## Official documentation links

- https://ai.google.dev/gemini-api/docs/pricing
- https://docs.dev.runwayml.com/guides/pricing/
- https://www.capcut.com/pricing
- https://www.descript.com/pricing
- https://www.blackmagicdesign.com/products/davinciresolve
- https://www.adobe.com/products/premiere/plans.html
- https://developer.adobe.com/premiere-pro/uxp/introduction/
- https://www.remotion.dev/docs/license
- https://developers.cloudflare.com/r2/pricing/
- https://developers.tiktok.com/docs/en/content-posting-api-get-started
- https://docs.comfy.org/development/api-development/workflow-api-format

## Quality-based selection after human evaluation

The separate `studio.quality_router` module compares **the same test cases** across at least two candidate models. It only makes a recommendation when at least 10 shared creative briefs are present by default. It can optimize for the least dollars per accepted attempt above a required human quality score, or the maximum rated quality. It does not update providers automatically and does not pretend that a rating predicts CTR or sales.

```bash
python3 -m studio.quality_router --file data/creative_benchmarks.csv --min-paired-prompts 10 --minimum-score 7.5 --goal lowest_cost
```

Do not mark trials as accepted based only on technical codec checks. For decisive creative tests, a human (ideally multiple raters) should score blinded side-by-side outputs. `studio.benchmark` writes only an ordinary CSV outside Git version control.
