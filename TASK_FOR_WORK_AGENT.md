# Task for ChatGPT Work / Codex Agent — COMPLETE CLOUD DEPLOYMENT

I own this AI Cloud Lab repository and want a browser-based Linux desktop + autonomous
AI coding and video project development, at the cheapest possible total cost.

Use the attached ZIP exactly; preserve dotfiles. I authorize free-tier setup and
installation only. **Do not enable any paid service or spend money without asking me**
for explicit approval showing the rate, projected bill, and hard cap. No free-trial
service that automatically transitions into paid hosting. No always-on VMs or GPUs.

1. Create a new PRIVATE GitHub repository `ai-cloud-lab` on my connected account (secure sign-in if needed). Do not alter any existing repositories. If GitHub App permissions cannot create repos, use the cloud browser and ask me to authorize the precise required action.
2. Upload all extracted files (including `.devcontainer`) and create a GitHub Codespace using the 2-core size. Confirm my remaining free personal Codespaces quota and set/verify a $0 overage budget in GitHub Billing if supported. Set default idle shutdown to ~10 minutes.
3. Wait for the dev container to finish. It installs Node.js, Python, Firefox, XFCE desktop, VNC/noVNC, Codex CLI and Expo EAS CLI. Verify `python3 -m unittest discover -s tests -v`, run `bash scripts/demo-video.sh`, and test the desktop private port 6080 `/vnc.html` with the password displayed locally via `bash scripts/desktop-password.sh`.
4. Confirm the port's visibility remains PRIVATE. Do not show passwords or session secrets in task output. Log in to Codex only through its supported interactive flow; the existing ChatGPT plan may have Codex usage subject to limits. Never assume separate API credit is included.
5. Create `apps/mobile` via `bash scripts/new_mobile.sh`. Validate Expo sources. Do not submit any build or create any Apple developer account without the user's go-ahead.
6. Batch queue sample video jobs `python3 video/batch.py --prompts video/sample-prompts.txt`; demonstrate listing and exporting. Do not call any metered generation API unless the user approves the provider and spend cap.
7. Do NOT provision Railway, RunPod, SaladCloud, Cloudflare R2 paid capacity, or extra disk. Only connect an R2 bucket if the user approves any required billing activation; use scoped R2 secrets and private buckets.
8. Return the private repository link, Codespace URL, browser desktop URL, exact tests run, live billing usage/limits, and honest list of what is not yet activated. Explicitly STOP the Codespace once verification finishes; tell me how to resume it.

If an action requires secure sign-in / 2FA / new permissions, request that specific step via the browser. Continue free preparation on other steps where possible.

## Creator Studio deployment additions

After cloud desktop provisioning, validate the creative studio with `python3 -m unittest discover -s tests -v`, `python3 -m studio.creative --help`, and `python3 -m studio.costs --model veo31_lite_720 --videos 1 --seconds 5 --attempts 1`. If `ffmpeg` is installed, render one authorized/synthetic MP4 from the included demo tool and validate using `studio.review`. Store renders outside git (the `output/` folder is ignored).

Do not advertise the creative-planning and FFmpeg scaffolding as an integrated paid video service. Ask before connecting any metered Veo, Runway, voice, video or GPU service. Require explicit approval for spend ceiling and exact provider before using any paid call. Present planned budgets in generated seconds and estimated retakes. Follow `docs/CREATIVE_STUDIO.md` and `docs/EVALUATOR.md`.

## Adaptive Studio installation (new requirement)

After the private Codespace is deployed and validated, perform a read-only demonstration of the updated tool catalog:

```bash
python3 -m studio.router --platform reels --ai-seconds 5 --attempts 2
python3 -m studio.production_budget --videos 1000 --final-seconds 30 --generated-seconds 5
python3 -m unittest discover -s tests -v
```

Show the user which editors can run directly in the small Codespace (FFmpeg and optional coding tools) versus those requiring a larger GPU desktop, external web subscription or ChatGPT app (DaVinci, Premiere, CapCut, Descript, Runway). Offer to connect Runway and Descript with explicit user sign-in. If the user enables the GitHub Actions workflow, the weekly read-only release check may be used but never auto-install software. Never turn on paid APIs or initiate charges or social ad spends before user approval. Read `docs/ADAPTIVE_STUDIO.md` and the policy file. Do not reverse engineer paid APIs or remove usage limits.

## Cheap clipping farm deployment, pending approval
Use `docs/CLIP_FARM.md` to validate the local MVP with owned sample footage. Do not activate
paid instances. For scale, propose a cheap CPU worker with temporary disk and a private R2
bucket, plus human-review upload drafts. Implement resumable jobs and actual account
OAuth integration only after the user explicitly approves the provider and uploads.
