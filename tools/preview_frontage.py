"""Render three Center frontage Godot scene views using an isolated display and user directory."""
import argparse,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='frontage-preview-') as work:
        work=Path(work)
        env=dict(os.environ,DOTNET_ROLL_FORWARD='Major',XDG_DATA_HOME=str(work/'data'),XDG_CONFIG_HOME=str(work/'config'))
        subprocess.run(['xvfb-run','-a','-s','-screen 0 1440x900x24',str(args.godot.resolve()),
                        '--display-driver','x11','--path',str(ROOT/'editor/SceneEditor'),
                        '--rendering-method','gl_compatibility','--resolution','1440x900',
                        '--script',str(ROOT/'tools/preview_frontage.gd'),'--',str(args.output.resolve())],
                       env=env,check=True,timeout=90)

if __name__=='__main__':main()
