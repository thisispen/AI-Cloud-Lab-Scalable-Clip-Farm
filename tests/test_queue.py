import json, subprocess, sys, tempfile, unittest
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/'video'/'queue.py'
class QueueSmoke(unittest.TestCase):
    def test_add_and_update(self):
        with tempfile.TemporaryDirectory() as td:
            db=str(Path(td)/'q.sqlite3')
            def run(*cmd):
                p=subprocess.run([sys.executable,str(SCRIPT),'--db',db,*cmd],text=True,capture_output=True)
                if p.returncode:raise AssertionError(p.stderr)
                return json.loads(p.stdout)
            job=run('add','--prompt','A 5s animation','--seconds','5')
            self.assertEqual(job['id'],1)
            self.assertEqual(run('stats'),{'pending':1})
            run('mark','--id','1','--status','completed','--output','output/test.mp4')
            self.assertEqual(run('stats'),{'completed':1})
            self.assertEqual(run('list')[0]['output_path'],'output/test.mp4')
if __name__=='__main__':unittest.main()
