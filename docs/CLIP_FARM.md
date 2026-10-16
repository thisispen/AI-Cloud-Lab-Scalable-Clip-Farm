# Clip Farm — rights-aware mass clipping without generated-video API bills

**MVP implemented:** large direct-media HTTP(S) streaming downloads with resume/size caps,
metadata inspection, time/silence cut *suggestions*, editable review manifest, batched FFmpeg
H.264 9:16/16:9/1:1 rendering, optional local captions, and account-specific upload-draft CSV.
No paid APIs, background services or publishing actions. This reuses the Adaptive Creator Studio.

**Not implemented:** Semantic highlight quality ranking/face tracking, real-time bot scheduler,
per-platform OAuth uploads, automatic growth optimisation, copyright detection, and the
production cloud backend. Do not confuse time-based suggestions with viral/high-quality clips.

## Quick start

From the project root:

```bash
# Inspect a local recording that you created or licensed:
python3 -m clipfarm.cli inspect --input /path/to/long-video.mp4

# OR stream an authorized direct public file, including large files (not a YouTube webpage):
python3 -m clipfarm.cli download --url https://my-file-host.example/my-video.mp4 \
  --out data/source.mp4 --max-gb 50 --rights-confirmed

# Suggest 12 candidate segments (these are not AI-ranked best moments):
python3 -m clipfarm.cli suggest --input data/source.mp4 --out data/clip-plan.json \
  --count 12 --min-seconds 15 --max-seconds 45

# Generate smaller previews of all candidates first, no approval flag required:
python3 -m clipfarm.cli render --plan data/clip-plan.json --outdir exports/previews --preview

# Edit the JSON, adjust timestamps, select clips, set approved=true for the final list.
# For now delete unselected candidate entries from the manifest.
python3 -m clipfarm.cli render --plan data/clip-plan.json \
  --outdir exports/shorts --profile shorts --mode crop --threads 2 --workers 1

# Optional offline captions for each finished clip after explicitly installing faster-whisper.
# Model downloads and CPU usage can be substantial; NOT included in default dependencies.
pip install faster-whisper
python3 -m clipfarm.cli captions --input exports/shorts/clip-001.mp4 --model tiny

# Create draft-upload rows for accounts you actually operate; publishing is never automatic.
python3 -m clipfarm.cli accounts --manifest exports/shorts/manifest.json \
  --accounts clipfarm/examples/accounts.json --out exports/account-upload-queue.csv
```

## Costs and scaling

- **CPU first**: FFmpeg segmentation is fast and can use `-c copy` in manual workflows for
  keyframe-aligned cuts. H.264 reframing/caption burn-in entails encoding CPU hours. A GPU
  is optional and only economical when benchmarks justify it.
- **Local scratch storage**: Keep one input file locally while rendering; move outputs to an
  authorized private object bucket. An 80GB VPS disk cannot hold unlimited 50GB inputs.
- **Storage**: Cloudflare R2 Standard $0.015/GB-month beyond free tier (generally 10GB),
  zero egress fees; Backblaze B2 has lower base storage but different egress rules.
- **Cloud worker**: 2–4 vCPU cheap VPS or pay-as-you-go CPU instances; Codespaces is for
  interactive development, not all-night autonomous jobs. Never activate a VM without consent.
- **Bulk accounts**: Keep per-account OAuth credentials separate in a secrets manager;
  respect each platform's post limits and review mechanisms; do not make duplicate-spam
  uploads or evade restrictions. This version stages files for manual or approved uploads.
- **Footage rights**: Only download assets you own or are authorized to download/repurpose.
  The downloader does not ingest YouTube/TikTok watch-page URLs, bypass DRM, use cookies,
  or scrape private accounts.

## Roadmap for truly excellent clips

1. Opt-in whisper CPU/GPU transcription plus sentence-aligned clip candidates.
2. Low-resolution proxies for long videos; shot/face tracking and crop transforms.
3. AI highlight ranker using transcripts + sampled frames; include human rejection rates.
4. Deduplicate videos and detect repeated intros/similar outputs.
5. Retryable SQLite/Redis queue, R2 object lifecycle, spot workers, and measured budgets.
6. Official OAuth upload adapters per platform after review and verified access.
7. Analytics loop to test first-second hook retention and outcomes per account/format.

For an ad or a professional Reel, editor review remains required. Better tools do not
replace story, creative judgment, licensed source material or platform authorization.

### Better highlight suggestions from a real transcript

For transcript-aware ranking, transcribe the **master** recording first (optional local
faster-whisper download may consume memory and CPU):

```bash
python3 -m clipfarm.cli captions --input data/source.mp4 --model small
python3 -m clipfarm.cli rank-srt --input data/source.mp4 --srt data/source.srt \
  --seconds 30 --count 20 --out data/highlight-plan.json
python3 -m clipfarm.cli render --plan data/highlight-plan.json \
  --outdir exports/preview-highlights --preview
```

The score is just keyword/density heuristics. A real high-quality editor or reviewer
must check the clip's context, hook, factual accuracy, and rights before publication.

### Near-zero-CPU cuts when video is already vertical

For a source already in the target resolution/aspect, the fastest route is stream-copy:

```bash
python3 -m clipfarm.cli render --plan data/approved-plan.json \
  --outdir exports/fastcuts --fast-copy
```

This avoids video re-encoding. Frame-accurate boundaries, animated subtitles,
reframing and color grading require the slower encode mode. Fast-copy may include
keyframe rounding, so inspect the export. The user still reviews and approves the cut list.
