import concurrent.futures, json, pathlib, subprocess, tempfile, unittest
from argparse import Namespace
from contextlib import closing
from farmworker.__main__ import dbconn, root_path, enqueue, claim, worker_loop

class WorkerTests(unittest.TestCase):
    def test_unique_claims(self):
        with tempfile.TemporaryDirectory() as folder:
            root=root_path(folder)
            media=root/'inputs'/'sample.mp4'; media.write_bytes(b'placeholder')
            args=Namespace(source='sample.mp4',brand='news',clips=1,min_seconds=5,max_seconds=10,profile='shorts',rights_confirmed=True)
            enqueue(root,args);enqueue(root,args)
            def take(name):
                with closing(dbconn(root)) as c:return claim(c,name)
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                a,b=list(pool.map(take,['one','two']))
            self.assertNotEqual(a['id'],b['id'])
    def test_requires_rights(self):
        with tempfile.TemporaryDirectory() as folder:
            root=root_path(folder)
            media=root/'inputs'/'sample.mp4';media.write_bytes(b'placeholder')
            args=Namespace(source='sample.mp4',brand='one',clips=1,min_seconds=5,max_seconds=10,profile='shorts',rights_confirmed=False)
            with self.assertRaises(PermissionError): enqueue(root,args)
    def test_render_preview(self):
        with tempfile.TemporaryDirectory() as folder:
            root=root_path(folder)
            media=root/'inputs'/'sample.mp4'
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-f','lavfi','-i','color=c=blue:s=160x90:r=10:d=6','-c:v','libx264','-pix_fmt','yuv420p','-y',str(media)],check=True)
            args=Namespace(source='sample.mp4',brand='tech',clips=1,min_seconds=3,max_seconds=5,profile='shorts',rights_confirmed=True)
            job=enqueue(root,args)
            worker_loop(root,True,0.01)
            with closing(dbconn(root)) as c:
                state=c.execute('SELECT * FROM jobs WHERE id=?',(job['job_id'],)).fetchone()
                self.assertEqual(state['status'],'preview_ready')
                self.assertTrue((pathlib.Path(state['output_dir'])/'previews'/'clip-001-preview.mp4').exists())

if __name__=='__main__': unittest.main()
