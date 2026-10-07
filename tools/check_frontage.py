"""Check entrance routes and every turn of the observation tower in real Godot physics."""
import argparse,json,math,os,subprocess,tempfile
from pathlib import Path
from map_layout import segments
from frontage_landscape import fences,PERCHES
from frontage_scene import contains,TOWER,HEIGHT,RADIUS,TURNS,APPROACH
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--godot',required=True,type=Path);p.add_argument('--descending',action='store_true');a=p.parse_args()
 paths=[]
 for start,end in list(segments())+list(zip(APPROACH,APPROACH[1:])):
  length=math.dist(start,end);count=max(1,math.ceil(length/.6))
  for i in range(count+1):
   x,z=[start[j]+(end[j]-start[j])*i/count for j in range(2)]
   if contains((x,z)):
    for offset in [-.6,0,.6]:paths.append([x-(end[1]-start[1])/length*offset,z+(end[0]-start[0])/length*offset])
 walk=[]
 for i in range(601):
  t=i*TURNS*2*math.pi/600
  for radius in [1.65,RADIUS,2.55]:walk.append([TOWER[0]+radius*math.cos(t),TOWER[1]+radius*math.sin(t),i*HEIGHT/600])
 for i in range(1,18):walk.append([TOWER[0]+RADIUS+i*.11,TOWER[1],HEIGHT])
 with tempfile.TemporaryDirectory(prefix='frontage-check-') as work:
  work=Path(work);cases=work/'points.json';cases.write_text(json.dumps(dict(paths=paths,walk=walk,descending=a.descending,fences=fences(),perches=PERCHES)))
  env=dict(os.environ,DOTNET_ROLL_FORWARD='Major',XDG_DATA_HOME=str(work/'data'),XDG_CONFIG_HOME=str(work/'config'),XDG_CACHE_HOME=str(work/'cache'))
  subprocess.run([str(a.godot.resolve()),'--headless','--path',str(ROOT/'editor/SceneEditor'),'--script',str(ROOT/'tools/check_frontage.gd'),'--',str(cases)],env=env,check=True,timeout=90)
if __name__=='__main__':main()
