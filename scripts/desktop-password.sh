#!/usr/bin/env bash
set -euo pipefail
password="${HOME}/.config/ai-cloud-lab/vnc-password"
if [[ ! -s "${password}" ]]; then
 echo 'Desktop not started. Run: bash scripts/start-desktop.sh' >&2; exit 1
fi
cat "${password}"
printf '\n'
