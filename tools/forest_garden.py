"""Layered forest planting around existing trails, facilities and terrain."""
import math,random
from functools import lru_cache

def contains(p):return -143<p[0]<-30 and -101<p[1]<-10

@lru_cache(maxsize=1)
def planting():
 from map_layout import layout,inside,biome,path_distance,pond_contains,FACILITIES
 from enclosure_layout import blocked
 from woodland_section import contains as in_study
 model=layout();rng=random.Random(41004)
 originals=[p for p,k,_ in model['trees'] if k=='forest']
 def dry(p,margin):
  return contains(p) and inside(p) and biome(p)=='forest' and not pond_contains(p,2) and not in_study(p,3) and not blocked(p,1) and path_distance(p)>margin and math.dist(p,FACILITIES['forest'])>8 and all(math.dist(p,q)>5 for q in [(-88,-51),(-72,-51),(-73,-36)])
 added=[]
 for x in range(-140,-30,4):
  for z in range(-98,-10,4):
   p=(x+rng.uniform(-1,1),z+rng.uniform(-1,1))
   if dry(p,2.8) and all(math.dist(p,q)>2.9 for q in originals+[(x,z) for x,z,_ in added]):added.append((*p,rng.uniform(2.0,2.5)))
 trunks=originals+[(x,z) for x,z,_ in added]
 grass=[];flowers=[]
 for ix in range(178):
  for iz in range(145):
   p=(-139+ix*.6+rng.uniform(-.15,.15),-98+iz*.6+rng.uniform(-.15,.15))
   if not dry(p,2.25) or any(math.dist(p,q)<.9 for q in trunks):continue
   # Broad alternating grass islands leave small open glades between trees.
   patch=math.sin(p[0]*.17)+math.cos(p[1]*.21)
   if patch<-.5 or rng.random()<.13:continue
   if patch<.05 or rng.random()<.11:flowers.append((*p,rng.uniform(.55,.85),rng.uniform(0,math.pi)))
   else:grass.append((*p,rng.uniform(.8,1.4),rng.uniform(0,math.pi)))
 rests=[]
 candidates=[(x,z) for x in range(-138,-32,2) for z in range(-96,-12,2)
             if dry((x,z),5.5) and all(math.dist((x,z),q)>1.8 for q in trunks)]
 for target in [(-120,-24),(-99,-27),(-105,-44),(-93,-58),(-63,-66),(-129,-62)]:
  possible=[p for p in candidates if all(math.dist(p,q)>10 for q in rests)]
  if possible:rests.append(min(possible,key=lambda p:math.dist(p,target)))
 grass=[p for p in grass if all(math.dist(p[:2],q)>3 for q in rests)]
 flowers=[p for p in flowers if all(math.dist(p[:2],q)>2.5 for q in rests)]
 return added,grass,flowers,rests

def build(g):
 from tree_landing_spots import add as tree_landing
 from park_perches import flat
 from sculpted_terrain import flat_ground
 node,sub,vec,box,prefab=[g[k] for k in ['node','sub','vec','box','prefab']]
 from picnic_garden import contains as in_picnic
 from forest_service_garden import contains as in_service
 parent='ForestGarden';node(parent,'Node3D','.')
 added,grass,flowers,rests=planting()
 from map_layout import layout
 for i,(p,key,s) in enumerate(layout()['trees']):
  if i not in (0,51,92) and flat_ground(p,1.2) and key=='forest' and contains(p) and not in_picnic(p) and not in_service(p):tree_landing(g,'ForestOriginalTree'+str(i),p[0],p[1],s*1.6,parent=parent)
 for i,(x,z,s) in enumerate(added):
  if not flat_ground((x,z),1.2) or i in (53,54) or in_picnic((x,z)) or in_service((x,z)):continue # Added cliff faces occupy these old trunk positions.
  ground=0
  prefab('ForestLayerTree'+str(i),'FunctionalObjects/TreeCFunctional',(x,ground,z),(s,s,s))
  tree_landing(g,'ForestLayerTree'+str(i),x,z,s,parent=parent,base_y=ground-.04)
 quad=sub('QuadMesh','size = Vector2(1,1)')
 def cards(name,asset,placements):
  tex=g['resource']('res://EXTERNAL/Touma/SafariZone/Frontage/'+asset+'.png','Texture2D')
  material=sub('StandardMaterial3D',f'transparency = 2\nalpha_scissor_threshold = 0.85\ncull_mode = 2\nalbedo_texture = {tex}\nroughness = 1.0')
  buffer=[]
  for x,z,h,a in placements:
   for turn in [0,math.pi/2]:
    c,s=math.cos(a+turn),math.sin(a+turn);buffer.extend([c*.85,0,s,x,0,h,0,h/2+.025,-s*.85,0,c,z])
  mm=sub('MultiMesh',f'transform_format = 1\ninstance_count = {len(placements)*2}\nmesh = {quad}\nbuffer = PackedFloat32Array('+', '.join(str(round(v,5)) for v in buffer)+')')
  node(name,'MultiMeshInstance3D',parent,f'multimesh = {mm}\nmaterial_override = {material}')
 grass=[p for p in grass if flat_ground(p[:2],.6) and not in_picnic(p[:2]) and not in_service(p[:2])]
 flowers=[p for p in flowers if flat_ground(p[:2],.6) and not in_picnic(p[:2]) and not in_service(p[:2])]
 cards('ForestTallGrass','tall-grass',grass);cards('ForestWildflowers','wildflowers',flowers)
 for i,(x,z) in enumerate(rests):
  if not flat_ground((x,z),3) or in_picnic((x,z)) or in_service((x,z)):continue
  # Feeders bring activity into the central glades with long, visible rail perches.
  box('FeederPost'+str(i),(x-1.5,1.05,z-1.5),(.18,2.1,.18),'arrivalwood',parent=parent)
  box('FeederTray'+str(i),(x-1.5,2.14,z-1.5),(1.8,.12,1.2),'plank',parent=parent)
  box('FeederRoof'+str(i),(x-1.5,2.95,z-1.5),(2.1,.15,1.5),'plank',parent=parent)
  for side in (-1,1):
   box(f'FeederUpright{i}_{side}',(x-1.5+side*.75,2.55,z-1.5),(.10,.7,.10),'arrivalwood',parent=parent)
  flat(g,'ForestFeederLanding'+str(i),(x-1.5,2.215,z-1.5),1.35,.95)
  h=.7 if i%2 else .45
  mesh=sub('CylinderMesh',f'top_radius = 0.55\nbottom_radius = 0.65\nheight = {h}\nradial_segments = 7')
  node('ForestStump'+str(i),'MeshInstance3D',parent,f'position = {vec((x,h/2,z))}\nmesh = {mesh}\nmaterial_override = {g["mats"]["arrivaldark"]}')
  box('StumpCollider'+str(i),(x,h/2,z),(.8,h,.8),'arrivaldark',parent=parent)
  flat(g,'ForestStumpLanding'+str(i),(x,h+.01,z),.65,.65)
  box('FallenLog'+str(i),(x+1.4,.28,z),(1.8,.56,.65),'arrivalwood',parent=parent)
  flat(g,'ForestLogLanding'+str(i),(x+1.4,.57,z),1.5,.5)
  prefab('ForestClearingLanding'+str(i),'FunctionalObjects/HopGroundHangout',(x,.06,z+1.7),(1.2,1,1.2))
 return {'added_trees':len(added)-2,'grass_cards':len(grass)*2,'flower_cards':len(flowers)*2,'rest_pockets':rests}
