"""Probe continuous forest fence collisions and an unobstructed opened passage."""
import argparse,json,math,os,subprocess,tempfile
from pathlib import Path
from forest_gate_scene import WEST,EAST,GATE
ROOT=Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--godot',required=True,type=Path);args=parser.parse_args()
 rays=[]
 for line in (WEST,EAST):
  for a,b in zip(line,line[1:]):
   length=math.dist(a,b);n=math.ceil(length/.4);dx=-(b[1]-a[1])/length;dz=(b[0]-a[0])/length
   for i in range(n+1):
    x=a[0]+(b[0]-a[0])*i/n;z=a[1]+(b[1]-a[1])*i/n;rays.append([x-10*dx,z-10*dz,x+10*dx,z+10*dz])
 passage=[[GATE[0]+offset,GATE[1]+dz/2] for offset in (-1,0,1) for dz in range(-8,9)]
 with tempfile.TemporaryDirectory(prefix='forest-check-') as work:
  work=Path(work);file=work/'points.json';file.write_text(json.dumps({'fences':rays,'passage':passage}))
  env=dict(os.environ,DOTNET_ROLL_FORWARD='Major',XDG_DATA_HOME=str(work/'data'),XDG_CONFIG_HOME=str(work/'config'))
  subprocess.run([str(args.godot.resolve()),'--headless','--path',str(ROOT/'editor/SceneEditor'),'--script',str(ROOT/'tools/check_forest.gd'),'--',str(file)],env=env,check=True,timeout=60)
if __name__=='__main__':main()
