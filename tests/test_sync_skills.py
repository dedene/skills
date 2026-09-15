import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('sync_skills', Path(__file__).parents[1] / 'scripts/sync-skills.py')
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class SyncSkillsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source, self.target = self.root / 'source', self.root / 'target'
        self.source.mkdir()
        self.target.mkdir()
        (self.source / 'SKILL.md').write_text('new')
        (self.source / 'second.md').write_text('second')
        (self.target / 'SKILL.md').write_text('old')
        (self.target / 'extra.md').write_text('keep')
        self.manifest = self.root / 'manifest.json'
        self.manifest.write_text(json.dumps([dict(name='test', source=str(self.source), targets=[str(self.target)])]))

    def plan(self):
        return sync.build_plan(self.manifest)

    def test_plan_does_not_write_and_apply_is_idempotent(self):
        plan = self.plan()
        self.assertEqual((self.target / 'SKILL.md').read_text(), 'old')
        self.assertFalse((self.target / 'second.md').exists())
        backup = sync.apply_plan(plan)
        index = json.loads((backup / 'index.json').read_text())
        old = next(item for item in index if item['destination'].endswith('SKILL.md'))
        self.assertEqual((backup / old['backup']).read_text(), 'old')
        self.assertEqual((self.target / 'SKILL.md').read_text(), 'new')
        self.assertEqual((self.target / 'extra.md').read_text(), 'keep')
        self.assertEqual(self.plan()['changes'], [])
        self.assertIsNone(sync.apply_plan(self.plan()))

    def test_changed_destination_rejected_before_any_write(self):
        plan = self.plan()
        (self.target / 'second.md').write_text('user edit')
        with self.assertRaisesRegex(ValueError, 'Destination changed'):
            sync.apply_plan(plan)
        self.assertEqual((self.target / 'SKILL.md').read_text(), 'old')
        self.assertEqual((self.target / 'second.md').read_text(), 'user edit')

    def test_changed_source_rejected_before_any_write(self):
        plan = self.plan()
        (self.source / 'second.md').write_text('new source edit')
        with self.assertRaisesRegex(ValueError, 'Source changed'):
            sync.apply_plan(plan)
        self.assertEqual((self.target / 'SKILL.md').read_text(), 'old')
        self.assertFalse((self.target / 'second.md').exists())

    def test_ignored_files_and_same_source_symlink(self):
        (self.source / '__pycache__').mkdir()
        (self.source / '__pycache__/cache.pyc').write_bytes(b'cache')
        (self.source / '.DS_Store').write_bytes(b'metadata')
        self.assertEqual(len(self.plan()['changes']), 2)
        alias = self.root / 'alias'
        alias.symlink_to(self.source, target_is_directory=True)
        self.manifest.write_text(json.dumps([dict(name='test', source=str(self.source), targets=[str(alias)])]))
        self.assertEqual(self.plan()['changes'], [])

    def test_traversal_directory_conflict_and_symlink_rejected(self):
        plan = self.plan()
        plan['changes'][0]['relative'] = '../escape'
        with self.assertRaisesRegex(ValueError, 'Unsafe relative'):
            sync.apply_plan(plan)
        (self.target / 'second.md').mkdir()
        with self.assertRaisesRegex(ValueError, 'Expected file'):
            self.plan()
        (self.source / 'linked').symlink_to(self.root)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            self.plan()

    def test_overlapping_roots_rejected(self):
        self.manifest.write_text(json.dumps([dict(name='test', source=str(self.source), targets=[str(self.source / 'installed')])]))
        with self.assertRaisesRegex(ValueError, 'Overlapping'):
            self.plan()


if __name__ == '__main__':
    unittest.main()
