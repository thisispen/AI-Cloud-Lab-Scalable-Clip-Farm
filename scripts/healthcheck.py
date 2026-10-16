#!/usr/bin/env python3
import json, os, shutil, subprocess, sys
from pathlib import Path

def version(command):
    p=shutil.which(command)
    if not p: return 'not installed'
    try:
        r=subprocess.run([p,'--version'],capture_output=True,text=True,timeout=12)
        return (r.stdout or r.stderr).strip().splitlines()[0]
    except Exception as e: return f'error: {e}'

report={
    'python':sys.version.split()[0],
    'node':version('node'),
    'npm':version('npm'),
    'git':version('git'),
    'gh':version('gh'),
    'env_file_exists':Path('.env').exists(),
    'r2_configured':all(os.environ.get(x) for x in ('R2_ACCOUNT_ID','R2_ACCESS_KEY_ID','R2_SECRET_ACCESS_KEY','R2_BUCKET')),
    'video_provider_mode':'manual (no metered API calls)',
    'codespace_detected':bool(os.environ.get('CODESPACES')),
}
print(json.dumps(report,indent=2))
