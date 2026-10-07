"""Low fountain clearing with native, physically supported bird landing areas."""
import math,random
CENTER=(-74,-18)
ROUTE=[(-87,-29),(-84,-25),(-82,-20),(-81,-16),(-84,-13),(-90,-13),(-99,-17)]
def distance(p,a,b):
 dx,dz=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dz)/(dx*dx+dz*dz)))
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dz)
def grade_mask(p):
 d=math.hypot((p[0]+75)/11,(p[1]+20)/8)
 path=min(distance(p,a,b) for a,b in zip(ROUTE,ROUTE[1:]))
 return min(max(0,min(1,(d-1)/.3)),max(0,min(1,(path-1.3)/1.4)))
def contains(p,margin=0):
 return ((p[0]+75)/(11+margin))**2+((p[1]+20)/(8+margin))**2<1


def build(g):
 from park_perches import flat
 from bench_landing_spots import add as bench_landing
 node,sub,vec,box,prefab=[g[k] for k in ['node','sub','vec','box','prefab']]
 parent='CliffFountainGarden';node(parent,'Node3D','.')
 cylinder=fountain(g,parent,CENTER)
 # A narrow curved path joins the existing forest approach, without a plaza.
 route=ROUTE
 for i,(a,b) in enumerate(zip(route,route[1:])):
  length=math.dist(a,b);angle=math.degrees(math.atan2(b[0]-a[0],b[1]-a[1]))
  node('Path'+str(i),'MeshInstance3D',parent,f'position = {vec(((a[0]+b[0])/2,.025,(a[1]+b[1])/2))}\nrotation_degrees = Vector3(0,{angle},0)\nmesh = '+sub('BoxMesh',f'size = Vector3(1.7,0.035,{length+.65})')+f'\nmaterial_override = {g["mats"]["path"]}')
 # Bench faces the fountain; every seat slat and its backrest have flat hangouts.
 bx,bz=-80,-24
 for j in range(4):box('Seat'+str(j),(bx,.60,bz-.4+j*.26),(3.4,.14,.22),'plank',parent=parent)
 for j in range(3):box('Back'+str(j),(bx,.96+j*.24,bz-.66),(3.4,.18,.14),'plank',parent=parent)
 for side in (-1,1):
  box('BenchLeg'+str(side),(bx+side*1.15,.29,bz),(.17,.58,.85),'iron',parent=parent)
  box('BenchSupport'+str(side),(bx+side*1.15,.9,bz-.72),(.14,1.3,.14),'iron',parent=parent)
 bench_landing(g,'FountainBench',[(bx,.67,bz-.4+j*.26,3.4,.22) for j in range(4)],(bx,1.53,bz-.66,3.4,.14))
 for i,(rx,rz) in enumerate([(-69,-23),(-85,-18)]):
  cylinder('GardenRock'+str(i),(rx,.30,rz),.85,.60,'rock',sides=7,solid=True)
  flat(g,'FountainRockLanding'+str(i),(rx,.615,rz),.8,.8)
 box('BirdPost',(-83,1.1,-18),(.20,2.2,.20),'arrivalwood',parent=parent)
 box('BirdPostTop',(-83,2.24,-18),(1.1,.12,.26),'arrivalwood',parent=parent)
 flat(g,'FountainPostLanding',(-83,2.31,-18),.85,.19)
 # Existing raster plants, laid out in asymmetric edge islands. Keep path,
 # fountain, furniture, trunks and cliff-shelf footprints clear.
 from map_layout import layout
 from forest_garden import planting
 trunks=[p for p,_,_ in layout()['trees']]+[(tx,tz) for tx,tz,_ in planting()[0]]
 from forest_gate_scene import distance
 rng=random.Random(10519);grass=[];flowers=[]
 for cx,cz,rx,rz in [(-69,-17,2.1,2.6),(-70,-25,2.8,1.7),(-87,-20,2.5,3),(-78,-14,3,1.1)]:
  for ix in range(-6,7):
   for iz in range(-6,7):
    px=cx+ix*.5;pz=cz+iz*.5
    if ((px-cx)/rx)**2+((pz-cz)/rz)**2>1 or not contains((px,pz),-1.5):continue
    if math.dist((px,pz),CENTER)<3.3 or min(distance((px,pz),a,b) for a,b in zip(route,route[1:]))<1.3:continue
    if any(math.dist((px,pz),p)<1.3 for p in trunks):continue
    if any(math.dist((px,pz),p)<1.1 for p in [(-69,-23),(-85,-18),(-83,-18)]):continue
    if abs(px-bx)<2 and abs(pz-bz)<1.2:continue
    target=flowers if rng.random()<.3 else grass
    target.append((px,pz,rng.uniform(.8,1.2) if target is grass else .55,rng.uniform(0,math.pi)))
 quad=sub('QuadMesh','size = Vector2(1,1)')
 for name,asset,points in [('Grass','tall-grass',grass),('Flowers','wildflowers',flowers)]:
  tex=g['resource']('res://EXTERNAL/Touma/SafariZone/Frontage/'+asset+'.png','Texture2D')
  material=sub('StandardMaterial3D',f'transparency = 2\nalpha_scissor_threshold = 0.85\ncull_mode = 2\nalbedo_texture = {tex}\nroughness = 1.0')
  buffer=[]
  for px,pz,h,a in points:
   for turn in (0,math.pi/2):
    c,s=math.cos(a+turn),math.sin(a+turn);buffer.extend([c*.85,0,s,px,0,h,0,h/2+.025,-s*.85,0,c,pz])
  mm=sub('MultiMesh',f'transform_format = 1\ninstance_count = {len(points)*2}\nmesh = {quad}\nbuffer = PackedFloat32Array('+', '.join(str(round(v,5)) for v in buffer)+')')
  node(name,'MultiMeshInstance3D',parent,f'multimesh = {mm}\nmaterial_override = {material}')
 for i,(px,pz) in enumerate([(-74,-23),(-78,-21),(-72,-14)]):
  prefab('FountainForaging'+str(i),'FunctionalObjects/HopGroundHangout',(px,.06,pz),(.9,1,.9))
 return {'center':CENTER,'rim_perches':8,'upper_bowl_perches':4,'bench_perches':5,'rock_perches':2,'post_perches':1,'ground_pockets':3,'grass_cards':len(grass)*2,'flower_cards':len(flowers)*2}

