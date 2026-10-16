#!/usr/bin/env bash
set -euo pipefail
vncserver -kill :1 || true
pidfile="${HOME}/.config/ai-cloud-lab/websockify.pid"
if [[ -f "${pidfile}" ]]; then
  pid="$(cat "${pidfile}")"
  if [[ "${pid}" =~ ^[0-9]+$ ]]; then kill "${pid}" 2>/dev/null || true; fi
  rm -f "${pidfile}"
fi
printf '%s\n' 'Graphical desktop stopped. To stop Codespaces compute charges, stop the Codespace in GitHub as well.'
