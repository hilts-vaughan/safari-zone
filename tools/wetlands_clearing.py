"""Wetlands Rest water garden and solid bluff with a dry walk-behind grotto."""
import math

def contains(p, margin=0):
 from wetlands_plaza import contains as plaza
 return plaza(p,margin) or (20-margin < p[0] < 73+margin and 54-margin < p[1] < 82+margin)

def grade_mask(p):
 # Feather the old hill away outside the authored clearing.
 x,z=p;d=min(max(20-x,x-73,54-z,z-82,0),max(49-x,x-79,34-z,z-56,0))
 return min(1,d/4)

def build(g):
 from fountain_garden import fountain
 from park_perches import flat
 from bench_landing_spots import add as bench_landing
 node,sub,vec,box,prefab=[g[k] for k in ['node','sub','vec','box','prefab']]
 parent='WetlandsWaterGarden';node(parent,'Node3D','.')
 for key,color in [('waterfallrock','#87978a'),('waterfallshade','#66786e'),('grottoshade','#51685e'),('waterfallgrass','#86b779'),('wetlandfoam','#def4e5'),('wetlandlily','#609d62')]:g['mats'][key]=g['mat'](color)
 cylinder=fountain(g,parent,(28,62),'Wetland')
 def disc(name,p,rx,rz,material):
  mesh=sub('CylinderMesh','top_radius = 1.0\nbottom_radius = 1.0\nheight = 0.04\nradial_segments = 20')
  node(name,'MeshInstance3D',parent,f'position = {vec(p)}\nscale = {vec((rx,1,rz))}\nmesh = {mesh}\nmaterial_override = {g["mats"][material]}')
 def trail(name,a,b,width=2.4):
  length=math.dist(a,b);angle=math.degrees(math.atan2(b[0]-a[0],b[1]-a[1]))
  mesh=sub('BoxMesh',f'size = Vector3({width},0.035,{length+width*.5})')
  node(name,'MeshInstance3D',parent,f'position = {vec(((a[0]+b[0])/2,.025,(a[1]+b[1])/2))}\nrotation_degrees = Vector3(0,{angle},0)\nmesh = {mesh}\nmaterial_override = {g["mats"]["path"]}')
 disc('FountainApron',(28,.024,62),4.6,4.6,'path')
 trail('FountainApproach',(38,62),(32,62))
 for i,(x,z) in enumerate([(24,67),(32,67)]):
  for j in range(4):box(f'Bench{i}Slat{j}',(x,.6,z-.4+j*.26),(3,.14,.22),'plank',parent=parent)
  for j in range(3):box(f'Bench{i}Back{j}',(x,.95+j*.24,z+.66),(3,.18,.14),'plank',parent=parent)
  for side in (-1,1):
   box(f'Bench{i}Leg{side}',(x+side*1,.29,z),(.17,.58,.85),'iron',parent=parent)
   box(f'Bench{i}Support{side}',(x+side*1,.9,z+.72),(.14,1.3,.14),'iron',parent=parent)
  bench_landing(g,f'WetlandBench{i}',[(x,.67,z-.4+j*.26,3,.22) for j in range(4)],(x,1.52,z+.66,3,.14))
 # A small ornamental pond has pads but no additional swimming spawner.
 disc('GardenPondBank',(24,.025,75),3.8,2.8,'shore')
 disc('GardenPond',(24,.11,75),3,2.1,'water')
 for i,(x,z) in enumerate([(24.5,74),(24.5,76),(25.7,75)]):
  cylinder('GardenLily'+str(i),(x,.165,z),.44,.04,'wetlandlily',sides=12,solid=True)
  flat(g,'GardenLilyLanding'+str(i),(x,.19,z),.48,.48)
 # Continuous arched deck: zero-height ends let players walk on without jumping.
 arch=[(-4+i*.5,.65*math.sin(math.pi*i/16)) for i in range(17)]
 polygon=', '.join(str(v) for p in [(-4,-.14)]+arch+[(4,-.14)] for v in p)
 node('BridgeDeck','CSGPolygon3D',parent,f'position = Vector3(23.5,0,75)\nrotation_degrees = Vector3(0,90,0)\npolygon = PackedVector2Array({polygon})\ndepth = 1.8\nmaterial = {g["mats"]["plank"]}\nuse_collision = true\ncollision_layer = 11\ncollision_mask = 0')
 # Rails follow the arch, with discrete posts and a generous clear walking lane.
 for side in (-1,1):
  x=22.6+side*.98
  for i in range(16):
   z0,y0=arch[i];z1,y1=arch[i+1];dy=y1-y0
   rail='BridgeRail'+str(side)+'_'+str(i)
   node(rail,'Node3D',parent,f'position = Vector3({x},{(y0+y1)/2+.95},{75+(z0+z1)/2})\nrotation_degrees = Vector3({-math.degrees(math.atan2(dy,z1-z0))},0,0)')
   box('Timber',(0,0,0),(.12,.12,math.hypot(.5,dy)+.025),'arrivalwood',parent=parent+'/'+rail)
  for i in [1,4,8,12,15]:
   z,y=arch[i]
   box(f'BridgePost{side}_{i}',(x,y+.46,75+z),(.14,.98,.14),'arrivalwood',parent=parent)
 trail('BridgeApproach',(23,68),(22.6,71),1.8)
 trail('BridgeExit',(22.6,79),(29,80),1.8)
 # Bluff: a back wall and roof leave a 3 m deep, 3.2 m tall passage.
 # Both side entrances remain open. Visible boxes share exact solid colliders.
 box('BluffBack',(62,4,58.5),(18,8,5),'grottoshade',parent=parent)
 profile=[(-9,3.2),(-9,6),(-7,7.8),(-3,8.7),(3,8.7),(7,8),(9,6.6),(9,3.2)]
 def rock_profile(name,points,depth,z,material,solid=False):
  polygon=', '.join(str(v) for p in points for v in p)
  node(name,'CSGPolygon3D',parent,f'position = Vector3(62,0,{z})\npolygon = PackedVector2Array({polygon})\ndepth = {depth}\nmaterial = {g["mats"][material]}\nuse_collision = {str(solid).lower()}\ncollision_layer = 11\ncollision_mask = 0')
 rock_profile('GrottoRoof',profile,4,65,'waterfallrock',True)
 # Shallow contrasting triangular faces create a faceted stone front.
 for i,(a,b) in enumerate(zip(profile,profile[1:]+profile[:1])):
  rock_profile('RockFace'+str(i),[a,b,(0,5.7)],.008,65.012,'waterfallshade' if i%3==0 else 'waterfallrock')
 cap=profile[1:7]+[(x,y-.17) for x,y in reversed(profile[1:7])]
 rock_profile('BluffTurf',cap,8.7,65.01,'waterfallgrass')
 box('DryPassage',(62,-.08,63),(18,.16,4),'rock',parent=parent)
 
 # Low-poly shoulders soften the bluff silhouette; keep entrance lanes clear.
 for i,(x,z,h,r) in enumerate([(52,58,6,3),(72,58,7,3),(56,57,8,3),(68,57,8.5,3)]):
  mesh=sub('CylinderMesh',f'top_radius = {r*.65}\nbottom_radius = {r}\nheight = {h}\nradial_segments = 7')
  node('BluffShoulder'+str(i),'MeshInstance3D',parent,f'position = {vec((x,h/2,z))}\nmesh = {mesh}\nmaterial_override = {g["mats"]["waterfallrock"]}')
  # Inscribed support stays inside the faceted stone and outside the corridor.
  box('ShoulderCore'+str(i),(x,h/2,z),(r,h,r),'waterfallrock',parent=parent)
 # Stream and curtain stand in front of the sheltered ledge, without a collider.
 box('StreamBed',(62,8.55,62),(3.8,.3,6),'waterfallrock',parent=parent)
 box('UpperStream',(62,8.725,62),(3.4,.04,6),'water',solid=False,parent=parent)
 water=sub('StandardMaterial3D','transparency = 1\ncull_mode = 2\nalbedo_color = Color(0.43,0.78,0.80,0.62)\nroughness = 0.7')
 mesh=sub('QuadMesh','size = Vector2(4.8,8.6)')
 node('WaterCurtain','MeshInstance3D',parent,f'position = Vector3(62,4.5,66.1)\nmesh = {mesh}\nmaterial_override = {water}')
 disc('WaterfallPoolBank',(62,.03,70),6.3,3.5,'shore')
 disc('WaterfallPool',(62,.115,70),5.7,2.9,'water')
 streak=sub('BoxMesh','size = Vector3(0.10,0.85,0.045)')
 node('FallingWater','CPUParticles3D',parent,f'position = Vector3(62,8.6,66.15)\namount = 80\nlifetime = 1.1\nmesh = {streak}\nmaterial_override = {g["mats"]["wetlandfoam"]}\nemission_shape = 3\nemission_box_extents = Vector3(2.25,0.04,0.03)\ndirection = Vector3(0,-1,0)\nspread = 2.0\ngravity = Vector3(0,-9,0)\ninitial_velocity_min = 4.0\ninitial_velocity_max = 5.0')
 foam=sub('SphereMesh','radius = 0.09\nheight = 0.18\nradial_segments = 6\nrings = 3')
 node('Splash','CPUParticles3D',parent,f'position = Vector3(62,0.25,66.5)\namount = 45\nlifetime = 0.65\nmesh = {foam}\nmaterial_override = {g["mats"]["wetlandfoam"]}\nemission_shape = 3\nemission_box_extents = Vector3(2.3,0.03,0.20)\ndirection = Vector3(0,1,0)\nspread = 40.0\ngravity = Vector3(0,-5,0)\ninitial_velocity_min = 1.0\ninitial_velocity_max = 2.0')
 # Native water volumes make both pools water habitat without extra spawners.
 for name,x,z,rx,rz in [('Garden',24,75,3,2.1),('Cascade',62,70,5.7,2.9)]:
  g['scriptnode'](name+'WaterArea','Area3D','Core/WaterArea',(x,-2.4,z),parent=parent)
  shape=sub('CylinderShape3D','radius = 1.0\nheight = 5.0')
  node('Shape','CollisionShape3D',parent+'/'+name+'WaterArea',f'scale = {vec((rx,1,rz))}\nshape = {shape}')
 trail('GrottoApproach',(43,66),(51,66),3)
 trail('GrottoEntrance',(51,66),(51,63),3)
 trail('GrottoExit',(73,63),(74,66),3)
 # Small solid-color reed clusters avoid the stock pale rectangular marsh cards.
 reedmesh=sub('CylinderMesh','top_radius = 0.005\nbottom_radius = 0.035\nheight = 1.0\nradial_segments = 5')
 for i,(x,z) in enumerate([(25,71.7),(27.4,74),(26.5,78),(20,74),(56,74),(67,74),(54,69),(71,69)]):
  for j in range(9):
   angle=j*2.4;h=.45+(j%4)*.13
   node(f'WaterGardenReed{i}_{j}','MeshInstance3D',parent,f'position = Vector3({x+.32*math.cos(angle)},{h/2},{z+.32*math.sin(angle)})\nscale = Vector3(1,{h},1)\nrotation_degrees = Vector3({8*math.cos(angle)},0,{8*math.sin(angle)})\nmesh = {reedmesh}\nmaterial_override = {g["mats"]["leaf"]}')
 for i,(x,z) in enumerate([(27,56),(32,57),(60,63),(64,63)]):
  y=8.72 if x>50 else .03
  prefab('WaterGardenFlowers'+str(i),'Decorations/Flowers',(x,y,z),(.06,.06,.06))
 for i,(x,z) in enumerate([(33,72),(48,69)]):
  box('FeederPost'+str(i),(x,1.1,z),(.2,2.2,.2),'arrivalwood',parent=parent)
  box('FeederTray'+str(i),(x,2.25,z),(1.3,.1,.85),'plank',parent=parent)
  flat(g,'WetlandFeederLanding'+str(i),(x,2.31,z),1.1,.65)
 from wetlands_plaza import build as build_plaza
 plaza=build_plaza(g,cylinder,disc)
 return {'plaza':plaza,'fountain':(28,62),'benches':2,'feeders':2,'pond':(24,75),'waterfall':(62,66.1),'grotto_floor_y':0,'grotto_clearance_m':3.2,'grotto_depth_m':4,'grotto_entrances':[(51,63),(73,63)],'water_curtain_has_collision':False}
