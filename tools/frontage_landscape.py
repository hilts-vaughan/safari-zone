"""Gate-connected timber boundaries and native grass/perches for Center exits."""
import math,random
GATES=[(-96.3,80,24),(-47.8,79,-10)]
BEDS=[(-112,85,8,3.5),(-87,92,8,3),(-98,87,3.2,5),(-33,80,3,4),(-35,98,5,2.6)]
TREES=[(-89,92),(-98,88),(-31,78),(-33,98)]
PERCHES=[(-84,93,1.8),(-91,94,2.2),(-98,90,1.8),(-31,81,1.8),(-36,98,2.2),(-40,99,1.8)]
def endpoints(gate):
 x,z,angle=gate;a=math.radians(angle)
 return [(x+side*3.6*math.cos(a),z-side*3.6*math.sin(a)) for side in [-1,1]]
def fences():
 west,east=map(endpoints,GATES)
 lines=[[(-133,80),(-116,81),west[0]],[west[1],(-85,76),(-80.8,76)],
        [(-59.2,76),east[0]],[east[1],(-27,76),(-27,106)]]
 return [(a,b) for line in lines for a,b in zip(line,line[1:])]
def grass_positions():
 from map_layout import inside,path_distance,segment_distance
 from frontage_scene import APPROACH
 rng=random.Random(43804);out=[]
 for bed,(x,z,rx,rz) in enumerate(BEDS):
  for ix in range(math.ceil(rx*2/.45)):
   for iz in range(math.ceil(rz*2/.45)):
    px=x-rx+(ix+.5)*.45+rng.uniform(-.12,.12);pz=z-rz+(iz+.5)*.45+rng.uniform(-.12,.12)
    if ((px-x)/rx)**2+((pz-z)/rz)**2>1:continue
    if not inside((px,pz)) or path_distance((px,pz))<2.15:continue
    if min(segment_distance((px,pz),a,b) for a,b in zip(APPROACH,APPROACH[1:]))<1.8:continue
    # The Center apron and bench approach remain clear.
    if -85<px<-55 and 78<pz<91:continue
    out.append((px,pz,rng.uniform(.95,1.3),rng.uniform(0,math.pi),bed))
 return out

def build(g):
 node,sub,vec,box,prefab=[g[n] for n in ['node','sub','vec','box','prefab']]
 parent='CenterArrival'
 for i,(a,b) in enumerate(fences()):
  dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz);angle=math.degrees(math.atan2(dx,dz))
  name='ArrivalFence'+str(i);path=parent+'/'+name
  node(name,'Node3D',parent,f'position = {vec(((a[0]+b[0])/2,0,(a[1]+b[1])/2))}\nrotation_degrees = Vector3(0,{angle},0)')
  for j in range(math.ceil(length/2.4)+1):
   local=-length/2+length*j/math.ceil(length/2.4)
   box('Post'+str(j),(0,.73,local),(.22,1.46,.22),'arrivalwood',solid=False,parent=path)
  for j,y in enumerate([.37,.77,1.17]):box('Rail'+str(j),(0,y,0),(.12,.16,length+.2),'arrivalwood',solid=False,parent=path)
  # Continuous collision avoids catching a player on individual fence posts.
  node('Guard','StaticBody3D',path,'collision_layer = 11\ncollision_mask = 0')
  shape=sub('BoxShape3D','size = '+vec((.24,1.4,length+.2)))
  node('Shape','CollisionShape3D',path+'/Guard','position = Vector3(0,0.7,0)\nshape = '+shape)
 texture=g['resource']('res://EXTERNAL/Touma/SafariZone/Frontage/tall-grass.png','Texture2D')
 material=sub('StandardMaterial3D',f'transparency = 2\nalpha_scissor_threshold = 0.85\ncull_mode = 2\nalbedo_color = Color(1,1,1,1)\nalbedo_texture = {texture}\nroughness = 1.0')
 mesh=sub('QuadMesh','size = Vector2(1,1)');buffer=[];positions=grass_positions()
 for x,z,h,a,_ in positions:
  for turn in [0,math.pi/2]:
   c,s=math.cos(a+turn),math.sin(a+turn)
   buffer.extend([c*.85,0,s,x,0,h,0,h/2+.025,-s*.85,0,c,z])
 mm=sub('MultiMesh',f'transform_format = 1\ninstance_count = {len(positions)*2}\nmesh = {mesh}\nbuffer = PackedFloat32Array('+', '.join(str(round(v,5)) for v in buffer)+')')
 node('ArrivalTallGrass','MultiMeshInstance3D',parent,f'multimesh = {mm}\nmaterial_override = {material}')
 for i,(x,z) in enumerate(TREES):
  prefab('ArrivalTallTree'+str(i),'FunctionalObjects/TreeCFunctional',(x,.04,z),(1.8,1.8,1.8))
  from tree_landing_spots import add
  add(g,'ArrivalTallTree'+str(i),x,z,1.8)
 for i,(x,z,h) in enumerate(PERCHES):
  box('ArrivalPerchPost'+str(i),(x,h/2,z),(.22,h,.22),'arrivalwood',parent=parent)
  box('ArrivalPerchBar'+str(i),(x,h,z),(1.6,.16,.55),'arrivaldark',parent=parent)
  prefab('ArrivalBirdPerch'+str(i),'FunctionalObjects/RockHangout',(x,h+.09,z),(1.2,1,.4))
 for i,(x,z,rx,rz) in enumerate(BEDS):
  from sculpted_terrain import flat_ground
  if not flat_ground((x,z),2.4):continue
  prefab('ArrivalGrassPerch'+str(i),'FunctionalObjects/HopGroundHangout',(x,.06,z),(2.4,1,1.8))
 return dict(tall_grass_cards=len(positions)*2,tall_trees=len(TREES),bird_posts=len(PERCHES),fence_runs=len(fences()))
