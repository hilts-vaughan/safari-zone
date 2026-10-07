"""Run generator, official export, validation, and packaging in dependency order."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from payload import ROOT, NAMESPACE


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-pack', required=True, type=Path)
    parser.add_argument('--godot', required=True, type=Path, help='Godot .NET executable; editor must already be built')
    args = parser.parse_args()
    pack, godot = args.game_pack.resolve(), args.godot.resolve()
    if not pack.is_file() or not godot.is_file():
        parser.error('Game pack and Godot executable must exist')
    env = dict(os.environ, FLOCK_MOD_OUTPUT=str(ROOT / 'dist' / NAMESPACE))
    subprocess.run([sys.executable, 'tools/build_mod.py', str(pack)], cwd=ROOT, check=True)
    subprocess.run([str(godot), '--headless', '--editor', '--path', 'editor/SceneEditor', '--import'],
                   cwd=ROOT, env=env, check=True, timeout=180)
    subprocess.run([str(godot), '--headless', '--path', 'editor/SceneEditor', '--', '--export-scene',
                    'res://Levels/SafariZone.tscn', str(pack)], cwd=ROOT, env=env, check=True, timeout=180)
    subprocess.run([sys.executable, 'tools/validate_mod.py', str(pack)], cwd=ROOT, check=True)
    subprocess.run([sys.executable, 'tools/package_mod.py'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
