#!/usr/bin/env python3
"""Offline AI-video job tracker; deliberately does not invoke paid video APIs."""
import argparse, json, sqlite3
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB=Path(__file__).resolve().parents[1]/'data'/'jobs.sqlite3'
def db_connect(p:Path):
    p.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(str(p))
    db.row_factory=sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS jobs (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       created_at TEXT NOT NULL,
       prompt TEXT NOT NULL,
       seconds INTEGER NOT NULL,
       provider TEXT NOT NULL,
       model TEXT,
       status TEXT NOT NULL DEFAULT 'pending',
       output_path TEXT,
       notes TEXT
    )""")
    db.commit()
    return db

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',default=str(DEFAULT_DB))
    sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('add'); a.add_argument('--prompt',required=True);a.add_argument('--seconds',type=int,default=5);a.add_argument('--provider',default='manual');a.add_argument('--model',default='')
    a=sub.add_parser('list');a.add_argument('--limit',type=int,default=30)
    a=sub.add_parser('mark');a.add_argument('--id',type=int,required=True);a.add_argument('--status',choices=('pending','processing','completed','failed'),required=True);a.add_argument('--output',default=None);a.add_argument('--notes',default=None)
    sub.add_parser('stats')
    a=sub.add_parser('export');a.add_argument('--out',required=True)
    args=p.parse_args(argv)
    with db_connect(Path(args.db)) as db:
        if args.cmd=='add':
            if not 1<=args.seconds<=600: p.error('--seconds must be in [1,600]')
            cur=db.execute('INSERT INTO jobs(created_at,prompt,seconds,provider,model) VALUES(?,?,?,?,?)', (datetime.now(timezone.utc).isoformat(),args.prompt,args.seconds,args.provider,args.model))
            db.commit(); print(json.dumps({'id':cur.lastrowid,'status':'pending'}))
        elif args.cmd=='list':
            print(json.dumps([dict(x) for x in db.execute('SELECT * FROM jobs ORDER BY id DESC LIMIT ?', (args.limit,))],indent=2))
        elif args.cmd=='mark':
            cur=db.execute('UPDATE jobs SET status=?,output_path=COALESCE(?,output_path),notes=COALESCE(?,notes) WHERE id=?',(args.status,args.output,args.notes,args.id))
            db.commit()
            if cur.rowcount==0: p.error(f'No such job: {args.id}')
            print(json.dumps({'id':args.id,'status':args.status}))
        elif args.cmd=='stats':
            print(json.dumps({row['status']:row['n'] for row in db.execute('SELECT status,COUNT(*) AS n FROM jobs GROUP BY status')},indent=2))
        elif args.cmd=='export':
            rows=[dict(x) for x in db.execute('SELECT * FROM jobs ORDER BY id')]
            out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
            out.write_text(json.dumps(rows,indent=2),encoding='utf-8')
            print(f'Exported {len(rows)} jobs to {out}')
if __name__=='__main__':main()
