import tempfile, unittest
from pathlib import Path
from video.batch import add_prompts
from video.queue import db_connect

class BatchTests(unittest.TestCase):
    def test_enqueues_without_api(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / 'jobs.sqlite3'
            n = add_prompts(db, ['cinematic A', 'cinematic B', '  '])
            self.assertEqual(n, 2)
            with db_connect(db) as conn:
                self.assertEqual(conn.execute('select count(*) from jobs').fetchone()[0],2)
                self.assertTrue(all(x[0]=='pending' for x in conn.execute('select status from jobs')))
    def test_rejects_invalid_seconds(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                add_prompts(Path(td)/'db.sqlite3',['A'],0)
