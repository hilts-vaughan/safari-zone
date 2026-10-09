"""Flower-lined seating pocket beside the southern Highlands trail."""
import math
BENCHES=[(35,-22),(25,-35)]
def reserved(p):
 return ((p[0]-30)/10)**2+((p[1]+28)/11)**2<1

def build(g):
 from sculpted_terrain import surface
 from park_perches import flat
 from map_layout import path_distance
 node,sub,vec,box,prefab=[g[k] for k in ['node','sub','vec','box','prefab']]
 parent='HighlandsRestGarden';node(parent,'Node3D','.')
 for i,(x,z) in enumerate(BENCHES):
  for j in range(4):box(f'Bench{i}Seat{j}',(x,.64,z-.39+j*.26),(3.6,.16,.23),'plank',parent=parent)
  for j in range(3):box(f'Bench{i}Back{j}',(x,1+j*.24,z-.58),(3.6,.18,.14),'plank',parent=parent)
  for side in (-1,1):
   box(f'Bench{i}Leg{side}',(x+side*1.2,.28,z),(.18,.56,.8),'arrivalwood',parent=parent)
   box(f'Bench{i}Support{side}',(x+side*1.2,.9,z-.58),(.16,1.5,.16),'arrivalwood',parent=parent)
  flat(g,'RestBenchLanding'+str(i),(x,.725,z),3.3,.70)
 # One continuous polygon joins the oval pocket to the nearby main trail.
 points=[(30+6*math.cos(i*math.tau/24),-28+4*math.sin(i*math.tau/24)) for i in range(24)]
 # The southeast sector extends as a narrow path spur, without overlapping disks.
 points[21:23]=[(38,-32.8),(42,-32),(42,-30.3),(37,-30.5)]
 node('RestPath','CSGPolygon3D',parent,'position = Vector3(0,0.075,0)\nrotation_degrees = Vector3(90,0,0)\npolygon = PackedVector2Array('+', '.join(str(v) for p in points for v in p)+')\ndepth = 0.015\nmaterial = '+g['mats']['path']+'\nuse_collision = false')
 # Shrubs frame the stone and seats, leaving their approach lanes open.
 mesh=sub('SphereMesh','radius = 0.5\nheight = 1\nradial_segments = 8\nrings = 4')
 plants=[(32,-30,.65),(26.5,-29,.65),(30,-31.5,.55),(37.5,-22,.7),(22.5,-35,.7),(26,-39,.6),(31,-38,.7),(34,-37,.6)]
 for i,(x,z,s) in enumerate(plants):
  if path_distance((x,z))<3.5:continue
  y,_=surface(x,z)
  node('Shrub'+str(i),'MeshInstance3D',parent,f'position = {vec((x,y+s*.45,z))}\nscale = {vec((s*2,s,s*1.6))}\nmesh = {mesh}\nmaterial_override = {g["mats"]["leaf"]}')
  prefab('Flowers'+str(i),'Decorations/Flowers',(x+.65,y+.025,z+.5),(.045,.045,.045))
 # Plant directly on sampled hill surfaces; nothing floats above the slope.
 for i,(x,z) in enumerate([(20,-23),(20,-28),(21,-32),(18,-27),(17,-31)]):
  y,normal=surface(x,z)
  if path_distance((x,z))<4:continue
  node('HillShrub'+str(i),'MeshInstance3D',parent,f'position = {vec((x,y+.22,z))}\nscale = Vector3(1.1,0.65,1)\nmesh = {mesh}\nmaterial_override = {g["mats"]["leaf"]}')
  prefab('HillFlowers'+str(i),'Decorations/Flowers',(x+1,y+.025,z),(.035,.035,.035))
 # A supported native Rock hangout attracts birds to the visible feeder tray.
 x,z=33,-34
 box('FeederPost',(x,1.1,z),(.18,2.2,.18),'arrivalwood',parent=parent)
 box('FeederTray',(x,2.24,z),(1.3,.12,.9),'plank',parent=parent)
 box('FeederRoof',(x,2.95,z),(1.6,.16,1.15),'arrivalwood',parent=parent)
 for side in (-1,1):box('FeederUpright'+str(side),(x+side*.5,2.6,z),(.09,.6,.09),'arrivalwood',parent=parent)
 flat(g,'RestFeederLanding',(x,2.31,z),1.05,.7)
 return {'benches':BENCHES,'feeder':(x,z),'rock':(29,-29),'plant_groups':len(plants)+5}
