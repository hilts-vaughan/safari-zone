"""Water plaza on the gate-facing side of the existing waterfall bluff."""
import math

def contains(p,margin=0):
 return 49-margin<p[0]<79+margin and 34-margin<p[1]<56+margin

def build(g,cylinder,disc):
 from fountain_garden import fountain
 from bench_landing_spots import add as bench_landing
 from park_perches import flat
 node,sub,vec,box,prefab=[g[k] for k in ['node','sub','vec','box','prefab']]
 parent='WetlandsWaterGarden'
 node('PlazaFountain','Node3D',parent)
 fountain(g,parent+'/PlazaFountain',(62,44),'Plaza')
 for i,(x,z) in enumerate([(55,45),(70,45)]):
  for j in range(4):box(f'PlazaBench{i}Seat{j}',(x,.6,z-.4+j*.26),(3,.14,.22),'plank',parent=parent)
  for j in range(3):box(f'PlazaBench{i}Back{j}',(x,.95+j*.24,z-.66),(3,.18,.14),'plank',parent=parent)
  for s in [-1,1]:
   box(f'PlazaBench{i}Leg{s}',(x+s,.29,z),(.17,.58,.85),'iron',parent=parent)
   box(f'PlazaBench{i}Support{s}',(x+s,.9,z-.72),(.14,1.3,.14),'iron',parent=parent)
  bench_landing(g,f'PlazaBench{i}',[(x,.67,z-.4+j*.26,3,.22) for j in range(4)],(x,1.52,z-.66,3,.14))
 # North cascade covers the formerly blank back wall. The original south-side
 # grotto remains open; the east footpath connects to its existing entrance.
 water=sub('StandardMaterial3D','transparency = 1\ncull_mode = 2\nalbedo_color = Color(0.43,0.78,0.80,0.72)\nroughness = 0.7')
 mesh=sub('QuadMesh','size = Vector2(3.8,7.5)')
 node('PlazaCascade','MeshInstance3D',parent,f'position = Vector3(62,4.2,55.94)\nmesh = {mesh}\nmaterial_override = {water}')
 cylinder('NorthStream',(62,8.035,58),1.9,.035,'water',sides=16)
 disc('PlazaCascadeBank',(62,.10,53),5.7,2.7,'shore')
 disc('PlazaCascadePool',(62,.15,53),5,2.1,'water')
 streak=sub('BoxMesh','size = Vector3(0.09,0.8,0.045)')
 node('PlazaFallingWater','CPUParticles3D',parent,f'position = Vector3(62,7.85,55.9)\namount = 64\nlifetime = 1.1\nmesh = {streak}\nmaterial_override = {g["mats"]["wetlandfoam"]}\nemission_shape = 3\nemission_box_extents = Vector3(1.7,0.04,0.03)\ndirection = Vector3(0,-1,0)\nspread = 2\ngravity = Vector3(0,-9,0)\ninitial_velocity_min = 4\ninitial_velocity_max = 5')
 for i in range(9):
  cylinder('PlazaFoam'+str(i),(60.4+i*.4,.19,55),.25,.045,'wetlandfoam',sides=8)
 # Staggered tapered shoulders and grass shelves break up the straight facade.
 for i,(x,z,r,h) in enumerate([(53,55,2.0,4.4),(71,55,2.1,5.1),(55,56,2.0,6.0),(69,56,2.0,6.8)]):
  mesh=sub('CylinderMesh',f'top_radius = {r*.7}\nbottom_radius = {r}\nheight = {h}\nradial_segments = 7')
  node('PlazaStoneShelf'+str(i),'MeshInstance3D',parent,f'position = {vec((x,h/2,z))}\nmesh = {mesh}\nmaterial_override = {g["mats"]["waterfallrock"]}')
  vertices=[]
  for yy,rr in [(-h/2,r),(h/2,r*.7)]:
   for k in range(7):vertices.extend([rr*math.sin(k*math.tau/7),yy,rr*math.cos(k*math.tau/7)])
  shape=sub('ConvexPolygonShape3D','points = PackedVector3Array('+', '.join(map(str,vertices))+')')
  node('PlazaShelfBody'+str(i),'StaticBody3D',parent,f'position = {vec((x,h/2,z))}\ncollision_layer = 11\ncollision_mask = 0')
  node('Shape','CollisionShape3D',parent+'/PlazaShelfBody'+str(i),'shape = '+shape)
  cylinder('PlazaShelfTurf'+str(i),(x,h+.02,z),r*.69,.06,'waterfallgrass',sides=7)
 sphere=sub('SphereMesh','radius = 1\nheight = 2\nradial_segments = 9\nrings = 4')
 for i,(x,y,z,r) in enumerate([(54,4.65,55,.8),(70,5.35,55,.8),(55,6.25,56,.65),(69,7.05,56,.7),(57,8.3,58,.8),(66,8.3,58,.7),(53,0.5,43,.8),(55,0.5,48,.75),(69,0.5,48,.8),(74,0.5,43,.8)]):
  node('PlazaBush'+str(i),'MeshInstance3D',parent,f'position = {vec((x,y,z))}\nscale = {vec((r,.38,r))}\nmesh = {sphere}\nmaterial_override = {g["mats"]["leaf"]}')
 for i,(x,z) in enumerate([(53,42),(54,48),(70,48),(75,43),(57,51),(68,51)]):
  prefab('PlazaFlowers'+str(i),'Decorations/Flowers',(x,.11,z),(.3,.3,.3))
  for j in range(7):
   a=j*2.4;h=.5+.12*(j%3)
   mesh=sub('CylinderMesh',f'top_radius = 0.006\nbottom_radius = 0.035\nheight = {h}\nradial_segments = 5')
   node(f'PlazaReed{i}_{j}','MeshInstance3D',parent,f'position = {vec((x+.65+.3*math.cos(a),.10+h/2,z+.3*math.sin(a)))}\nrotation_degrees = Vector3(8,0,6)\nmesh = {mesh}\nmaterial_override = {g["mats"]["leaf"]}')
 # Crossed raster flower cards form readable low beds in the native style.
 tex=g['resource']('res://EXTERNAL/Touma/SafariZone/Frontage/wildflowers.png','Texture2D')
 material=sub('StandardMaterial3D',f'transparency = 2\nalpha_scissor_threshold = 0.85\ncull_mode = 2\nalbedo_texture = {tex}\nroughness = 1')
 quad=sub('QuadMesh','size = Vector2(1,1)')
 for i,(cx,cz) in enumerate([(53,42),(54,48),(70,48),(75,43),(57,51),(68,51)]):
  for j in range(15):
   a=j*2.4;r=.3+.3*(j%4);x=cx+r*math.cos(a);z=cz+r*.6*math.sin(a)
   for turn in [0,90]:
    node(f'PlazaFlowerCard{i}_{j}_{turn}','MeshInstance3D',parent,f'position = {vec((x,.37,z))}\nscale = Vector3(1,0.55,1)\nrotation_degrees = Vector3(0,{turn},0)\nmesh = {quad}\nmaterial_override = {material}')
 box('PlazaPerchPost',(75,1.2,48),(.18,2.4,.18),'arrivalwood',parent=parent)
 box('PlazaPerchTop',(75,2.45,48),(1.1,.1,.32),'plank',parent=parent)
 flat(g,'PlazaPerchLanding',(75,2.51,48),.95,.24)
 return {'fountain':(62,44),'benches':2,'cascade_pool':(62,53),'grotto_access':'east side via (75,56) to (73,63)'}
