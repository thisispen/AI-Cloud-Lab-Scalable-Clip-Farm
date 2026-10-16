#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p output
# A synthetic 2-second MP4 verifies FFmpeg without using paid GPU/API services.
ffmpeg -hide_banner -loglevel error -y -f lavfi -i "testsrc2=size=640x360:rate=24" \
  -t 2 -c:v libx264 -preset ultrafast -pix_fmt yuv420p output/cloud-lab-demo.mp4
file output/cloud-lab-demo.mp4
printf 'Demo video created without any paid AI-generation request.\n'
