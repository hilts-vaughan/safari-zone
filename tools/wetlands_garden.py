"""Dry-bank habitat pockets, an open forest lake edge, and high-only legend roosts."""
import math, random

def build(g):
 from map_layout import layout, inside, path_distance, pond_contains
 from gatehouse_scene import contains as indoors
 from enclosure_layout import blocked
 from woodland_section import contains as study
 from tree_landing_spots import add as branches
 from park_perches import flat
 from sculpted_terrain import flat_ground
 from wetlands_clearing import contains as in_water_garden
 from gate_picnic import contains as in_gate_picnic
 node,sub,vec,box,prefab=[g[k] for k in ['node','sub','vec','box','prefab']]
 parent='WetlandsGarden';node(parent,'Node3D','.')
 model=layout();trunks=[p for p,_,_ in model['trees']];rng=random.Random(10052026)
 def safe(p,r=1):
  return not in_gate_picnic(p,r) and not in_water_garden(p,r) and flat_ground(p,r) and inside(p) and not indoors(p,4+r) and not pond_contains(p,2+r) and not blocked(p,r) and path_distance(p)>2.8+r and not study(p,2)
 trees=[]
 centers=[(58,91),(100,91),(112,63),(86,31),(125,20),(63,17)]
 for x in range(49,133,5):
  for z in range(11,102,5):
   p=(x,z)
   if len(trees)<18 and min(math.dist(p,c) for c in centers)<11 and safe(p,1.6) and all(math.dist(p,q)>3.4 for q in trunks+trees):trees.append(p)
 for cx,cz in [(58,91),(100,91),(112,63),(86,31),(125,20),(63,17)]:
  for dx,dz in [(-3,-3),(3,0),(0,4)]:
   p=(cx+dx,cz+dz)
   if safe(p,1.6) and all(math.dist(p,q)>3 for q in trunks+trees):trees.append(p)
 for i,(x,z) in enumerate(trees):
  s=1.7+(i%3)*.15
  prefab('WetlandsBankTree'+str(i),'FunctionalObjects/TreeCFunctional',(x,0,z),(s,s,s))
  branches(g,'WetlandsBankTree'+str(i),x,z,s,parent=parent)
 # Existing marsh trees get the same supported branch-tip landing rectangles.
 for i,(p,key,s) in enumerate(model['trees']):
  if not in_gate_picnic(p,2) and not in_water_garden(p,2) and flat_ground(p,1.2) and key=='water' and not indoors(p,3):branches(g,'WetlandsOriginalTree'+str(i),*p,s,parent=parent)
 grass=[];flowers=[];pockets=[]
 for cx,cz in [(58,91),(100,91),(112,63),(86,31),(125,20),(63,17)]:
  for ix in range(-8,9):
   for iz in range(-6,7):
    x=cx+ix*.65+rng.uniform(-.12,.12);z=cz+iz*.65+rng.uniform(-.12,.12)
    if not safe((x,z),.1) or any(math.dist((x,z),q)<1 for q in trunks+trees):continue
    target=flowers if abs(ix)>6 or abs(iz)>4 or rng.random()<.18 else grass
    target.append((x,z,rng.uniform(.65,1.25) if target is grass else .55,rng.uniform(0,math.pi)))
  if safe((cx,cz),1.5) and all(math.dist((cx,cz),q)>2 for q in trunks+trees):pockets.append((cx,cz))
 quad=sub('QuadMesh','size = Vector2(1,1)')
 def cards(name,asset,points):
  tex=g['resource']('res://EXTERNAL/Touma/SafariZone/Frontage/'+asset+'.png','Texture2D')
  mat=sub('StandardMaterial3D',f'transparency = 2\nalpha_scissor_threshold = 0.85\ncull_mode = 2\nalbedo_texture = {tex}\nroughness = 1.0')
  buffer=[]
  for x,z,h,a in points:
   for turn in [0,math.pi/2]:
    c,s=math.cos(a+turn),math.sin(a+turn);buffer.extend([c*.85,0,s,x,0,h,0,h/2+.025,-s*.85,0,c,z])
  mm=sub('MultiMesh',f'transform_format = 1\ninstance_count = {len(points)*2}\nmesh = {quad}\nbuffer = PackedFloat32Array('+', '.join(str(round(v,5)) for v in buffer)+')')
  node(name,'MultiMeshInstance3D',parent,f'multimesh = {mm}\nmaterial_override = {mat}')
 cards('WetlandsTallGrass','tall-grass',grass);cards('WetlandsFlowers','wildflowers',flowers)
 for i,(x,z) in enumerate(pockets):
  # Small dry-bank stones and open foraging pockets, never spanning the water.
  box('BankRestStone'+str(i),(x,.3,z),(1.4,.6,1.2),'rock',parent=parent)
  flat(g,'BankStoneLanding'+str(i),(x,.61,z),1.1,.9)
  prefab('BankForaging'+str(i),'FunctionalObjects/HopGroundHangout',(x+2,.06,z),(1.2,1,1.2))
 # The authored forest/highlands lake is centered at (12,-55). Its eastern
 # retaining ridge is gone; keep the shore open, with low rocks and flowers.
 shore=[]
 for i,(x,z) in enumerate([]): # Retire redundant shore rocks intersecting the authored planting.
  box('LakeShoreStone'+str(i),(x,.25,z),(1.2,.5,.9),'rock',parent=parent)
  flat(g,'LakeShoreLanding'+str(i),(x,.51,z),.9,.65)
  for j in range(5):shore.append((x+(j-2)*.5,z+1.1,.5,j*.7))
 cards('ForestLakeFlowers','wildflowers',shore)
 # Broad supported cliff tops dedicated to the native high-point descriptor.
 for i,(x,z) in enumerate([(90,-93),(119,-84),(140,-52)]):
  mesh=sub('CylinderMesh','top_radius = 2.7\nbottom_radius = 4.2\nheight = 14.0\nradial_segments = 7')
  node('LegendOutcrop'+str(i),'MeshInstance3D',parent,f'position = {vec((x,7,z))}\nmesh = {mesh}\nmaterial_override = {g["mats"]["rock"]}')
  # Solid central support lies below the visible top; no inaccessible float.
  box('LegendOutcropCore'+str(i),(x,7,z),(3.2,14,3.2),'rock',parent=parent)
  prefab('LegendHighRoost'+str(i),'FunctionalObjects/BirdsOfPrayHangout',(x,14.025,z),(3.2,1,3.2),props='_maxOccupants = 1')
 return {'bank_trees':len(trees),'grass_cards':len(grass)*2,'flower_cards':len(flowers)*2,'dry_bank_pockets':pockets,'forest_lake_open':True,'high_roosts':3,'high_roost_height':14.025}
