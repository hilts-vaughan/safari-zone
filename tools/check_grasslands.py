"""Check real Godot ground routes, hedge entrances and elevated walk surfaces."""
import argparse,json,math,os,subprocess,tempfile
from pathlib import Path
from map_layout import segments
from grasslands_layout import contains,walkway_samples,POCKETS,hedges,DECK,HEIGHT
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot',required=True,type=Path)
    args=parser.parse_args()
    points=[]
    for a,b in segments():
        length=math.dist(a,b);count=max(1,math.ceil(length/.8))
        for i in range(count+1):
            p=[a[j]+(b[j]-a[j])*i/count for j in range(2)]
            if contains(p):
                for offset in [-.7,0,.7]:points.append([p[0]-(b[1]-a[1])/length*offset,p[1]+(b[0]-a[0])/length*offset])
    for x,z,rx,rz in POCKETS:
        for dz in range(-math.ceil(rz)-3,math.ceil(rz)+4):points.append([x,z+dz])
    walk=walkway_samples()
    x,z,w,d=DECK
    for dx in [-2,-1,0,1,2]:
        for dz in [-2,0,2]:walk.append([x+dx,z+dz,HEIGHT])
    checks={'walk':walk,'paths':points,'cliffs':[[-143,z] for z in range(6,63)],'hedges':[[a[0],a[1]] for _,a,b in hedges()[::9]]}
    with tempfile.TemporaryDirectory(prefix='grasslands-check-') as work:
        work=Path(work);samples=work/'points.json';samples.write_text(json.dumps(checks))
        env=dict(os.environ,DOTNET_ROLL_FORWARD='Major',XDG_DATA_HOME=str(work/'data'),XDG_CONFIG_HOME=str(work/'config'))
        subprocess.run([str(args.godot.resolve()),'--headless','--path',str(ROOT/'editor/SceneEditor'),'--script',str(ROOT/'tools/check_grasslands.gd'),'--',str(samples)],env=env,check=True,timeout=60)

if __name__=='__main__':main()