def fountain(g,parent,center,landing_prefix=""):
 from park_perches import flat
 node,sub,vec,box=[g[k] for k in ["node","sub","vec","box"]]
 x,z=center
 g['mats']['fountainstone']=g['mat']('#bbc6bd')
 g['mats']['fountainwater']=g['mat']('#77c9ce')
 def cylinder(name,pos,radius,height,material,sides=8,solid=False):
  mesh=sub('CylinderMesh',f'top_radius = {radius}\nbottom_radius = {radius}\nheight = {height}\nradial_segments = {sides}')
  node(name,'MeshInstance3D',parent,f'position = {vec(pos)}\nmesh = {mesh}\nmaterial_override = {g["mats"][material]}')
  if solid:
   # Same regular polygon as the mesh, so collisions match its visible faces.
   vertices=[]
   for y in (-height/2,height/2):
    for k in range(sides):vertices.extend([radius*math.sin(k*2*math.pi/sides),y,radius*math.cos(k*2*math.pi/sides)])
   shape=sub('ConvexPolygonShape3D','points = PackedVector3Array('+', '.join(map(str,vertices))+')')
   node(name+'Body','StaticBody3D',parent,f'position = {vec(pos)}\ncollision_layer = 11\ncollision_mask = 0')
   node('Shape','CollisionShape3D',parent+'/'+name+'Body','shape = '+shape)
 cylinder('BasinBase',(x,.09,z),2.5,.18,'fountainstone',solid=True)
 # Eight continuous rim segments have the same wide flat top as their perches.
 # Apothem/chord placement keeps the landing rectangles wholly within the stone.
 apothem=2.5*math.cos(math.pi/8);length=2*2.5*math.sin(math.pi/8)
 for i in range(8):
  a=(i+.5)*math.pi/4;px=x+apothem*math.sin(a);pz=z+apothem*math.cos(a)
  name='BasinRim'+str(i)
  node(name,'Node3D',parent,f'position = {vec((px,.42,pz))}\nrotation_degrees = Vector3(0,{math.degrees(a)},0)')
  box('Stone',(0,0,0),(length+.12,.66,.48),'fountainstone',parent=parent+'/'+name)
  ref=g['resource']('res://Scenes/FunctionalObjects/RockHangout.tscn','PackedScene')
  node('Landing',None,parent+'/'+name,'position = Vector3(0,0.34,0)\nscale = '+vec((length-.25,1,.32)),ref)
 cylinder('WaterSurface',(x,.45,z),2.14,.025,'fountainwater')
 cylinder('Pedestal',(x,.96,z),.25,1.06,'fountainstone',solid=True)
 cylinder('UpperBowl',(x,1.53,z),.68,.18,'fountainstone',solid=True)
 cylinder('UpperWater',(x,1.627,z),.54,.018,'fountainwater')
 # Discrete supported tips allow resting around the small bowl without sitting
 # in the central spout. The large basin remains the principal bird bath rim.
 for i in range(4):
  a=i*math.pi/2;flat(g,landing_prefix+'UpperBowlLanding'+str(i),(x+.565*math.sin(a),1.635,z+.565*math.cos(a)),.12,.12)
 cylinder('WaterSpout',(x,1.79,z),.035,.32,'fountainwater',sides=6)
 for i,(dx,dy,dz) in enumerate([(.06,1.99,0),(-.10,1.93,.03),(.13,1.78,.04)]):
  sphere=sub('SphereMesh','radius = 0.035\nheight = 0.07\nradial_segments = 6\nrings = 3')
  node('Droplet'+str(i),'MeshInstance3D',parent,f'position = {vec((x+dx,dy,z+dz))}\nmesh = {sphere}\nmaterial_override = {g["mats"]["fountainwater"]}')
 dropmesh=sub('SphereMesh','radius = 0.025\nheight = 0.05\nradial_segments = 6\nrings = 3')
 node('FlowingWater','CPUParticles3D',parent,f'position = {vec((x,1.65,z))}\namount = 24\nlifetime = 0.7\nmesh = {dropmesh}\nmaterial_override = {g["mats"]["fountainwater"]}\ndirection = Vector3(0,1,0)\nspread = 12.0\ngravity = Vector3(0,-8,0)\ninitial_velocity_min = 2.2\ninitial_velocity_max = 2.6\nscale_amount_min = 0.8\nscale_amount_max = 1.2')

 return cylinder
