"""Verify the sculpted reserve terrain leaves the entire existing trail graph flat."""
import argparse,json,math,os,subprocess,tempfile
from pathlib import Path
from map_layout import segments
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--godot',required=True,type=Path);a=p.parse_args()
 samples=[]
 for first,last in segments():
  length=math.dist(first,last);count=max(1,math.ceil(length/.7))
  nx,nz=-(last[1]-first[1])/length,(last[0]-first[0])/length
  for i in range(count+1):
   for offset in [-1,0,1]:samples.append([first[0]+(last[0]-first[0])*i/count+nx*offset,first[1]+(last[1]-first[1])*i/count+nz*offset])
 with tempfile.TemporaryDirectory(prefix='terrain-check-') as work:
  work=Path(work);file=work/'samples.json';file.write_text(json.dumps(samples))
  env=dict(os.environ,DOTNET_ROLL_FORWARD='Major',XDG_DATA_HOME=str(work/'data'),XDG_CONFIG_HOME=str(work/'config'))
  subprocess.run([str(a.godot.resolve()),'--headless','--path',str(ROOT/'editor/SceneEditor'),'--script',str(ROOT/'tools/check_terrain.gd'),'--',str(file)],env=env,check=True,timeout=60)
if __name__=='__main__':main()
