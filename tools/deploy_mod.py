"""Verified, staged local deployment; no Steam or save configuration changes."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil
import tempfile
from payload import ROOT, NAMESPACE, hashes, verify


def deploy(source, mods_dir, manifest, apply=False):
    source, mods_dir = Path(source).resolve(), Path(mods_dir).absolute()
    verify(source, manifest)
    destination = mods_dir / NAMESPACE
    if any(p.is_symlink() for p in (destination, *destination.parents)):
        raise ValueError('Deployment path contains a symlink')
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Source and destination overlap')
    current = hashes(destination) if destination.exists() else None
    desired = hashes(source)
    status = 'unchanged' if current == desired else 'update' if current is not None else 'install'
    print(f'{status}: {destination}')
    if not apply or status == 'unchanged':
        return status
    mods_dir.mkdir(parents=True, exist_ok=True)
    backup_root = mods_dir.parent / 'ModBackups'
    if backup_root.is_symlink():
        raise ValueError('Backup directory must not be a symlink')
    backup = None
    with tempfile.TemporaryDirectory(prefix='.flock-deploy-', dir=mods_dir.parent) as work:
        staged = Path(work) / 'SafariZone'
        shutil.copytree(source, staged)
        if hashes(staged) != desired:
            raise ValueError('Staged payload verification failed')
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            backup_root.mkdir(exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
            backup = backup_root / f'Touma-SafariZone-{stamp}'
            destination.rename(backup)
        try:
            staged.rename(destination)
            if hashes(destination) != desired:
                raise ValueError('Installed payload verification failed')
        except BaseException:
            if destination.exists():
                shutil.rmtree(destination)
            if backup is not None:
                backup.rename(destination)
            raise
    print('Verified installed files.' + (f' Backup: {backup}' if backup else ''))
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mods-dir', required=True, type=Path)
    parser.add_argument('--source', type=Path, default=ROOT / 'dist' / NAMESPACE)
    parser.add_argument('--manifest', type=Path, default=ROOT / 'docs/build-manifest.json')
    parser.add_argument('--apply', action='store_true', help='Install/update; otherwise verify and report only')
    args = parser.parse_args()
    deploy(args.source, args.mods_dir, args.manifest, args.apply)


if __name__ == '__main__':
    main()
