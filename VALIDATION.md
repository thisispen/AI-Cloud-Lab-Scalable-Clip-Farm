# Validation and live deployment status — October 14, 2026

## Verified inside the ChatGPT preparation runtime
- Original `ai-cloud-lab-starter.zip` was extracted and reused as the base.
- 3 Python unittest cases passed (original offline queue + new batch queue checks).
- `bash -n scripts/*.sh` passed.
- The devcontainer JSON parsed successfully; port 6080 configured as private.
- FFmpeg generated a valid local synthetic 2-second MP4 without GPU or video API costs.
- The sample batch enqueued 3 jobs, all initially pending, without video generation.
- ZIP archive generated and contents verified.

## Not yet verified or provisioned
- Docker image build, XFCE/TigerVNC/noVNC graphical session and browser access (no Docker daemon in preparation environment).
- GitHub private repository creation, Codespaces environment or account-specific Codespaces billing caps (connected GitHub tools expose no create-repository/create-Codespace action; no visible accessible repositories).
- Codex and EAS npm installers inside Codespaces (requires provisioned cloud environment).
- Expo authentication and iOS/Android cloud build (separate account and potentially paid signing/build requirements).
- Cloudflare R2 account or bucket (not connected; possible billing activation).
- Official video provider integration and generated AI videos (provider, metered spending and credential approval needed).
- Dedicated GPU/cloud worker or always-on server (not started or charged).

## Hard cost and privacy boundary
No paid service, GPU workload, server, metered video API, storage bucket or subscription was activated. The starter contains no passwords, API keys or account data.

## Deployment instructions
Read `TASK_FOR_WORK_AGENT.md` and `README.md`. GitHub Codespaces is a lightweight browser-based **Linux** desktop, not a Windows desktop or a GPU workstation. The default Codespaces inactivity policy shuts the computer down; Codex cloud tasks can be used separately where available.

## Creator Studio extension checks (October 14, 2026)

- Added offline creative brief/storyboard generator for TikTok, Instagram Reels, Facebook Reels/ads, YouTube Shorts and long-form YouTube.
- Added price scenario calculator for Google Gemini Veo 3.1 and Runway models based on published API rates; **not a live pricing quote or a billing connection**.
- Added offline FFmpeg clip assembler with optional external audio / reviewed SRT subtitles and an MP4 technical preflight.
- Added rubric instructing humans / multimodal agents to inspect actual output; no automated visual aesthetics or hook-performance accuracy claimed.
- **7 Python tests passed**, including two real, synthetic FFmpeg clips combined into a 5.5-second vertical H.264 MP4 with an audio stream.
- `bash -n scripts/*.sh` passed; sample Instagram Reels plan generated; $1,500 estimate for 1,000×15-second Veo 3.1 Lite outputs with 2× attempts (AI footage alone).
- No connected provider credential, paid GPU, actual AI video generation or live deployment was activated.

## Clip Farm extension, October 14, 2026

- New commands: `python3 -m clipfarm.cli` download/inspect/suggest/rank-srt/render/captions/accounts.
- Confirmed: `python3 -m unittest discover -s tests -v` **21 tests passed**, including
  synthetic video inspection, preview H.264 FFmpeg encodes (360x640), fast-copy remux,
  manifest approval requirement, upload-draft CSV, rights confirmation check,
  and SRT subtitle parsing + heuristic clip candidate selection.
- Confirmed: `bash -n scripts/*.sh` passed.
- Cloud integrations were NOT deployed, tested or charged.
- Downloader was not tested against a real hosted large video or authenticated video platform.
- Transcript scoring is a rule-based heuristic; not actual semantic quality assessment.
- Optional faster-whisper model and real platform upload integrations are NOT installed/tested.
- A separate user's clipping bot farm project was not present; new functionality was
  added to the provided Cloud Lab/Adaptive Studio scaffold.
