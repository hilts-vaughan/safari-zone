"""Covered seating in the Highlands clearing, clear of the scaffold approach."""
import math
CENTER=(77,-48)
BENCHES=[(53,-43),(60,-46)]

def build(g):
 node,sub,vec,box,prefab=[g[k] for k in ['node','sub','vec','box','prefab']]
 parent='HighlandsPavilion';node(parent,'Node3D','.')
 g['mats']['pavilionroof']=g['mat']('#91a776')
 x,z=CENTER
 # Hexagonal deck; the open south edge faces the arrival clearing.
 ring=[(x+6*math.cos(i*math.tau/6),z+6*math.sin(i*math.tau/6)) for i in range(6)]
 polygon=', '.join(str(v) for p in ring for v in p)
 node('Deck','CSGPolygon3D',parent,f'position = Vector3(0,0,0)\nrotation_degrees = Vector3(90,0,0)\npolygon = PackedVector2Array({polygon})\ndepth = 0.3\nmaterial = {g["mats"]["arrivalwood"]}\nuse_collision = true\ncollision_layer = 11\ncollision_mask = 0')
 for i,(sz,y,d) in enumerate([(z+5.9,.05,1.2),(z+5.5,.15,1.0)]):
  box('EntryStep'+str(i),(x,y,sz),(5.7,y*2,d),'arrivalwood',parent=parent)
 for i,(px,pz) in enumerate(ring):box('Post'+str(i),(x+(px-x)*.9,2.35,z+(pz-z)*.9),(.3,4.1,.3),'arrivalwood',parent=parent)
 # One cone mesh supplies every roof face, avoiding coplanar overlay panels.
 roof=sub('CylinderMesh','top_radius = 0.0\nbottom_radius = 7.0\nheight = 1.9\nradial_segments = 6')
 node('Roof','MeshInstance3D',parent,f'position = Vector3({x},5.35,{z})\nmesh = {roof}\nmaterial_override = {g["mats"]["pavilionroof"]}')
 verts=[(x,6.3,z)]+[(x+7*math.cos(i*math.tau/6),4.4,z+7*math.sin(i*math.tau/6)) for i in range(6)]
 shape=sub('ConvexPolygonShape3D','points = PackedVector3Array('+', '.join(str(v) for p in verts for v in p)+')')
 node('RoofBody','StaticBody3D',parent,'collision_layer = 11\ncollision_mask = 0');node('Shape','CollisionShape3D',parent+'/RoofBody','shape = '+shape)
 def segment(name,a,b,y,width,height):
  dx,dz=b[0]-a[0],b[1]-a[1]
  node(name,'Node3D',parent,f'position = {vec(((a[0]+b[0])/2,y,(a[1]+b[1])/2))}\nrotation_degrees = Vector3(0,{math.degrees(math.atan2(dx,dz))},0)')
  box('Timber',(0,0,0),(width,height,math.hypot(dx,dz)),'arrivalwood',parent=parent+'/'+name)
 for i in range(6):
  a,b=ring[i],ring[(i+1)%6]
  segment('Header'+str(i),a,b,4.25,.24,.25)
  # Rear and side enclosure only; the two forward diagonal edges stay open.
  if i in (0,1):continue
  a=(x+(a[0]-x)*.88,z+(a[1]-z)*.88);b=(x+(b[0]-x)*.88,z+(b[1]-z)*.88)
  segment('HalfWall'+str(i),a,b,1.0,.14,1.4)
  a=(x+(a[0]-x)*.90,z+(a[1]-z)*.90);b=(x+(b[0]-x)*.90,z+(b[1]-z)*.90)
  segment('BenchSeat'+str(i),a,b,.85,.65,.16)
  for j,p in enumerate([a,b]):box(f'SeatLeg{i}_{j}',(p[0],.54,p[1]),(.18,.48,.45),'arrivalwood',parent=parent)
 # Picnic table and seats rest on the deck, with room to circulate around them.
 box('TableTop',(x,1.35,z),(3.2,.16,1.4),'plank',parent=parent)
 for side in (-1,1):
  box('TableLeg'+str(side),(x+side*1.05,.79,z),(.2,.98,1.0),'arrivalwood',parent=parent)
  box('TableSeat'+str(side),(x,.86,z+side*1.2),(3.5,.16,.45),'plank',parent=parent)
  for end in (-1,1):box(f'TableSeatLeg{side}_{end}',(x+end*1.15,.54,z+side*1.2),(.18,.48,.38),'arrivalwood',parent=parent)
 for i,(bx,bz) in enumerate(BENCHES):
  box(f'LeftBench{i}Seat',(bx,.64,bz),(3.6,.16,.85),'plank',parent=parent)
  for j in range(3):box(f'LeftBench{i}Back{j}',(bx,1.0+j*.24,bz-.5),(3.6,.18,.14),'plank',parent=parent)
  for side in (-1,1):
   box(f'LeftBench{i}Leg{side}',(bx+side*1.2,.28,bz),(.18,.56,.7),'arrivalwood',parent=parent)
   box(f'LeftBench{i}Support{side}',(bx+side*1.2,.88,bz-.5),(.16,1.5,.16),'arrivalwood',parent=parent)
 for i,(fx,fz) in enumerate([(70.8,-44),(83.2,-44),(51,-43),(58,-46)]):
  prefab('PavilionFlowers'+str(i),'Decorations/Flowers',(fx,.03,fz),(.045,.045,.045))
 return {'center':CENTER,'radius':6,'roof_radius':7,'outside_benches':2,'interior_benches':4,'picnic_tables':1}
