"""Terraced highlands with native perches and a connected smooth scaffold route."""
import math,random
# Polygons share the existing woodland cliff palette, with successively smaller caps.
TERRACES=[
 (4,[(24,-104),(47,-110),(95,-108),(123,-98),(125,-84),(110,-73),(43,-73),(28,-86)]),
 (9,[(38,-102),(53,-107),(85,-102),(97,-91),(92,-80),(46,-80),(36,-90)]),
 (16,[(48,-101),(58,-104),(76,-100),(81,-91),(76,-85),(49,-85),(45,-92)]),
 (7,[(94,-99),(111,-100),(122,-92),(116,-83),(97,-83),(91,-90)])]
# All segments join generous level decks; long gradual ramps are hidden beneath treads.
ROUTE=[(42,0,-56),(42,4,-68),(58,9,-68),(58,9,-77),(74,16,-77),(74,16,-87)]
EAST_ROUTE=[(58,9,-77),(58,9,-82),(88,9,-82),(88,9,-76),(106,7,-76),(106,7,-87)]
BOULDERS=[(37,-55,1),(50,-32,0.85),(82,-33,1.1),(96,-49,0.8),(111,-23,1),(29,-29,0.75)]
BENCHES=[(98,-17),(71,-30)]
GROUND=[(33,-36),(53,-20),(87,-25),(104,-38)]
def contains(p,margin=0):
 from woodland_section import contains as authored
 return 18-margin<p[0]<133+margin and -113-margin<p[1]<-12+margin and not authored(p,2)
def grade_mask(p):
 if not contains(p):return 1
 return 0.0

def terrain_height(p):
 from map_layout import inside
 return max([h for h,poly in TERRACES if inside(p,poly)]+[0])

