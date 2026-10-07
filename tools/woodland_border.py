"""Planted lawn and cliff edge alongside the existing authored woodland."""
import json,math,random
from pathlib import Path
from fountain_garden import distance
ROUTE=[(-32,-27),(-28,-26),(-23,-25),(-18,-25.5),(-13,-23),(-7,-22),(0,-21),(6,-21),(8,-25)]
TREES=[(-27,-29,1.55),(-17,-29,1.4)]
ROCKS=[(-23,-28,.8),(-12,-19,.6),(-4,-19,.75)]
SHELVES=[(-25,-14.5,2.6),(-13,-14.8,3.0)]
def build(g):
 from park_perches import flat
 from woodland_section import plan
 from map_layout import path_distance
 node,sub,vec,box,prefab=[g[k] for k in ['node','sub','vec','box','prefab']]
 parent='WoodlandBorderGarden';node(parent,'Node3D','.')
 survey=json.loads((g['ROOT']/'assets/environment/woodland/border-ground.json').read_text())
 heights={(x,z):h for x,z,h in survey['samples']}
 def ground(x,z):
  # Bilinear interpolation of the existing terrain survey; unknown props stay excluded.
  x0,z0=math.floor(x),math.floor(z);t,u=x-x0,z-z0
  corners=[heights.get((xx,zz)) for xx,zz in [(x0,z0),(x0+1,z0),(x0,z0+1),(x0+1,z0+1)]]
  if any(h is None for h in corners):return None
  return (corners[0]*(1-t)+corners[1]*t)*(1-u)+(corners[2]*(1-t)+corners[3]*t)*u
 for i,(x,z,s) in enumerate(TREES):
  prefab(f'BorderTree{i}','FunctionalObjects/TreeCFunctional',(x,0,z),(s,s,s))
  for side in (-1,1):
   y=(2.2 if side==1 else 2.7)*s
   box(f'Branch{i}_{side}',(x+side*.85*s,y-.055,z),(1.3*s,.11,.28),'arrivaldark',parent=parent)
   flat(g,f'BorderBranchLanding{i}_{side}',(x+side*1.05*s,y+.01,z),.65*s,.20)
 # Same faceted stone palette and polygon geometry as the existing cliffs.
 g['mats']['borderstone']=g['mat']('#65716f');g['mats']['borderturf']=g['mat']('#92b16f')
 def stone(name,x,z,top,rx,rz,thickness,turf=False):
  # Flat top and tapering underside, visible mesh and convex collision agree.
  sides=8;mesh=sub('CylinderMesh',f'top_radius = 1.0\nbottom_radius = 0.55\nheight = {thickness}\nradial_segments = {sides}')
  node(name,'MeshInstance3D',parent,f'position = {vec((x,top-thickness/2,z))}\nscale = {vec((rx,1,rz))}\nmesh = {mesh}\nmaterial_override = {g["mats"]["borderstone"]}')
  vertices=[]
  for y,r in [(-thickness/2,.55),(thickness/2,1)]:
   for k in range(sides):vertices.extend([rx*r*math.sin(k*2*math.pi/sides),y,rz*r*math.cos(k*2*math.pi/sides)])
  shape=sub('ConvexPolygonShape3D','points = PackedVector3Array('+', '.join(map(str,vertices))+')')
  node(name+'Body','StaticBody3D',parent,f'position = {vec((x,top-thickness/2,z))}\ncollision_layer = 11\ncollision_mask = 0')
  node('Shape','CollisionShape3D',parent+'/'+name+'Body','shape = '+shape)
  if turf:
   cap=sub('CylinderMesh','top_radius = 1.0\nbottom_radius = 1.0\nheight = 0.04\nradial_segments = 8')
   node(name+'Turf','MeshInstance3D',parent,f'position = {vec((x,top+.015,z))}\nscale = {vec((rx,1,rz))}\nmesh = {cap}\nmaterial_override = {g["mats"]["borderturf"]}')
 for i,(x,z,h) in enumerate(ROCKS):
  stone('Rock'+str(i),x,z,h,1.05,.85,h)
  flat(g,f'BorderRockLanding{i}',(x,h+.01,z),.9,.65)
 for i,(x,z,h) in enumerate(SHELVES):
  stone('Shelf'+str(i),x,z,h,1.7,1.1,.95,True)
  # Thin turf cap is visual; its support stays within 4cm of the landing origin.
  flat(g,f'BorderShelfLanding{i}',(x,h+.025,z),1.3,.6)
 for i,(a,b) in enumerate(zip(ROUTE,ROUTE[1:])):
  length=math.dist(a,b);angle=math.degrees(math.atan2(b[0]-a[0],b[1]-a[1]))
  node(f'Path{i}','MeshInstance3D',parent,f'position = {vec(((a[0]+b[0])/2,.025,(a[1]+b[1])/2))}\nrotation_degrees = Vector3(0,{angle},0)\nmesh = '+sub('BoxMesh',f'size = Vector3(1.5,0.035,{length+.65})')+f'\nmaterial_override = {g["mats"]["path"]}')
 # Dense islands and cliff-base border, with dry gaps for walking/foraging.
 original=plan();trunks=original['trees']+[(x,z) for x,z,_ in TREES]
 rng=random.Random(1052042);grass=[];flowers=[]
 for ix in range(73):
  for iz in range(27):
   x=-30+ix*.5;z=-30+iz*.5;p=(x,z);h=ground(x,z)
   if h is None or h>.18:continue
   if min(distance(p,a,b) for a,b in zip(ROUTE,ROUTE[1:]))<1.2 or path_distance(p)<1.9:continue
   if any(math.dist(p,q)<1.4 for q in trunks):continue
   if any(math.dist(p,(rx,rz))<1.3 for rx,rz,_ in ROCKS):continue
   if any(math.dist(p,q)<1 for q in [(-26,-22),(-20,-28),(-15,-20)]):continue
   if any(math.dist(p,q)<2.6 for q in original['hedges']):continue
   # Retain irregular open pockets rather than a uniform rectangle.
   if z<-25 and math.sin(x*.39)+math.cos(z*.47)<-.1:continue
   if rng.random()<.13:continue
   target=flowers if rng.random()<.5 else grass
   target.append((x,h,z,rng.uniform(.85,1.25) if target is grass else rng.uniform(.5,.75),rng.uniform(0,math.pi)))
 quad=sub('QuadMesh','size = Vector2(1,1)')
 for name,asset,points in [('Grass','tall-grass',grass),('Flowers','wildflowers',flowers)]:
  tex=g['resource']('res://EXTERNAL/Touma/SafariZone/Frontage/'+asset+'.png','Texture2D')
  material=sub('StandardMaterial3D',f'transparency = 2\nalpha_scissor_threshold = 0.85\ncull_mode = 2\nalbedo_texture = {tex}\nroughness = 1.0')
  buffer=[]
  for x,y,z,h,a in points:
   for turn in (0,math.pi/2):
    c,s=math.cos(a+turn),math.sin(a+turn);buffer.extend([c*.85,0,s,x,0,h,0,y+h/2+.025,-s*.85,0,c,z])
  mm=sub('MultiMesh',f'transform_format = 1\ninstance_count = {len(points)*2}\nmesh = {quad}\nbuffer = PackedFloat32Array('+', '.join(str(round(v,5)) for v in buffer)+')')
  node(name,'MultiMeshInstance3D',parent,f'multimesh = {mm}\nmaterial_override = {material}')
 # Small flattened oval leaves follow the surveyed cliff surface. No new texture.
 leaf=sub('SphereMesh','radius = 0.5\nheight = 1.0\nradial_segments = 6\nrings = 3')
 vines=0
 for base in [-28,-22,-17,-10,-5]:
  for j in range(24):
   x=base+.55*math.sin(j*.6);z=-14.6+j*.125;y=ground(x,z)
   if y is None or y<.5:continue
   for side in (-1,1):
    node(f'VineLeaf{vines}','MeshInstance3D',parent,f'position = {vec((x+side*.14,y+.04,z-.1))}\nscale = Vector3(0.28,0.09,0.40)\nrotation_degrees = Vector3(45,{side*30},0)\nmesh = {leaf}\nmaterial_override = {g["mats"]["leaf"]}');vines+=1
 for i,(x,z) in enumerate([(-26,-22),(-20,-28),(-15,-20)]):prefab(f'BorderForaging{i}','FunctionalObjects/HopGroundHangout',(x,.06,z),(.8,1,.8))
 return {'trees':2,'rocks':3,'shelves':2,'landing_rectangles':9,'foraging_pockets':3,'grass_cards':len(grass)*2,'flower_cards':len(flowers)*2,'vine_leaves':vines,'route':ROUTE}
