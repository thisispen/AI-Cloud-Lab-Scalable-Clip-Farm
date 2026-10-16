"""Read-only tests for costs, routing, release observations, and quality benchmarks."""
import tempfile
import unittest
from pathlib import Path
from studio.router import load_data, plan
from studio.production_budget import estimate
from studio.benchmark import record, summarize
from studio.release_watch import safe_release, check
from studio.style_fingerprint import fingerprint


class AdaptiveStudioTests(unittest.TestCase):
    def test_catalog_blocks_payments_and_publishing(self):
        c,p=load_data()
        self.assertFalse(p['paid_apis_enabled'])
        self.assertFalse(p['automated_purchases_enabled'])
        self.assertFalse(p['production_auto_publish_enabled'])
        self.assertEqual(p['monthly_max_new_spend_usd'],0)
        for m in c['generation_models']:
            self.assertFalse(m['connected'])

    def test_router_never_unlocks_paid_calls(self):
        q=plan('facebook_ads',5,2)
        self.assertEqual(q['layout'],'vertical')
        self.assertEqual(q['generation_candidates_lowest_listed_price_first'][0]['estimated_generation_usd_per_video'],0.5)
        self.assertTrue(all(x['blocked_until_approval'] for x in q['generation_candidates_lowest_listed_price_first']))
        self.assertFalse(q['permission_state']['production_auto_publish_enabled'])

    def test_all_platforms_have_tool_plan(self):
        c,p=load_data()
        for name in c['platforms']:
            with self.subTest(platform=name):
                self.assertGreaterEqual(len(plan(name,catalog=c,policy=p)['editing_candidates_lowest_subscription_first']),1)

    def test_hybrid_vs_full_ai_budget(self):
        hybrid=estimate(videos=1000,final_seconds=30,generated_seconds=5,attempts=2,storage_gb=100)
        self.assertEqual(hybrid['expenses']['generation_usd'],500.0)
        self.assertEqual(hybrid['expenses']['storage_usd_per_month_estimate'],1.35)
        full=estimate(videos=1000,final_seconds=15,generated_seconds=15,attempts=2,storage_gb=0)
        self.assertEqual(full['expenses']['generation_usd'],1500)
        with self.assertRaises(ValueError):estimate(videos=100,final_seconds=10,generated_seconds=11)

    def test_honest_quality_benchmark(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'results.csv'
            record(path,'modelA','hook1',8,True,5,0.25)
            record(path,'modelA','hook2',3,False,5,0.25)
            r=summarize(path)
            x=r['models'][0]
            self.assertEqual(x['tests'],2)
            self.assertFalse(x['ready_for_cost_quality_comparison'])
            self.assertEqual(x['acceptance_rate'],0.5)
            self.assertEqual(x['usd_per_accepted_attempt'],0.5)

    def test_release_check_requires_manual_review(self):
        r=safe_release('Comfy-Org/ComfyUI',{'tag_name':'v0.5.2',
            'html_url':'https://github.com/Comfy-Org/ComfyUI/releases/tag/v0.5.2'})
        self.assertEqual(r['status'],'unreviewed_candidate')
        self.assertFalse(r['automatic_upgrade'])
        self.assertEqual(safe_release('Comfy-Org/ComfyUI',{'tag_name':'v0.5.2',
            'html_url':'https://github.com/Comfy-Org/ComfyUI/releases/tag/v0.5.2'},'v0.5.2')['status'],
            'approved_version_current')
        with self.assertRaises(ValueError):safe_release('Comfy-Org/ComfyUI',{'tag_name':'v0.5.2','html_url':'http://evil/'})
        r=check(['Comfy-Org/ComfyUI'],fetch=lambda repo:{'tag_name':'v0.5.2',
            'html_url':'https://github.com/Comfy-Org/ComfyUI/releases/tag/v0.5.2'})
        self.assertEqual(r['checked_sources'],1)

    def test_reference_fingerprint_offline(self):
        demo=Path(__file__).resolve().parents[1]/'output'/'cloud-lab-demo.mp4'
        if not demo.is_file():self.skipTest('Bundled synthetic test video unavailable')
        info=fingerprint(demo,sample_seconds=2)
        self.assertGreater(info['duration_seconds'],0)
        self.assertGreater(info['width'],0)
        self.assertLessEqual(info['analyzed_seconds'],2)


if __name__=='__main__':unittest.main()

class QualityRouterTests(unittest.TestCase):
    def test_no_winner_without_matched_prompt_samples(self):
        from studio.quality_router import propose
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bench.csv'
            record(p,'A','prompt-a',9,True,5,0.9)
            record(p,'B','prompt-b',8,True,5,0.2)
            result=propose(p)
            self.assertIsNone(result['proposal'])
            self.assertFalse(result['automatic_switch'])

    def test_paired_prompts_pick_cheapest_acceptable(self):
        from studio.quality_router import propose
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'bench.csv'
            for i in range(10):
                record(p,'A',f'prompt-{i}',9,True,5,0.70)
                record(p,'B',f'prompt-{i}',8,True,5,0.25)
            self.assertEqual(propose(p)['proposal'],'B')
            self.assertEqual(propose(p,goal='highest_quality')['proposal'],'A')
            self.assertFalse(propose(p)['automatic_switch'])
