"""Center arrival garden and fifteen-metre spiral observation tower."""
import math
from frontage_landscape import GATES
TOWER=(-40,89)
HEIGHT=15
RADIUS=2.1
STEPS=120
TURNS=5
APPROACH=[(-50,85),(-45,83),(-40,83),(-34,84),(-34,89),(-37.9,89)]

def contains(p,margin=0):return -101-margin<p[0]<-26+margin and 64-margin<p[1]<104+margin

def build(g):
 from park_perches import flat,rail
 node,sub,vec,box,prefab,mat=[g[n] for n in ['node','sub','vec','box','prefab','mat']]
 for k,c in [('arrivalwood','#a9794f'),('arrivaldark','#805c3d'),('arrivalstone','#a8ada6'),('arrivalgreen','#628954'),('arrivalwater','#71b8c6')]:g['mats'][k]=mat(c)
 node('CenterArrival','Node3D','.')
 par='CenterArrival'
 def solid(n,p,s,m='arrivalwood',solid=True):box(n,p,s,m,solid=solid,parent=par)
 unit=sub('BoxMesh','size = Vector3(1, 1, 1)')
 def detail(n,p,s,m='arrivalwood',rot=(0,0,0)):
  node(n,'MeshInstance3D',par,f'position = {vec(p)}\nscale = {vec(s)}\nrotation_degrees = {vec(rot)}\nmesh = {unit}\nmaterial_override = {g["mats"][m]}')
 def beam(n,a,b,w=0.16,m='arrivalwood',collision=False):
  dx,dy,dz=[b[i]-a[i] for i in range(3)];length=math.sqrt(dx*dx+dy*dy+dz*dz)
  angle=math.degrees(math.atan2(dx,dz));slope=-math.degrees(math.atan2(dy,math.hypot(dx,dz)))
  pos=tuple((a[i]+b[i])/2 for i in range(3))
  detail(n,pos,(w,w,length),m,(slope,angle,0))
  if (n.startswith('DeckRail') and n.endswith('_1.1')) or (n.startswith('SpiralRail') and '_3.1_1.12' in n and int(n.split('_')[0].replace('SpiralRail',''))%12==0):
   rail(g,n+'Landing',a,b,w,par)
  if collision:
   node(n+'Body','StaticBody3D',par,f'position = {vec(pos)}\nrotation_degrees = {vec((slope,angle,0))}\ncollision_layer = 11\ncollision_mask = 0')
   shape=sub('BoxShape3D','size = '+vec((w,w,length)))
   node('Shape','CollisionShape3D',par+'/'+n+'Body','shape = '+shape)
 # A narrow spur curves around the tower supports to the lower stair opening.
 for i,(a,b) in enumerate(zip(APPROACH,APPROACH[1:])):
  dx,dz=b[0]-a[0],b[1]-a[1]
  detail('TowerApproach'+str(i),((a[0]+b[0])/2,.055,(a[1]+b[1])/2),(2.2,.08,math.hypot(dx,dz)),'path',(0,math.degrees(math.atan2(dx,dz)),0))
 # Gateways straddle the existing two paths, framing both departures.
 for gate,(x,z,angle) in enumerate(GATES):
  node('Gateway'+str(gate),'Node3D',par,f'position = {vec((x,0,z))}\nrotation_degrees = Vector3(0,{angle},0)')
  path=par+'/Gateway'+str(gate)
  for side in [-1,1]:
   box('Post'+str(side),(side*3.6,2.2,0),(0.55,4.4,0.6),'arrivalwood',parent=path)
   box('Foot'+str(side),(side*3.6,0.3,0),(0.85,0.6,0.9),'arrivalstone',parent=path)
  box('Lintel',(0,4.2,0),(8.5,0.5,0.75),'arrivalwood',parent=path)
  box('GreenTop',(0,4.49,0),(8.7,0.12,0.9),'arrivalgreen',solid=False,parent=path)
  ref=g['resource']('res://Scenes/FunctionalObjects/RockHangout.tscn','PackedScene')
  node('LintelLanding',None,path,'position = Vector3(0,4.56,0)\nscale = Vector3(7.8,1,0.65)',ref)
  for side in [-1,1]:
   box('LanternFrame'+str(side),(side*2.8,3.4,.12),(.45,.6,.42),'frame',solid=False,parent=path)
   box('LanternGlass'+str(side),(side*2.8,3.4,.35),(.31,.4,.04),'emblemwhite',solid=False,parent=path)
 # A pond garden in front of the building, keeping its open doors clear.
 disk=sub('CylinderMesh','top_radius = 1\nbottom_radius = 1\nheight = 1\nradial_segments = 28')
 for n,p,s,m in [('PondBank',(-57,0.035,96),(7.5,0.06,4.8),'arrivalstone'),('ArrivalPond',(-57,0.09,96),(6.7,0.06,4),'arrivalwater')]:
  node(n,'MeshInstance3D',par,f'position = {vec(p)}\nscale = {vec(s)}\nmesh = {disk}\nmaterial_override = {g["mats"][m]}')
 for j in range(22):
  t=j*2*math.pi/22;x=-57+7.1*math.cos(t);z=96+4.45*math.sin(t)
  solid('PondStone'+str(j),(x,0.22,z),(1.05,0.44,0.7),'arrivalstone')
  if j%4==0:flat(g,'PondStoneLanding'+str(j),(x,.45,z),.85,.5)
  if j%2==0:prefab('ArrivalReed'+str(j),'Decorations/CatTail3DA',(x,0,z),(0.8,0.9,0.8))
 for j in range(4):
  node('Lily'+str(j),'MeshInstance3D',par,f'position = {vec((-59+j*1.4,0.131,96+math.sin(j)))}\nscale = Vector3(0.45,0.025,0.35)\nmesh = {disk}\nmaterial_override = {g["mats"]["arrivalgreen"]}')
 from tree_landing_spots import add as tree_landing
 for i,(x,z) in enumerate([(-97,92),(-31,83),(-47,101)]):
  prefab('ArrivalCherry'+str(i),'FunctionalObjects/CherryBlossomTreeAFunctional',(x,0,z),(1.2,1.2,1.2))
  tree_landing(g,'ArrivalCherry'+str(i),x,z,1.2,cherry=True)
 # Low post-and-rail fence follows the pond's front arc.
 for j in range(12):
  a=j*math.pi/11;b=(j+1)*math.pi/11
  x,z=-57+8*math.cos(a),96+5.2*math.sin(a)
  solid('PondFencePost'+str(j),(x,.5,z),(.14,1,.14))
  if j%3==0:flat(g,'PondPostLanding'+str(j),(x,1.01,z),.10,.10)
  if j<11:beam('PondFenceRail'+str(j),(x,.76,z),(-57+8*math.cos(b),.76,96+5.2*math.sin(b)),.075,'arrivaldark',collision=True)
 # Tower structural posts outside the walkable helix; crossed braces on its outer faces.
 cx,cz=TOWER
 for i,(dx,dz) in enumerate([(-3.4,-3.4),(-3.4,3.4),(3.4,-3.4),(3.4,3.4)]):
  solid('TowerPost'+str(i),(cx+dx,HEIGHT/2,cz+dz),(0.45,HEIGHT,0.45))
  solid('TowerFoundation'+str(i),(cx+dx,0.35,cz+dz),(0.9,0.7,0.9),'arrivalstone')
 for side in [-1,1]:
  for j in range(3):
   y=j*5+.4
   beam(f'TowerBrace{side}_{j}A',(cx-3.4,y,cz+side*3.4),(cx+3.4,y+4.3,cz+side*3.4),0.25,'arrivaldark')
   beam(f'TowerBrace{side}_{j}B',(cx+3.4,y,cz+side*3.4),(cx-3.4,y+4.3,cz+side*3.4),0.25,'arrivaldark')
 solid('TowerCore',(cx,7.5,cz),(0.65,15,0.65))
 # Visible treads sit above one connected ramp surface; no internal collision faces.
 ramp_faces=[]
 for i in range(STEPS):
  a=i*TURNS*2*math.pi/STEPS;b=(i+1)*TURNS*2*math.pi/STEPS;y=(i+1)*HEIGHT/STEPS
  points=[(r*math.cos(t),r*math.sin(t)) for r,t in [(1.15,a),(3.4 if i==STEPS-1 else 3.05,a),(3.4 if i==STEPS-1 else 3.05,b),(1.15,b)]]
  polygon=', '.join(str(round(v,6)) for p in points for v in p)
  node('SpiralTread'+str(i),'CSGPolygon3D',par,f'position = {vec((cx,y-.18,cz))}\nrotation_degrees = Vector3(90,0,0)\npolygon = PackedVector2Array({polygon})\ndepth = 0.18\nmaterial = {g["mats"]["arrivalwood"]}')
  for radius in [1.1,3.1]:
   if radius>3 and (i<2 or i>=STEPS-2):continue
   for rise in [.6,1.12]:beam(f'SpiralRail{i}_{radius}_{rise}',(cx+radius*math.cos(a),y-.125+rise,cz+radius*math.sin(a)),(cx+radius*math.cos(b),y+rise,cz+radius*math.sin(b)),0.11,collision=False)
   if i%2==0:solid(f'SpiralPost{i}_{radius}',(cx+radius*math.cos(a),y+.5,cz+radius*math.sin(a)),(0.12,1.2,0.12),solid=False)
 # Fine angular sampling produces a smooth helicoid beneath the broad visible treads.
 for i in range(STEPS*10):
  a=i*TURNS*2*math.pi/(STEPS*10);b=(i+1)*TURNS*2*math.pi/(STEPS*10)
  if i==0:a-=.001
  if i==STEPS*10-1:b+=.001
  outer=3.4 if i>=STEPS*10-10 else 3.05
  corners=[(r*math.cos(t),h,r*math.sin(t)) for r,t,h in [(1.15,a,HEIGHT*i/(STEPS*10)),(outer,a,HEIGHT*i/(STEPS*10)),(outer,b,HEIGHT*(i+1)/(STEPS*10)),(1.15,b,HEIGHT*(i+1)/(STEPS*10))]]
  for j in [0,1,2,0,2,3]:ramp_faces.extend(corners[j])
 shape=sub('ConcavePolygonShape3D','data = PackedVector3Array('+', '.join(map(str,ramp_faces))+')\nbackface_collision = true')
 node('SpiralRamp','StaticBody3D',par,f'position = {vec((cx,0,cz))}\ncollision_layer = 11\ncollision_mask = 0')
 node('Shape','CollisionShape3D',par+'/SpiralRamp','shape = '+shape)
 # One connected triangle surface per guard has no internal segment end faces to catch a player.
 for inner,outer,label,start,end in [(1.04,1.15,'Inner',0,STEPS*10),(3.05,3.16,'Outer',20,STEPS*10-20)]:
  faces=[]
  def quad(a,b,c,d):
   for p in [a,b,c,a,c,d]:faces.extend(p)
  for i in range(start,end):
   a=i*TURNS*2*math.pi/(STEPS*10);b=(i+1)*TURNS*2*math.pi/(STEPS*10)
   vertices=[]
   for rise in [-.25,1.35]:
    for r,t,h in [(inner,a,i),(outer,a,i),(outer,b,i+1),(inner,b,i+1)]:
     vertices.append((r*math.cos(t),HEIGHT*h/(STEPS*10)+rise,r*math.sin(t)))
   for j,k in [(0,1),(1,2),(2,3),(3,0)]:
    # Radial start/end caps exist only at the actual ends of the entire guard.
    if (j==0 and i!=start) or (j==2 and i!=end-1):continue
    quad(vertices[j],vertices[k],vertices[k+4],vertices[j+4])
   quad(*vertices[:4]);quad(*vertices[4:])
  shape=sub('ConcavePolygonShape3D','data = PackedVector3Array('+', '.join(map(str,faces))+')\nbackface_collision = true')
  node('SpiralGuard'+label,'StaticBody3D',par,f'position = {vec((cx,0,cz))}\ncollision_layer = 11\ncollision_mask = 0')
  node('Shape','CollisionShape3D',par+'/SpiralGuard'+label,'shape = '+shape)
 # Octagonal deck with a central opening for the spiral's final turn.
 for j in range(8):
  a=j*math.pi/4;b=(j+1)*math.pi/4
  polygon=', '.join(str(v) for r,t in [(3.2,a),(4.95,a),(4.95,b),(3.2,b)] for v in [r*math.cos(t),r*math.sin(t)])
  node('TowerDeck'+str(j),'CSGPolygon3D',par,f'position = {vec((cx,14.76,cz))}\nrotation_degrees = Vector3(90,0,0)\npolygon = PackedVector2Array({polygon})\ndepth = 0.24\nmaterial = {g["mats"]["arrivalwood"]}\nuse_collision = true\ncollision_layer = 11\ncollision_mask = 0')
  for rise in [.55,1.1]:beam(f'DeckRail{j}_{rise}',(cx+4.95*math.cos(a),15+rise,cz+4.95*math.sin(a)),(cx+4.95*math.cos(b),15+rise,cz+4.95*math.sin(b)),0.16,collision=True)
  solid('DeckPost'+str(j),(cx+4.95*math.cos(a),15.6,cz+4.95*math.sin(a)),(0.2,1.3,0.2))
 # Inner deck railing leaves a clear opening for the final tread.
 for j in range(1,31):
  a=j*math.pi/16;b=(j+1)*math.pi/16
  for rise in [.6,1.12]:beam(f'DeckInnerRail{j}_{rise}',(cx+3.2*math.cos(a),15+rise,cz+3.2*math.sin(a)),(cx+3.2*math.cos(b),15+rise,cz+3.2*math.sin(b)),.12,collision=True)
 from frontage_landscape import build as plant_frontage
 planting=plant_frontage(g)
 return dict(tower=TOWER,height_m=HEIGHT,spiral_turns=TURNS,steps=STEPS,planting=planting)
