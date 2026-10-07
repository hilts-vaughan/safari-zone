"""Package native payload with reproducible ZIP metadata and content hashes."""
import json
import zipfile
from payload import ROOT, NAMESPACE, hashes


def package():
    dist = ROOT / 'dist'
    manifest = {(NAMESPACE / name).as_posix(): digest for name, digest in hashes(dist / NAMESPACE).items()}
    if (NAMESPACE / 'Level_SafariZone.json').as_posix() not in manifest:
        raise ValueError('Missing level config')
    target = dist / 'SafariZone.zip'
    staging = target.with_suffix('.zip.tmp')
    try:
        with zipfile.ZipFile(staging, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name in sorted(manifest):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, (dist / name).read_bytes(), compresslevel=9)
        staging.replace(target)
    finally:
        staging.unlink(missing_ok=True)
    (ROOT / 'docs/build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Packaged {len(manifest)} files: {target}')


if __name__ == '__main__':
    package()
