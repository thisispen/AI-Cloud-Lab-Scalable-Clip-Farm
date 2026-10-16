#!/usr/bin/env bash
set -euo pipefail
# Free-to-install npm CLIs. Signing in and any API usage are separate.
BIN_DIR="${HOME}/.local/share/ai-cloud-lab-cli/node_modules/.bin"
NPM_PREFIX="${HOME}/.local/share/ai-cloud-lab-cli"
mkdir -p "${NPM_PREFIX}"
npm install --no-fund --no-audit --prefix "${NPM_PREFIX}" @openai/codex eas-cli
if ! grep -q 'ai-cloud-lab-cli/node_modules/.bin' "${HOME}/.bashrc" 2>/dev/null; then
  printf '\n# AI Cloud Lab command-line tools\n' >> "${HOME}/.bashrc"
  printf 'export PATH="%s:$PATH"\n' "${BIN_DIR}" >> "${HOME}/.bashrc"
fi
export PATH="${BIN_DIR}:${PATH}"
printf 'Codex CLI: '; codex --version
printf 'EAS CLI: '; eas --version
printf 'Log in interactively. Do not paste login codes or API keys into chat.\n'
