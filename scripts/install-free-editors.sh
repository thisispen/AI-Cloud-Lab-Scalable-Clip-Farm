#!/usr/bin/env bash
set -euo pipefail
# Free editors are OPTIONAL. Never automatically install large GUIs on a 2-core Codespace.
if [[ "${1:-}" != "--approve" ]]; then
  echo 'DRY RUN: Optional desktop editors: Kdenlive, Shotcut, Blender (large install; requires suitable VM).'
  echo 'FFmpeg is already installed by the devcontainer. Remotion may be installed on demand per project.'
  echo 'Review RAM, disk, GPU, license and Codespaces quotas first. Then run with --approve if desired.'
  exit 0
fi
if [[ "${ALLOW_FREE_EDITOR_INSTALL:-}" != "yes" ]]; then
  echo 'Set ALLOW_FREE_EDITOR_INSTALL=yes to confirm resource usage and rerun.' >&2
  exit 2
fi
sudo apt-get update
sudo apt-get install -y --no-install-recommends kdenlive shotcut
printf 'Installed free editors. This operation consumed storage/compute quotas; no paid video API called.\n'
