#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -f apps/web/package.json ]]; then
  echo "apps/web exists. Not overwriting."
  exit 0
fi
mkdir -p apps
npx --yes create-next-app@latest apps/web --typescript --eslint --tailwind --app --use-npm --yes
