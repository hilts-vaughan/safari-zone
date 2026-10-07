"""Check actual Godot cliff continuity and player clearance without editing assets."""
import argparse,json,math,os,subprocess,tempfile
from pathlib import Path
from map_layout import segments
from woodland_section import ORIGIN,contains
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot',required=True,type=Path)
    args=parser.parse_args()
    points=[]
    for a,b in segments():
        count=max(1,math.ceil(math.dist(a,b)))
        for i in range(count+1):
            p=[a[j]+(b[j]-a[j])*i/count for j in range(2)]
            if contains(p):
                length=math.dist(a,b)
                normal=[-(b[1]-a[1])/length,(b[0]-a[0])/length]
                for offset in [-.85,0,.85]:
                    points.append([p[j]-ORIGIN[j]+normal[j]*offset for j in range(2)])
    with tempfile.TemporaryDirectory(prefix='woodland-check-') as work:
        work=Path(work);samples=work/'points.json';samples.write_text(json.dumps(points))
        env=dict(os.environ,DOTNET_ROLL_FORWARD='Major',XDG_DATA_HOME=str(work/'data'),XDG_CONFIG_HOME=str(work/'config'))
        subprocess.run([str(args.godot.resolve()),'--headless','--path',str(ROOT/'editor/SceneEditor'),'--script',str(ROOT/'tools/check_woodland.gd'),'--',str(samples)],env=env,check=True,timeout=60)
if __name__=='__main__':main()
