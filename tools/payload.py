"""Shared payload integrity checks for packaging, deployment, and runtime tests."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = Path('Touma/SafariZone')


def hashes(directory):
    directory = Path(directory)
    if not directory.is_dir() or directory.is_symlink():
        raise ValueError(f'Not a regular payload directory: {directory}')
    result = {}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Symlinks are not allowed in a payload: {path}')
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def verify(source, manifest):
    expected = json.loads(Path(manifest).read_text())
    prefix = NAMESPACE.as_posix() + '/'
    if not expected or any(not name.startswith(prefix) for name in expected):
        raise ValueError('Manifest must contain only Touma/SafariZone files')
    actual = {prefix + name: digest for name, digest in hashes(source).items()}
    if actual != expected:
        raise ValueError('Payload differs from build manifest; validate and package again')
    if prefix + 'Level_SafariZone.json' not in actual:
        raise ValueError('Missing level config')
    return actual
