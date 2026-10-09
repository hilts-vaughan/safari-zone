"""Emit native scenery and embedded geometry from the reserve layout."""
import math,json,random
from gatehouse_scene import contains as in_gatehouse
from grasslands_layout import contains as in_grasslands
from frontage_scene import contains as in_frontage
from woodland_section import contains as in_study,ORIGIN as STUDY_ORIGIN,SCENE as STUDY_SCENE
from enclosure_layout import blocked
from highlands_garden import contains as in_highlands
from wetlands_clearing import contains as in_water_garden
from picnic_garden import contains as in_picnic
from gate_picnic import contains as in_gate_picnic
from forest_service_garden import contains as in_service
from map_layout import layout,FACILITIES,WAYPOINTS,PONDS,segments,biome,inside,clear,preview,segment_distance

def build(g):
 node,sub,vec,mat,box,prefab,scriptnode=[g[n] for n in ['node','sub','vec','mat','box','prefab','scriptnode']]
 mats=g['mats'];bids=g['bids'];root=g['ROOT'];out=g['OUT'];model=layout();rng=random.Random(865)
 for k,c in [('soil','#91ac70'),('meadow','#a6b87e'),('forestfloor','#748e61'),('shore','#b4bd86'),('stone','#b8b093'),('flower','#e2c69e')]:mats[k]=mat(c)
 # The polygon is a single continuous floor; extrusion points downward.
 polygon=', '.join(str(v) for p in model['outline'] for v in p)
 node('ReserveFloor','CSGPolygon3D','.',f'position = Vector3(0, -1, 0)\nrotation_degrees = Vector3(90, 0, 0)\npolygon = PackedVector2Array({polygon})\ndepth = 1.0\nmaterial = {mats["grass"]}\nuse_collision = true\ncollision_layer = 11\ncollision_mask = 0')
 unitbox=sub('BoxMesh','size = Vector3(1, 1, 1)')
 unitdisk=sub('CylinderMesh','top_radius = 1.0\nbottom_radius = 1.0\nheight = 1.0\nradial_segments = 16')
 def shape(name,pos,size,m,disk=False,angle=0):
  node(name,'MeshInstance3D','.',f'position = {vec(pos)}\nscale = {vec(size)}\nrotation_degrees = Vector3(0, {angle}, 0)\nmesh = {unitdisk if disk else unitbox}\nmaterial_override = {mats[m]}')
 def link(name,a,b,width,m,y=.04,solid=False,height=.08):
  dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz);angle=math.degrees(math.atan2(dx,dz))
  pos=((a[0]+b[0])/2,y,(a[1]+b[1])/2)
  if solid:
   node(name,'Node3D','.',f'position = {vec(pos)}\nrotation_degrees = Vector3(0, {angle}, 0)')
   node('Mesh','MeshInstance3D',name,f'scale = {vec((width,height,length+.25))}\nmesh = {unitbox}\nmaterial_override = {mats[m]}')
   node('Body','StaticBody3D',name,'collision_layer = 11\ncollision_mask = 0')
   col=sub('BoxShape3D','size = '+vec((width,height,length+.25)));node('Shape','CollisionShape3D',name+'/Body','shape = '+col)
  else:shape(name,pos,(width,height,length+.8),m,angle=angle)
 from path_surface import build as build_paths
 paths=build_paths(g)
 from enclosure_scene import build as build_enclosures
 enclosures=build_enclosures(g)
 from forest_gate_scene import build as build_forest_gate
 forest_gate=build_forest_gate(g)
 from sculpted_terrain import surface,flat_ground,foliage
 hilltop_foliage=foliage(g)
 for i,(a,b) in enumerate(zip(model['outline'],model['outline'][1:]+model['outline'][:1])):
  # Low visual stone edge backed by an invisible perimeter collision wall.
  link('ReserveEdge_'+str(i),a,b,.65,'rock',y=.3,solid=True,height=.6)
  node('Boundary_'+str(i),'StaticBody3D','.',f'position = {vec(((a[0]+b[0])/2,4,(a[1]+b[1])/2))}\nrotation_degrees = Vector3(0, {math.degrees(math.atan2(b[0]-a[0],b[1]-a[1]))}, 0)\ncollision_layer = 11\ncollision_mask = 0')
  c=sub('BoxShape3D','size = '+vec((.8,8,math.dist(a,b)+.5)));node('Shape','CollisionShape3D','Boundary_'+str(i),'shape = '+c)
 # Wavy habitat boundaries are tiled volumes, not four square terrain slabs.
 for key,name,_,_,_ in g['zones']:
  scriptnode('Zone_'+key,'Area3D','Core/BiomeZone',(0,10,0),f'_biomeResource = {bids[key]}\ncollision_layer = 0\ncollision_mask = 0')
  c=sub('BoxShape3D','size = Vector3(16, 80, 16)')
  j=0
  for x in range(-176,177,16):
   for z in range(-128,129,16):
    if biome((x,z))==key:
     node('Cell'+str(j),'CollisionShape3D','Zone_'+key,f'position = {vec((x,0,z))}\nshape = '+c);j+=1
  x,z=FACILITIES[key]
  scriptnode('Spawner_'+key,'Node3D','Core/BirdSpawner',(x,12,z),'_spawnType = 1438849508')
  # Facilities sit off the trail in a wide clearing, with a short access spur.
  if key!='grass':prefab('Shop_'+key,'CoreGameplay/Shop',(x-8,0,z-8),props=f'_biome = {bids[key]}')
  if key!='grass':prefab('Develop_'+key,'CoreGameplay/DevelopOTron',(x+8,0,z-8))
  prefab('Warp_'+key,'FunctionalObjects/BiomeWarpPoint',(x+7,.15,z+7),props=f'_biome = {bids[key]}')
 for i,(x,z,rx,rz) in enumerate(PONDS):
  shape('PondBank_'+str(i),(x,.035,z),(rx+2,.04,rz+2),'shore',True)
  shape('Pond_'+str(i),(x,.1,z),(rx,.06,rz),'water',True)
  scriptnode('WaterArea'+str(i),'Area3D','Core/WaterArea',(x,-2.4,z))
  c=sub('CylinderShape3D',f'radius = 1.0\nheight = 5.0');node('Shape','CollisionShape3D','WaterArea'+str(i),f'scale = {vec((rx,1,rz))}\nshape = '+c)
  # The native AI can pick any compatible hangout in the whole map.
  # Keep duck destinations in one convex pond so every transition stays wet.
  if i==1:
   for copy in range(1):
    prefab(f'PondSwimHangout_{i}_{copy}','FunctionalObjects/WaterHangout',
           (x,.13,z),(rx*.65,1,rz*.65),props='_maxOccupants = 2')
   scriptnode('PondWaterSpawner'+str(i),'Node3D','Core/BirdSpawner',
              (x,.13,z),'_spawnType = 3806188274')
  # Raised lily pads give flying water birds a supported dry landing above the waterline.
  from park_perches import flat
  lily=g['mat']('#588e57')
  for j,(dx,dz) in enumerate([(-.45,-.25),(.30,-.4),(.45,.25),(-.2,.4)]):
   px,pz=x+dx*rx,z+dz*rz
   pad=sub('CylinderMesh','top_radius = 1.05\nbottom_radius = 1.05\nheight = 0.08\nradial_segments = 12')
   node(f'LilyPad{i}_{j}','MeshInstance3D','.',f'position = {vec((px,.17,pz))}\nmesh = {pad}\nmaterial_override = {lily}')
   body=sub('CylinderShape3D','radius = 1.0\nheight = 0.08')
   node(f'LilyPadBody{i}_{j}','StaticBody3D','.',f'position = {vec((px,.17,pz))}\ncollision_layer = 11\ncollision_mask = 0')
   node('Shape','CollisionShape3D',f'LilyPadBody{i}_{j}','shape = '+body)
   flat(g,f'LilyPadLanding{i}_{j}',(px,.225,pz),1.2,1.2)
  for j in range(14):
   t=2*math.pi*j/14;px=x+(rx+1.5)*math.cos(t);pz=z+(rz+1.5)*math.sin(t)
   if inside((px,pz)) and clear((px,pz),0):prefab(f'Reeds_{i}_{j}','Decorations/MarshBushA',(px,.1,pz),(.8,1.3,.8))
 trees={'forest':['TreeCFunctional','TreeBFunctional','GaryOakTreeAFunctional'],'grass':['TreeCFunctional','CherryBlossomTreeAFunctional'],'water':['WillowTreeAFunctional','MarshTreeAFunctional'],'cliffs':['ConiferousTreeSmallAFunctional','TreeADeadFunctional']}
 for i,(p,key,s) in enumerate(model['trees']):
  x,z=p;kind=rng.choice(trees[key]);s*=1.6 if key=='forest' else 1;s*=.16 if kind=='WillowTreeAFunctional' else 1
  # Preserve random choices/IDs while omitting trees in the gatehouse and
  # perimeter collider. The west tree rests on the existing garden ridge.
  if not flat_ground(p,1.2) or i in (0,51,92) or in_picnic(p) or in_service(p) or in_highlands(p) or in_water_garden(p) or in_gate_picnic(p):continue
  prefab('Tree_'+str(i),'FunctionalObjects/'+kind,(x,0,z),(s,s,s))
 for i,(p,key,s) in enumerate(model['shrubs']):
  if not flat_ground(p,1.5) or in_picnic(p) or in_service(p) or in_highlands(p) or in_water_garden(p) or in_gate_picnic(p):continue
  prefab('Shrub_'+str(i),'Decorations/'+('MarshBushB' if key=='water' else 'MarshBushA'),(p[0],0,p[1]),(s,s,s))
  if i%3==0:prefab('BushPerch_'+str(i),'FunctionalObjects/BushHangout',(p[0],.7*s,p[1]))
 for i,(p,key,t) in enumerate(model['details']):
  if not flat_ground(p,1.5) or in_picnic(p) or in_service(p) or in_highlands(p) or in_water_garden(p) or in_gate_picnic(p):continue
  asset='Flowers' if t<.18 and key in ['grass','forest'] else ('YellowGrassA' if key=='cliffs' else 'GreenGrassA' if t<.65 else 'GreenGrassB')
  s=.08 if asset=='Flowers' else 1.1;prefab('Understory_'+str(i),'Decorations/'+asset,(p[0],.26 if asset=='Flowers' else .15,p[1]),(s,s,s))
  if i%12==0:shape('GroundPatch_'+str(i),(p[0],.012,p[1]),(3.5,.018,2.8),{'forest':'forestfloor','grass':'meadow','water':'soil','cliffs':'stone'}[key],True)
 # Ground perches are evenly distributed through safe, dry photography pockets.
 count=0
 for x in range(-140,145,14):
  for z in range(-98,100,14):
   if (x,z)==(42,-70) or min(segment_distance((x,z),a,b) for a,b in zip(model["outline"],model["outline"][1:]+model["outline"][:1]))<4:continue
   if not in_gate_picnic((x,z)) and not in_water_garden((x,z)) and not in_highlands((x,z)) and not in_grasslands((x,z),1) and not in_gatehouse((x,z),2) and not in_study((x,z),1) and inside((x,z)) and clear((x,z),1) and not blocked((x,z),1) and flat_ground((x,z),2):
    prefab('GroundPerch_'+str(count),'FunctionalObjects/HopGroundHangout',(x,.115,z),(2,1,2));count+=1
 node('WoodlandPassage',None,'.','position = '+vec((STUDY_ORIGIN[0],0,STUDY_ORIGIN[1])),g['resource'](STUDY_SCENE,'PackedScene'))
 from center_scene import build as build_center
 build_center(g)
 from frontage_scene import build as build_frontage
 frontage=build_frontage(g)
 from gatehouse_scene import build as build_gatehouse
 build_gatehouse(g)
 from grasslands_scene import build as build_grasslands
 grasslands=build_grasslands(g)
 from bird_garden_scene import build as build_bird_garden
 bird_garden=build_bird_garden(g)
 from bench_landing_spots import build as build_benches
 benches=build_benches(g)
 from park_perches import build as build_park_perches
 park_perches=build_park_perches(g)
 from forest_garden import build as build_forest_garden
 forest_garden=build_forest_garden(g)
 from wetlands_garden import build as build_wetlands
 wetlands=build_wetlands(g)
 from wetlands_clearing import build as build_water_garden
 water_garden=build_water_garden(g)
 from fountain_garden import build as build_fountain
 fountain=build_fountain(g)
 from picnic_garden import build as build_picnic
 picnic=build_picnic(g)
 from gate_picnic import build as build_gate_picnic
 gate_picnic=build_gate_picnic(g)
 from forest_service_garden import build as build_service
 service=build_service(g)
 from woodland_border import build as build_border
 border=build_border(g)
 from highlands_garden import build as build_highlands
 highlands=build_highlands(g)
 from meadow_perch_grove import build as build_grove
 grasslands['perch_grove']=build_grove(g)
 preview(model,out/'map.png');preview(model,root/'docs/map-layout.png')
 stats={'area_m2':round(model['area'],3),'original_area_m2':168*168,'area_multiplier':round(model['area']/(168*168),5),'trees':len(model['trees']),'shrubs':len(model['shrubs']),'ground_details':len(model['details']),'ground_perches':count,'path_width_m':5.5,'paths':paths,'hilltop_foliage':hilltop_foliage,'ponds':len(PONDS),'waypoints':WAYPOINTS,'facilities':FACILITIES,'outline':model['outline'],'enclosures':enclosures,'grasslands':grasslands,'frontage':frontage,'forest_checkpoint':forest_gate,'bird_garden':bird_garden,'benches':benches,'park_perches':park_perches,'forest_garden':forest_garden,'wetlands_garden':wetlands,'wetlands_water_garden':water_garden,'fountain_garden':fountain,'picnic_garden':picnic,'gate_picnic':gate_picnic,'forest_service_garden':service,'woodland_border':border,'highlands_garden':highlands}
 (root/'docs/map-layout.json').write_text(json.dumps(stats,indent=2)+'\n')
