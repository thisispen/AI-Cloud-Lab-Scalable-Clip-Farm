"""Offline validation; the synthetic source includes no copyrighted input."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from clipfarm.core import probe,suggest
from clipfarm.fetch import fetch,validate_url
from clipfarm.render import render_manifest
from clipfarm.accounts import export_account_queue
from clipfarm.highlights import parse_srt,rank_srt


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'ffmpeg tools missing')
class ClipFarmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.dir=Path(cls.tmp.name)
        cls.video=cls.dir/'source.mp4'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',
             '-f','lavfi','-i','testsrc2=size=640x360:rate=15',
             '-f','lavfi','-i','sine=frequency=440:sample_rate=16000',
             '-t','9','-c:v','libx264','-preset','ultrafast','-crf','31',
             '-c:a','aac','-shortest',str(cls.video)],check=True)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_probe(self):
        d=probe(self.video)
        self.assertGreater(d['duration'],8)
        self.assertEqual(d['width'],640)
        self.assertTrue(d['has_audio'])

    def test_suggest_review_required(self):
        plan=suggest(self.video,minimum=3,maximum=5,count=2)
        self.assertTrue(plan['clips'])
        self.assertFalse(plan['clips'][0]['approved'])

    def test_render_and_draft_accounts(self):
        plan=suggest(self.video,minimum=3,maximum=5,count=2)
        source=self.dir/'plan.json';source.write_text(json.dumps(plan))
        with self.assertRaises(PermissionError):
            render_manifest(source,self.dir/'cannot-final')
        previews=render_manifest(source,self.dir/'previews',preview=True)
        self.assertEqual(len(previews['outputs']),2)
        for result in previews['outputs']:
            details=probe(result['path'])
            self.assertEqual(details['width'],360)
            self.assertEqual(details['height'],640)
        accounts=self.dir/'accounts.json';accounts.write_text('[{"name":"test","platform":"tiktok"}]')
        q=self.dir/'drafts.csv'
        self.assertEqual(export_account_queue(self.dir/'previews'/'manifest.json',accounts,q),2)
        self.assertIn('awaiting_editor_approval',q.read_text())
        plan['clips'][0]['approved']=True
        plan['clips']=plan['clips'][:1]
        source.write_text(json.dumps(plan))
        copies=render_manifest(source,self.dir/'fastcuts',fast_copy=True)
        self.assertEqual(len(copies['outputs']),1)
        self.assertTrue(copies['outputs'][0]['fast_copy_keyframe_approximation'])

    def test_srt_candidate_scores(self):
        srt=self.dir/'captions.srt'
        srt.write_text('1\n00:00:00,000 --> 00:00:02,000\nThe biggest mistake I learned\n\n'
                       '2\n00:00:02,500 --> 00:00:06,000\nHere is why it matters\n\n')
        self.assertEqual(len(parse_srt(srt)),2)
        data=rank_srt(self.video,srt,seconds=5,count=2)
        self.assertTrue(data['clips'])
        self.assertFalse(data['clips'][0]['approved'])

    def test_download_consent(self):
        with self.assertRaises(PermissionError):fetch('https://example.com/test.mp4',self.dir/'test.mp4')
        with self.assertRaises(ValueError):validate_url('http://127.0.0.1/private.mp4')

if __name__=='__main__':unittest.main()
