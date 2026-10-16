"""Small durable single-host SQLite job queue: prepare previews, never auto-post."""
import argparse, json, os, re, sqlite3, sys, time, uuid, threading, traceback
from pathlib import Path
from contextlib import closing
from clipfarm.core import suggest
from clipfarm.render import render_manifest

LEASE_SECONDS=600
RETRIES=3
def root_path(p):
    root=Path(p).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    for dirname in ('inputs','outputs','state'): (root/dirname).mkdir(exist_ok=True)
    return root
def dbconn(root):
    c=sqlite3.connect(root/'state'/'jobs.sqlite',timeout=30,isolation_level=None)
    c.row_factory=sqlite3.Row
    c.execute('PRAGMA journal_mode=WAL')
    c.execute('PRAGMA busy_timeout=30000')
    c.execute("""CREATE TABLE IF NOT EXISTS jobs (
      id TEXT PRIMARY KEY, brand TEXT NOT NULL, source TEXT NOT NULL,
      profile TEXT NOT NULL, clip_count INTEGER NOT NULL,
      min_seconds INTEGER NOT NULL, max_seconds INTEGER NOT NULL,
      status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
      worker TEXT, lease_until REAL, created REAL NOT NULL, updated REAL NOT NULL,
      output_dir TEXT, error TEXT)""")
    return c
def safe_brand(s):
    if not re.fullmatch('[a-zA-Z0-9_-]{1,40}',s): raise ValueError('Brand must be 1-40 letters/numbers/_/-')
    return s
def safe_source(root,filepath):
    inp=(root/'inputs').resolve()
    p=Path(filepath)
    p=(p if p.is_absolute() else inp/p).resolve()
    if not p.is_relative_to(inp):raise ValueError('Put authorized source files inside farm-data/inputs')
    if not p.is_file(): raise FileNotFoundError(str(p))
    return p
def enqueue(root,args):
    if not args.rights_confirmed: raise PermissionError('Must confirm the legal right to download and repurpose source media')
    src=safe_source(root,args.source)
    if not (1<=args.clips<=100): raise ValueError('Clips must be between 1 and 100')
    if not (3<=args.min_seconds<=args.max_seconds<=180): raise ValueError('Clip lengths must fit 3..180s')
    jobid=str(uuid.uuid4())[:12]
    stamp=time.time()
    with closing(dbconn(root)) as c:
        c.execute("""INSERT INTO jobs(id,brand,source,profile,clip_count,min_seconds,max_seconds,status,created,updated)
              VALUES(?,?,?,?,?,?,?,?,?,?)""",
          (jobid,safe_brand(args.brand),str(src),args.profile,args.clips,args.min_seconds,args.max_seconds,'queued',stamp,stamp))
    return {'job_id':jobid,'status':'queued','brand':args.brand,'source':str(src)}
def claim(c,worker):
    now=time.time()
    c.execute('BEGIN IMMEDIATE')
    try:
        c.execute('UPDATE jobs SET status="failed",error="Job lease expired repeatedly",updated=? WHERE status="running" AND lease_until<? AND attempts>=?',(now,now,RETRIES))
        row=c.execute("""SELECT * FROM jobs WHERE (status='queued' OR (status='running' AND lease_until<?))
                          AND attempts<? ORDER BY created LIMIT 1""",(now,RETRIES)).fetchone()
        if row:
            c.execute('UPDATE jobs SET status="running",worker=?,attempts=attempts+1,lease_until=?,updated=? WHERE id=?',(worker,now+LEASE_SECONDS,now,row['id']))
        c.execute('COMMIT')
        return dict(row) if row else None
    except BaseException:
        c.execute('ROLLBACK');raise
def heartbeat(root,jobid,worker,stop):
    while not stop.wait(60):
        try:
            with closing(dbconn(root)) as c:
                c.execute('UPDATE jobs SET lease_until=?,updated=? WHERE id=? AND worker=? AND status="running"',
                          (time.time()+LEASE_SECONDS,time.time(),jobid,worker))
        except Exception as e:
            print('Heartbeat warning',repr(e),file=sys.stderr,flush=True)
