#!/usr/bin/env python3
"""Queue lines of prompts locally. Explicitly never calls a video-generation API."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from video.queue import db_connect, DEFAULT_DB


def add_prompts(database: Path, prompts: list[str], seconds: int = 5, provider: str = 'manual') -> int:
    if not 1 <= seconds <= 600:
        raise ValueError('seconds must be between 1 and 600')
    now = datetime.now(timezone.utc).isoformat()
    with db_connect(database) as db:
        db.executemany(
            'INSERT INTO jobs(created_at,prompt,seconds,provider,model) VALUES(?,?,?,?,?)',
            ((now, prompt, seconds, provider, '') for prompt in prompts if prompt.strip()))
        db.commit()
    return sum(bool(x.strip()) for x in prompts)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prompts', required=True, type=Path, help='One prompt per line')
    p.add_argument('--seconds', type=int, default=5)
    p.add_argument('--provider', default='manual')
    p.add_argument('--db', type=Path, default=DEFAULT_DB)
    args = p.parse_args()
    if not args.prompts.is_file():
        p.error('Prompts file does not exist')
    prompts = [s.strip() for s in args.prompts.read_text(encoding='utf-8').splitlines() if s.strip()]
    count = add_prompts(args.db, prompts, args.seconds, args.provider)
    print(f'Added {count} offline jobs. $0 spent on video generation.')

if __name__ == '__main__':
    main()
