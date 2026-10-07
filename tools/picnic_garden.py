"""Forest-edge picnic grove, using existing assets and native supported hangouts."""
import math, random
from fountain_garden import distance
TABLES=[(-62,-28),(-52,-25),(-42,-26),(-62,-19),(-52,-19),(-36,-20)]
BENCHES=[(-57,-14.5),(-43,-15.5)]
TREES=[(-59,-14,1.4),(-40,-17,1.35)]
ROUTE=[(-68,-31),(-65,-28),(-65,-23),(-64,-16),(-56,-16),(-48,-17),(-34,-17)]
def contains(p,margin=0):
 x,z=p
 # Reserve the empty lawn; retain the surrounding authored woodland.
 return -66-margin<x<-32+margin and -33-margin<z<-12+margin 
def grade_mask(p):
 if contains(p):return 0.0
 # Smooth apron without changing the authored woodland terrain.
 from woodland_section import contains as woodland
 if woodland(p):return 1.0
 return 0.0 if min(distance(p,a,b) for a,b in zip(ROUTE,ROUTE[1:]))<1.5 else 1.0

def build(g):
 from park_perches import flat
 from bench_landing_spots import add as bench_landing
 node,sub,vec,box,prefab=[g[k] for k in ['node','sub','vec','box','prefab']]
 parent='ForestPicnicGrove';node(parent,'Node3D','.')
 perches=0
 for i,(x,z) in enumerate(TABLES):perches+=table(g,parent,i,x,z)
 for i,(x,z) in enumerate(BENCHES):
  for j in range(4):box(f'PicnicBench{i}Seat{j}',(x,.60,z-.4+j*.26),(3.4,.14,.22),'plank',parent=parent)
  for j in range(3):box(f'PicnicBench{i}Back{j}',(x,.96+j*.24,z+.65),(3.4,.18,.14),'plank',parent=parent)
  for side in (-1,1):
   box(f'PicnicBench{i}Leg{side}',(x+side*1.15,.29,z),(.17,.58,.85),'iron',parent=parent)
   box(f'PicnicBench{i}Support{side}',(x+side*1.15,.9,z+.72),(.14,1.3,.14),'iron',parent=parent)
  bench_landing(g,f'PicnicBench{i}',[(x,.67,z-.4+j*.26,3.4,.22) for j in range(4)],(x,1.53,z+.65,3.4,.14));perches+=5
 for i,(x,z,s) in enumerate(TREES):
  prefab(f'PicnicTree{i}','FunctionalObjects/TreeCFunctional',(x,0,z),(s,s,s))
  # Solid branch tips make their landing geometry verifiable.
  for side in (-1,1):
   y=(2.2 if side==1 else 2.7)*s
   box(f'PicnicBranch{i}_{side}',(x+side*.85*s,y-.055,z),(1.3*s,.11,.28),'arrivaldark',parent=parent)
   flat(g,f'PicnicBranchLanding{i}_{side}',(x+side*1.05*s,y+.01,z),.65*s,.20);perches+=1
 for i,(x,z) in enumerate([(-64,-24),(-48,-15),(-34,-22)]):
  # Flat-topped native-style faceted stones with identical visible/collision mesh.
  radius=.85;height=.65;sides=7
  mesh=sub('CylinderMesh',f'top_radius = {radius}\nbottom_radius = {radius}\nheight = {height}\nradial_segments = {sides}')
  node(f'Rock{i}','MeshInstance3D',parent,f'position = {vec((x,height/2,z))}\nmesh = {mesh}\nmaterial_override = {g["mats"]["rock"]}')
  vertices=[]
  for y in (-height/2,height/2):
   for k in range(sides):vertices.extend([radius*math.sin(k*2*math.pi/sides),y,radius*math.cos(k*2*math.pi/sides)])
  shape=sub('ConvexPolygonShape3D','points = PackedVector3Array('+', '.join(map(str,vertices))+')')
  node(f'RockBody{i}','StaticBody3D',parent,f'position = {vec((x,height/2,z))}\ncollision_layer = 11\ncollision_mask = 0')
  node('Shape','CollisionShape3D',parent+f'/RockBody{i}','shape = '+shape)
  flat(g,f'PicnicRockLanding{i}',(x,height+.01,z),.8,.8);perches+=1
 for i,(x,z) in enumerate([(-58,-22),(-33,-17)]):
  box(f'BirdPost{i}',(x,1.1,z),(.18,2.2,.18),'arrivalwood',parent=parent)
  box(f'BirdRail{i}',(x,2.24,z),(1.1,.12,.26),'arrivalwood',parent=parent)
  flat(g,f'PicnicPostLanding{i}',(x,2.31,z),.85,.19);perches+=1
 # Narrow continuous fork, plus short table access spurs.
 links=list(zip(ROUTE,ROUTE[1:]))+[((-65,-28),(-62,-28)),((-65,-23),(-52,-23)),((-52,-23),(-42,-24)),((-42,-24),(-36,-20)),((-64,-16),(-62,-19)),((-56,-16),(-52,-19)),((-48,-17),(-42,-24)),((-34,-17),(-36,-20))]
 for i,(a,b) in enumerate(links):
  length=math.dist(a,b);angle=math.degrees(math.atan2(b[0]-a[0],b[1]-a[1]))
  node(f'Path{i}','MeshInstance3D',parent,f'position = {vec(((a[0]+b[0])/2,.025,(a[1]+b[1])/2))}\nrotation_degrees = Vector3(0,{angle},0)\nmesh = '+sub('BoxMesh',f'size = Vector3(1.4,0.035,{length+.6})')+f'\nmaterial_override = {g["mats"]["path"]}')
 rng=random.Random(1052026);grass=[];flowers=[]
 for ix in range(65):
  for iz in range(39):
   x=-65+ix*.5;z=-32+iz*.5;p=(x,z)
   if not contains(p) or z>-13:continue
   if min(distance(p,a,b) for a,b in links)<1.0:continue
   if any(abs(x-tx)<1.95 and abs(z-tz)<1.7 for tx,tz in TABLES):continue
   if any(abs(x-tx)<2 and abs(z-tz)<1.1 for tx,tz in BENCHES):continue
   if any(math.dist(p,(tx,tz))<1.2 for tx,tz,_ in TREES):continue
   if any(math.dist(p,q)<1.1 for q in [(-64,-24),(-48,-15),(-34,-22),(-58,-22),(-33,-17)]):continue
   if rng.random()<.17:continue
   target=flowers if rng.random()<.35 else grass
   target.append((x,z,rng.uniform(.85,1.25) if target is grass else rng.uniform(.5,.75),rng.uniform(0,math.pi)))
 quad=sub('QuadMesh','size = Vector2(1,1)')
 for name,asset,points in [('Grass','tall-grass',grass),('Flowers','wildflowers',flowers)]:
  tex=g['resource']('res://EXTERNAL/Touma/SafariZone/Frontage/'+asset+'.png','Texture2D')
  material=sub('StandardMaterial3D',f'transparency = 2\nalpha_scissor_threshold = 0.85\ncull_mode = 2\nalbedo_texture = {tex}\nroughness = 1.0')
  buffer=[]
  for x,z,h,a in points:
   for turn in (0,math.pi/2):
    c,s=math.cos(a+turn),math.sin(a+turn);buffer.extend([c*.85,0,s,x,0,h,0,h/2+.025,-s*.85,0,c,z])
  mm=sub('MultiMesh',f'transform_format = 1\ninstance_count = {len(points)*2}\nmesh = {quad}\nbuffer = PackedFloat32Array('+', '.join(str(round(v,5)) for v in buffer)+')')
  node(name,'MultiMeshInstance3D',parent,f'multimesh = {mm}\nmaterial_override = {material}')
 for i,(x,z) in enumerate([(-60,-23),(-50,-17),(-39,-18)]):prefab(f'PicnicForaging{i}','FunctionalObjects/HopGroundHangout',(x,.06,z),(.8,1,.8))
 return {'tables':6,'benches':2,'trees':2,'rocks':3,'posts':2,'landing_rectangles':perches,'foraging_pockets':3,'grass_cards':len(grass)*2,'flower_cards':len(flowers)*2}

def table(g,parent,i,x,z):
 from park_perches import flat
 box=g["box"]
 # Continuous collider tops with slatted visuals. The gaps cannot snag players.
 for j in range(5):box(f'Table{i}Slat{j}',(x,1.0,z-.52+j*.26),(3.0,.14,.245),'plank',solid=False,parent=parent)
 box(f'Table{i}TopSupport',(x,1.0,z),(2.98,.14,1.28),'arrivalwood',parent=parent)
 flat(g,f'PicnicTableLanding{i}',(x,1.08,z),2.75,1.05)
 for side in (-1,1):
  box(f'Table{i}Seat{side}',(x,.53,z+side*1.0),(3.25,.14,.40),'plank',parent=parent)
  flat(g,f'PicnicSeatLanding{i}_{side}',(x,.61,z+side*1.0),3.0,.33)
 for side in (-1,1):
  box(f'Table{i}Leg{side}',(x+side*.95,.44,z),(.18,.88,1.08),'arrivalwood',parent=parent)
  box(f'Table{i}SeatSupport{side}',(x+side*.95,.36,z),(.18,.14,2.4),'arrivalwood',parent=parent)
 return 3