def complete(c,j,status,out=None,error=None):
    c.execute('UPDATE jobs SET status=?, output_dir=?, error=?,lease_until=NULL,updated=? WHERE id=?',(status,out,error,time.time(),j['id']))
def process_job(root,j):
    out=root/'outputs'/j['brand']/j['id']
    out.mkdir(parents=True,exist_ok=True)
    manifest=out/'clip-plan.json'
    plan=suggest(j['source'],minimum=j['min_seconds'],maximum=j['max_seconds'],count=j['clip_count'])
    manifest.write_text(json.dumps(plan,indent=2),encoding='utf8')
    if not plan['clips']: raise ValueError('No preview candidates; check input length')
    render_manifest(manifest,out/'previews',profile=j['profile'],preview=True,workers=1,threads=1)
    (out/'REVIEW.txt').write_text('Preview clips are NOT final videos. Review clip-plan.json, remove unwanted clips, and set approved=true before final render. Do not post without rights/editorial review.\n',encoding='utf8')
    return str(out)
def worker_loop(root,once,poll):
    worker=f'{os.uname().nodename}-{os.getpid()}' if hasattr(os,'uname') else str(os.getpid())
    with closing(dbconn(root)) as c:
        while True:
            j=claim(c,worker)
            if j is None:
                if once:return {'status':'idle','worker':worker}
                time.sleep(poll);continue
            print(json.dumps({'event':'claimed','job_id':j['id'],'worker':worker}),flush=True)
            stop=threading.Event()
            t=threading.Thread(target=heartbeat,args=(root,j['id'],worker,stop),daemon=True)
            t.start()
            try:
                out=process_job(root,j)
                complete(c,j,'preview_ready',out)
                print(json.dumps({'event':'preview_ready','job_id':j['id'],'output':out}),flush=True)
            except Exception as e:
                message=f'{type(e).__name__}: {e}'
                if j['attempts']+1>=RETRIES: status='failed'
                else: status='queued'
                complete(c,j,status,error=message)
                print(json.dumps({'event':'error','job_id':j['id'],'error':message,'state':status}),file=sys.stderr,flush=True)
            finally:
                stop.set();t.join(timeout=3)
            if once:return {'status':'processed','job_id':j['id']}
def main():
    p=argparse.ArgumentParser(description='Multi-worker, single-host authorized video preview farm')
    p.add_argument('--root',default=os.environ.get('FARM_ROOT','./farm-data'))
    sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('init')
    q=sub.add_parser('enqueue'); q.add_argument('--source',required=True);q.add_argument('--brand',required=True)
    q.add_argument('--profile',choices=['shorts','reels','tiktok','horizontal','square'],default='shorts')
    q.add_argument('--clips',type=int,default=12);q.add_argument('--min-seconds',type=int,default=15);q.add_argument('--max-seconds',type=int,default=45)
    q.add_argument('--rights-confirmed',action='store_true')
    q=sub.add_parser('work');q.add_argument('--once',action='store_true');q.add_argument('--poll',type=float,default=5)
    sub.add_parser('list')
    args=p.parse_args();root=root_path(args.root)
    if args.cmd=='init': out={'root':str(root),'db':str(root/'state'/'jobs.sqlite')};dbconn(root).close()
    elif args.cmd=='enqueue': out=enqueue(root,args)
    elif args.cmd=='work':out=worker_loop(root,args.once,args.poll)
    else:
        with closing(dbconn(root)) as c:
            out=[dict(x) for x in c.execute('SELECT id,brand,profile,status,attempts,created,output_dir,error FROM jobs ORDER BY created DESC LIMIT 100')]
    print(json.dumps(out,indent=2))
if __name__=='__main__': main()
