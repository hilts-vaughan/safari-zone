"""Bounds and placement of the editor-authored northern-fork study."""
ORIGIN=(-5,-43)
SCENE='res://EXTERNAL/Touma/SafariZone/Woodland/WoodlandPassage.tscn'
SOURCE='assets/environment/woodland/WoodlandPassage.tscn'
def contains(p,margin=0):
 x,z=p[0]-ORIGIN[0],p[1]-ORIGIN[1]
 return -47-margin<x<46+margin and -42-margin<z<23+margin

def plan():
 """Read preview geometry from the saved scene so layout has one source."""
 import re
 from pathlib import Path
 text=(Path(__file__).resolve().parents[1]/SOURCE).read_text()
 result={'cliffs':[],'hedges':[],'trees':[]}
 for block in re.split(r'(?=\[node )',text):
  header=block.splitlines()[0]
  transform=re.search(r'transform = Transform3D\(([^)]+)\)',block)
  if transform:
   values=[float(v) for v in transform[1].split(',')]
   position=(values[-3]+ORIGIN[0],values[-1]+ORIGIN[1])
   if re.search(r'name="FloweringHedge\d+"',header):result['hedges'].append(position)
   if re.search(r'name="(?:Tree|SkylineTree)\d+"',header):result['trees'].append(position)
  polygon=re.search(r'polygon = PackedVector2Array\(([^)]+)\)',block)
  if polygon and 'parent="Escarpments"' in header and 'Turf' not in header:
   values=[float(v) for v in polygon[1].split(',')]
   result['cliffs'].append([(values[i]+ORIGIN[0],values[i+1]+ORIGIN[1]) for i in range(0,len(values),2)])
 return result