def build(g):
 from park_perches import flat
 from map_layout import path_distance,pond_contains,FACILITIES,inside
 from fountain_garden import distance
 node,sub,vec,box,prefab=[g[k] for k in ['node','sub','vec','box','prefab']]
 parent='HighlandsGarden';node(parent,'Node3D','.')
 g['mats']['highstone']=g['mat']('#65716f');g['mats']['highturf']=g['mat']('#92b16f')
 stats={'terraces':len(TERRACES),'route':ROUTE,'east_route':EAST_ROUTE};landing=0
 def perch(name,p,w,d):
  nonlocal landing
  flat(g,'HighlandsLanding'+name,p,w,d);landing+=1
 def prism(name,poly,top,base,material,solid=True):
  points=', '.join(str(v) for p in poly for v in p)
  node(name,'CSGPolygon3D',parent,f'position = Vector3(0,{base},0)\nrotation_degrees = Vector3(90,0,0)\npolygon = PackedVector2Array({points})\ndepth = {top-base}\nmaterial = {g["mats"][material]}\nuse_collision = {str(solid).lower()}\ncollision_layer = 11\ncollision_mask = 0')
 for i,(h,poly) in enumerate(TERRACES):
  prism('Cliff'+str(i),poly,h,0,'highstone')
  prism('Turf'+str(i),poly,h+.025,h-.015,'highturf',False)
 # Exposed front shelves provide supported landing strips without blocking the climb.
 for i,(x,z,h) in enumerate([(33,-86,4),(49,-74,4),(65,-74,4),(85,-74,4),(106,-74,4),(48,-81,9),(68,-81,9),(88,-81,9),(53,-86,16),(67,-86,16),(106,-84,7)]):
  box('Shelf'+str(i),(x,h-.4,z),(3.5,0.8,2.2),'highstone',parent=parent)
  box('ShelfCap'+str(i),(x,h+.005,z),(3.5,0.03,2.2),'highturf',False,parent=parent)
  perch('Shelf'+str(i),(x,h+.01,z),2.8,1.4)
 def beam(name,a,b,width=0.16,solid=False):
  dx,dy,dz=[b[i]-a[i] for i in range(3)];length=math.sqrt(dx*dx+dy*dy+dz*dz)
  angle=math.degrees(math.atan2(dx,dz));slope=-math.degrees(math.atan2(dy,math.hypot(dx,dz)))
  node(name,'Node3D',parent,f'position = {vec(tuple((a[i]+b[i])/2 for i in range(3)))}\nrotation_degrees = Vector3({slope},{angle},0)')
  box('Beam',(0,0,0),(width,width,length),'arrivalwood',solid,parent=parent+'/'+name)
 def deck(i,p):
  x,h,z=p;box('Deck'+str(i),(x,h-.15,z),(4.4,0.3,4.4),'arrivalwood',parent=parent)
  for k in range(14):box(f'DeckPlank{i}_{k}',(x-2.05+k*.315,h+.005,z),(0.018,0.018,4.3),'arrivaldark',False,parent=parent)
  for dx in [-2,2]:
   for dz in [-2,2]:
    box(f'DeckPost{i}_{dx}_{dz}',(x+dx,(h+1)/2,z+dz),(0.24,h+1,0.24),'arrivalwood',False,parent=parent)
  if h>2:beam('Brace'+str(i),(x-2,0.4,z-2),(x+2,h-.3,z-2),0.2)
  # Corner resting patch avoids crossing any scaffold entrance.
  perch('Deck'+str(i),(x-1.85,h+0.01,z+1.85),0.4,0.4)
 def run(name,points):
  nonlocal landing
  for i,(first,last) in enumerate(zip(points,points[1:])):
   distance_xz=math.hypot(last[0]-first[0],last[2]-first[2]);trim=min(2.2,distance_xz/2-0.1)
   a=(first[0]+(last[0]-first[0])*trim/distance_xz,first[1],first[2]+(last[2]-first[2])*trim/distance_xz)
   b=(last[0]-(last[0]-first[0])*trim/distance_xz,last[1],last[2]-(last[2]-first[2])*trim/distance_xz)
   dx,dy,dz=[b[j]-a[j] for j in range(3)];length=math.hypot(dx,dz);nx,nz=dz/length,-dx/length
   # A connected convex wedge removes individual tread collision edges.
   verts=[]
   for p in [a,b]:
    for side in [-1,1]:
     for y in [-.3,0]:verts.extend([p[0]+nx*1.65*side,p[1]+y,p[2]+nz*1.65*side])
   shape=sub('ConvexPolygonShape3D','points = PackedVector3Array('+', '.join(map(str,verts))+')')
   body=name+'Ramp'+str(i);node(body,'StaticBody3D',parent,'collision_layer = 11\ncollision_mask = 0');node('Shape','CollisionShape3D',parent+'/'+body,'shape = '+shape)
   count=math.ceil(length/.35)
   for j in range(count):
    t=(j+.5)/count;x=a[0]+dx*t;z=a[2]+dz*t;h=a[1]+dy*t
    # Decorative treads are beneath the smooth collision surface.
    node(f'{name}Tread{i}_{j}','MeshInstance3D',parent,f'position = {vec((x,h-.1,z))}\nrotation_degrees = Vector3(0,{math.degrees(math.atan2(dx,dz))},0)\nmesh = '+sub('BoxMesh',f'size = Vector3(3.3,0.20,{length/count+.018})')+f'\nmaterial_override = {g["mats"]["arrivalwood"]}')
   for side in [-1,1]:
    p=tuple(a[k]+(nx*1.75*side if k==0 else nz*1.75*side if k==2 else 1.05) for k in range(3));q=tuple(b[k]+(nx*1.75*side if k==0 else nz*1.75*side if k==2 else 1.05) for k in range(3))
    beam(f'{name}Guard{i}_{side}',p,q,0.16,True)
    if abs(dy)<0.001:
     from park_perches import rail
     rail(g,f'HighlandsLandingRail{name}{i}_{side}',p,q,0.16,parent);landing+=1
    beam(f'{name}Rail{i}_{side}',(p[0],p[1]-.4,p[2]),(q[0],q[1]-.4,q[2]),0.10)
    for j in range(math.ceil(length/2)+1):
     t=j/math.ceil(length/2);x=p[0]+(q[0]-p[0])*t;z=p[2]+(q[2]-p[2])*t;h=a[1]+dy*t
     box(f'{name}Upright{i}_{side}_{j}',(x,h+.5,z),(0.16,1.15,0.16),'arrivalwood',False,parent=parent)
  for i,p in enumerate(points):deck(name+str(i),p)
 run('Main',ROUTE);run('East',EAST_ROUTE);run('Lower',[(42,4,-68),(42,4,-76)])
 # Upper roosts for the high-only rare legends, supported on summit stone.
 for i,(x,z) in enumerate([(56,-94),(68,-96)]):
  prefab('HighlandsLegendRoost'+str(i),'FunctionalObjects/BirdsOfPrayHangout',(x,16.02,z),(1.8,1,1.8),props='_maxOccupants = 1')
 # Trees placed deliberately around the meadow and on flat terrace interiors.
 trees=[(29,-95,1.5),(37,-98,1.3),(48,-95,1.5),(63,-99,1.4),(76,-95,1.3),(87,-94,1.5),(103,-92,1.4),(114,-90,1.2),(46,-76,1.3),(82,-76,1.5),(115,-78,1.2),
 (28,-60,1.4),(33,-49,1.5),(47,-58,1.4),(56,-60,1.3),(79,-61,1.5),(91,-59,1.4),(106,-61,1.5),(119,-62,1.3),(27,-37,1.5),(41,-32,1.3),(58,-24,1.4),(78,-23,1.3),(91,-36,1.4),(107,-31,1.3),(127,-33,1.4)]
 for i,(x,z,s) in enumerate(trees):
  if i==11:continue # Existing sculpted escarpment occupies this tree footprint.
  h=terrain_height((x,z));kind='TreeCFunctional' if i%4==0 else 'ConiferousTreeSmallAFunctional'
  prefab('HighlandsTree'+str(i),'FunctionalObjects/'+kind,(x,h,z),(s,s,s))
  # Compact solid branch ends stay outside the trunk.
  y=h+2.1*s;box('TreeBranch'+str(i),(x+.9*s,y-.06,z),(1.3*s,0.12,0.24),'arrivaldark',parent=parent)
  perch('Tree'+str(i),(x+1.15*s,y+.01,z),0.6*s,0.18)
 for i,(x,z,h) in enumerate(BOULDERS):
  poly=[(x+1.7*math.cos(j*math.tau/7),z+1.3*math.sin(j*math.tau/7)) for j in range(7)]
  prism('Boulder'+str(i),poly,h,0,'highstone');perch('Rock'+str(i),(x,h+.01,z),1.7,1.1)
 from bench_landing_spots import add as bench_landing
 for i,(x,z) in enumerate(BENCHES):
  for j in range(4):box(f'Bench{i}Seat{j}',(x,0.6,z-.45+j*.28),(3.6,0.14,0.22),'plank',parent=parent)
  for j in range(3):box(f'Bench{i}Back{j}',(x,0.95+j*.24,z-.65),(3.6,0.18,0.12),'plank',parent=parent)
  for side in [-1,1]:
   box(f'Bench{i}Leg{side}',(x+side*1.25,0.26,z),(0.12,0.52,0.8),'iron',parent=parent)
   box(f'Bench{i}Support{side}',(x+side*1.25,0.9,z-.7),(0.12,1.3,0.12),'iron',parent=parent)
  bench_landing(g,'HighlandsBench'+str(i),[(x,0.67,z-.45+j*.28,3.6,0.22) for j in range(4)],(x,1.52,z-.65,3.6,0.12));landing+=5
 box('DryLog',(35,0.35,-22),(4,0.7,0.9),'arrivaldark',parent=parent);perch('Log',(35,0.71,-22),3.4,0.65)
 for i,(x,z) in enumerate(GROUND):prefab('HighlandsForaging'+str(i),'FunctionalObjects/HopGroundHangout',(x,0.06,z),(1.4,1,1.4))
 from highlands_pavilion import build as build_pavilion
 stats['pavilion']=build_pavilion(g)
 # Tall grass and flowers throughout lower meadow and broad terrace interiors.
 rng=random.Random(510226);grass=[];flowers=[]
 for ix in range(153):
  for iz in range(139):
   x=22+ix*.7;z=-108+iz*.7;p=(x,z);h=terrain_height(p)
   if math.dist(p,(77,-48))<8 or any(math.dist(p,q)<3 for q in [(53,-43),(60,-46)]):continue
   if not contains(p) or not inside(p) or pond_contains(p,2) or path_distance(p)<3.6:continue
   if any(math.dist(p,q)<15 for q in FACILITIES.values()):continue
   if any(distance(p,(a[0],a[2]),(b[0],b[2]))<3 for line in [ROUTE,EAST_ROUTE,[(42,4,-68),(42,4,-76)]] for a,b in zip(line,line[1:])):continue
   if any(math.dist(p,(tx,tz))<1.6 for tx,tz,_ in trees):continue
   if any(math.dist(p,(rx,rz))<2.1 for rx,rz,_ in BOULDERS):continue
   if any(math.dist(p,q)<2.8 for q in BENCHES+GROUND+[(35,-22)]):continue
   # Only plant sufficiently inside a terrace to avoid hanging over its rim.
   if h and any(terrain_height((x+dx,z+dz))!=h for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]):continue
   if not h and z<-69:continue
   if math.sin(x*.24)+math.cos(z*.27)<-.45 or rng.random()<.20:continue
   target=flowers if rng.random()<.2 else grass
   target.append((x,h+.03,z,rng.uniform(0.95,1.6) if target is grass else rng.uniform(0.5,0.8),rng.uniform(0,math.pi)))
 quad=sub('QuadMesh','size = Vector2(1,1)')
 for name,asset,points in [('TallGrass','tall-grass',grass),('Flowers','wildflowers',flowers)]:
  tex=g['resource']('res://EXTERNAL/Touma/SafariZone/Frontage/'+asset+'.png','Texture2D');material=sub('StandardMaterial3D',f'transparency = 2\nalpha_scissor_threshold = 0.85\ncull_mode = 2\nalbedo_texture = {tex}\nroughness = 1.0');buffer=[]
  for x,y,z,h,a in points:
   for turn in [0,math.pi/2]:
    c,s=math.cos(a+turn),math.sin(a+turn);buffer.extend([c*.9,0,s,x,0,h,0,y+h/2,-s*.9,0,c,z])
  mm=sub('MultiMesh',f'transform_format = 1\ninstance_count = {len(points)*2}\nmesh = {quad}\nbuffer = PackedFloat32Array('+', '.join(str(round(v,5)) for v in buffer)+')');node(name,'MultiMeshInstance3D',parent,f'multimesh = {mm}\nmaterial_override = {material}')
 leaf=sub('SphereMesh','radius = 0.5\nheight = 1\nradial_segments = 6\nrings = 3');vines=0
 for h,poly in TERRACES:
  for a,b in zip(poly,poly[1:]+poly[:1]):
   # Face strips on exposed south-facing edges.
   if (a[1]+b[1])/2<-88:continue
   for t in [.25,0.65]:
    x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t+.04
    for j in range(int(h*2)):
     y=h-j*.35
     if terrain_height((x,z+.2))>=y:continue
     node('Vine'+str(vines),'MeshInstance3D',parent,f'position = {vec((x+.15*math.sin(j),y,z))}\nscale = Vector3(0.3,0.24,0.08)\nmesh = {leaf}\nmaterial_override = {g["mats"]["leaf"]}');vines+=1
 stats.update(trees=len(trees),rocks=len(BOULDERS),benches=len(BENCHES),landing_rectangles=landing,high_legend_roosts=2,ground_pockets=len(GROUND),grass_cards=len(grass)*2,flower_cards=len(flowers)*2,vine_leaves=vines)
 return stats
