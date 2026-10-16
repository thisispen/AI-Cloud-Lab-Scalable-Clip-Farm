#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -f apps/mobile/package.json ]]; then
  echo "apps/mobile exists. Not overwriting."
  exit 0
fi
mkdir -p apps
npx --yes create-expo-app@latest apps/mobile --template blank-typescript --yes
printf '\nNow: cd apps/mobile && npx expo start --tunnel\n'
printf 'For cloud builds: npx eas-cli@latest login && npx eas-cli@latest build:configure\n'
