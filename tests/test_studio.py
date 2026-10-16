import tempfile
import unittest
from pathlib import Path
from studio.creative import plan, save, safe_name, PROFILES
from studio.costs import estimate
from studio.review import review
from studio.edit import assemble, media_info
import shutil
import subprocess

class StudioPlanningTests(unittest.TestCase):
    def test_profiles_and_hooks(self):
        self.assertEqual(PROFILES["instagram_reels"]["ratio"], "9:16")
        p=plan("New ad", "facebook_ad", "eco mug", "commuters", "trial", 30)
        self.assertEqual(len(p["hooks"]), 3)
        self.assertEqual(p["status"], "CREATIVE_DRAFT_REQUIRES_REVIEW")
        self.assertFalse(p["distribution"]["publish_automatically"])
        self.assertFalse(p["distribution"]["paid_ads_enabled"])
        self.assertNotIn('A study shows', str(p))
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/"project"
            paths=save(p,dest)
            self.assertTrue(all(path.exists() for path in paths))
            with self.assertRaises(FileExistsError): save(p,dest)

    def test_validation(self):
        with self.assertRaises(ValueError):
            plan('Test','youtube_short','app','people','trial',1)
        self.assertEqual(safe_name("Video & App"), "video-app")

    def test_costs(self):
        self.assertEqual(estimate('veo31_lite_720', 1000*15, 2), 1500.)
        self.assertEqual(estimate('runway_gen4_turbo',5,1),0.25)
        with self.assertRaises(ValueError):estimate('runway_gen4_turbo', 5, 0)

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'ffmpeg not installed')
    def test_render_and_technical_review(self):
        with tempfile.TemporaryDirectory() as d:
            tmp=Path(d)
            clips=[]
            for n in range(2):
                clip=tmp/f"clip{n}.mp4"
                subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',f'color=c={"blue" if n==0 else "purple"}:s=320x180:r=30',
                    '-t','2.75','-an','-c:v','libx264','-pix_fmt','yuv420p',str(clip)],capture_output=True,check=True)
                clips.append(clip)
            target=tmp/'final.mp4'
            rendered=assemble(clips,target,'vertical',width=360,height=640)
            self.assertAlmostEqual(rendered['duration_seconds'],5.5,delta=0.2)
            self.assertEqual((rendered['width'],rendered['height']),(360,640))
            checked=review(target,'vertical',min_seconds=5)
            self.assertTrue(checked['technical_pass'],checked)
            self.assertIn('NOT PERFORMED',checked['creative_review'])
            self.assertTrue(rendered['audio'])

if __name__ == '__main__': unittest.main()
