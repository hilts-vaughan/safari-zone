"""Probe real elevated cave route, open chamber and blocking cliff boundary."""
import argparse,json,math,os,subprocess,tempfile
from pathlib import Path
from forest_cave_scene import APPROACH,EXIT
from forest_gate_scene import WEST,EAST
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--godot',type=Path,required=True);args=p.parse_args();walk=[]
 for a,b in list(zip(APPROACH,APPROACH[1:]))+list(zip(EXIT,EXIT[1:])):
  n=math.ceil(math.dist(a[:2],b[:2])/.45)
  for i in range(n+1):
   t=i/n;walk.append([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t])
 walk += [[-111,z,8] for z in range(-11,11)]
 boundary=[]
 for line in (WEST,EAST):
  for a,b in zip(line,line[1:]):
   n=math.ceil(math.dist(a,b));dx=-(b[1]-a[1])/math.dist(a,b);dz=(b[0]-a[0])/math.dist(a,b)
   for i in range(n+1):
    x=a[0]+(b[0]-a[0])*i/n;z=a[1]+(b[1]-a[1])*i/n;boundary.append([x-20*dx,z-20*dz,x+20*dx,z+20*dz])
 with tempfile.TemporaryDirectory(prefix='cave-check-') as d:
  f=Path(d)/'cases.json';f.write_text(json.dumps({'walk':walk,'boundary':boundary}))
  subprocess.run([str(args.godot.resolve()),'--headless','--path',str(ROOT/'editor/SceneEditor'),'--script',str(ROOT/'tools/check_cave.gd'),'--',str(f)],env=dict(os.environ,DOTNET_ROLL_FORWARD='Major',XDG_DATA_HOME=d+'/data',XDG_CONFIG_HOME=d+'/config'),check=True,timeout=60)
if __name__=='__main__':main()
