"""Failure and reproducibility checks using temporary payloads only."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from payload import NAMESPACE, hashes
from deploy_mod import deploy
import package_mod
from regression_mod import error_report, finalize, wait_for, clean


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'dist' / NAMESPACE
        self.source.mkdir(parents=True)
        (self.source / 'Level_SafariZone.json').write_text('{}')
        (self.root / 'docs').mkdir()
        self.manifest = self.root / 'docs/build-manifest.json'
        self.refresh()
        self.mods = self.root / 'save/Mods'

    def refresh(self):
        self.manifest.write_text(json.dumps({(NAMESPACE / name).as_posix(): digest for name, digest in hashes(self.source).items()}))

    def test_inspection_wait_ignores_stale_spawn_ids(self):
        log=self.root/'game.log'
        old='Spawning Noctowl with ID 69\n'
        log.write_text(old+'Spawning Noctowl with ID 153\n')
        offset=len(clean(old))
        process=Mock();process.poll.return_value=0;process.returncode=0
        match=wait_for(process,log,r'Spawning Noctowl with ID (\d+)',1,offset=offset)
        self.assertEqual(match.group(1),'153')
        log.write_text(old)
        with self.assertRaises(RuntimeError):
            wait_for(process,log,r'Spawning Noctowl with ID (\d+)',1,offset=offset)

    def test_dry_run_and_idempotent_install(self):
        deploy(self.source, self.mods, self.manifest)
        self.assertFalse(self.mods.exists())
        self.assertEqual(deploy(self.source, self.mods, self.manifest, True), 'install')
        self.assertEqual(hashes(self.source), hashes(self.mods / NAMESPACE))
        self.assertEqual(deploy(self.source, self.mods, self.manifest, True), 'unchanged')
        self.assertFalse((self.mods.parent / 'ModBackups').exists())

    def test_update_removes_stale_files_and_preserves_other_mods(self):
        deploy(self.source, self.mods, self.manifest, True)
        destination = self.mods / NAMESPACE
        (destination / 'obsolete.json').write_text('old')
        unrelated = self.mods / 'Other/mod.json'
        unrelated.parent.mkdir()
        unrelated.write_text('keep')
        deploy(self.source, self.mods, self.manifest, True)
        self.assertFalse((destination / 'obsolete.json').exists())
        self.assertEqual(unrelated.read_text(), 'keep')
        backups = list((self.mods.parent / 'ModBackups').iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / 'obsolete.json').read_text(), 'old')

    def test_corrupt_source_cannot_change_install(self):
        deploy(self.source, self.mods, self.manifest, True)
        before = hashes(self.mods / NAMESPACE)
        (self.source / 'Level_SafariZone.json').write_text('corrupt')
        with self.assertRaises(ValueError):
            deploy(self.source, self.mods, self.manifest, True)
        self.assertEqual(hashes(self.mods / NAMESPACE), before)

    def test_failed_install_restores_previous_version(self):
        deploy(self.source, self.mods, self.manifest, True)
        before = hashes(self.mods / NAMESPACE)
        (self.source / 'Level_SafariZone.json').write_text('updated')
        self.refresh()
        original = Path.rename

        def failing_rename(path, target):
            if path.parent.name.startswith('.flock-deploy-'):
                raise OSError('simulated installation failure')
            return original(path, target)

        with patch.object(Path, 'rename', failing_rename), self.assertRaises(OSError):
            deploy(self.source, self.mods, self.manifest, True)
        self.assertEqual(hashes(self.mods / NAMESPACE), before)

    def test_symlink_destination_is_rejected(self):
        self.mods.parent.mkdir()
        self.mods.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises(ValueError):
            deploy(self.source, self.mods, self.manifest, True)

    def test_zip_bytes_ignore_source_timestamps(self):
        import os
        with patch.object(package_mod, 'ROOT', self.root):
            package_mod.package()
            first = (self.root / 'dist/SafariZone.zip').read_bytes()
            os.utime(self.source / 'Level_SafariZone.json', (1700000000, 1700000000))
            package_mod.package()
            self.assertEqual((self.root / 'dist/SafariZone.zip').read_bytes(), first)

    def test_log_classification_does_not_hide_other_errors(self):
        text = '\x1b[31mERROR: System.NullReferenceException: bad\x1b[0m\n at BirdGame.Core.GameCore.FinishLoadScene(Node n)\n'
        report = error_report(text + 'ERROR: Missing branch\n at Other.Code()\n')
        self.assertEqual(len(report['localhost_startup_errors']), 1)
        self.assertEqual(len(report['unexpected_errors']), 1)
        self.assertEqual(len(error_report('ERROR: System.NullReferenceException: bad\n at Other.Code()')['unexpected_errors']), 1)

    def test_shutdown_error_cannot_leave_passing_status(self):
        report = {'status': 'passed_with_known_startup_error', 'allow_localhost_startup_error': True}
        finalize(report, 'ERROR: BUG: Unreferenced static string to 0: _set_parameter\n at: unref\n')
        self.assertEqual(report['status'], 'failed')
        self.assertIn('shutdown', report['failure'])


if __name__ == '__main__':
    unittest.main()
