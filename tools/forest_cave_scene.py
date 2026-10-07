"""Elevated open forest cave, authored native geometry and generated statue art."""
import math
CAVE_HEIGHT=8.0
# (x,z,height): wide railed stair approach and gentle rear descent.
APPROACH=[(-134,29,0),(-134,20.5,4),(-134,18,4),(-131.5,18,4),(-113.5,18,8),(-111,18,8),(-111,15.5,8),(-111,10,8)]
EXIT=[(-111,-11,8),(-111,-17,8),(-111,-53,0)]

def contains(p,margin=0):
 from forest_gate_scene import distance
 return (-140-margin<p[0]<-94+margin and -14-margin<p[1]<32+margin) or any(distance(p,a[:2],b[:2])<4+margin for a,b in zip(EXIT,EXIT[1:]))

def build(g,parent='ForestCheckpoint'):
 node,sub,vec,box,mat=[g[k] for k in ('node','sub','vec','box','mat')]
 for key,color in [('caverock','#596b70'),('cavemoss','#8faa70'),('cavepath','#ded4ad'),('cavewood','#a78055'),('cavegold','#f6d494')]:g['mats'][key]=mat(color)
 node('ElevatedCave','Node3D',parent);par=parent+'/ElevatedCave'
 def block(name,p,s,key='caverock',solid=True):box(name,p,s,key,solid,parent=par)
 def prism(name,points,top,depth,key='caverock'):
  polygon=', '.join(str(v) for p in points for v in p)
  node(name,'CSGPolygon3D',par,f'position = Vector3(0,{top-depth},0)\nrotation_degrees = Vector3(90,0,0)\npolygon = PackedVector2Array({polygon})\ndepth = {depth}\nmaterial = {g["mats"][key]}\nuse_collision = true\ncollision_layer = 11\ncollision_mask = 0')
 # Broad solid lower escarpment beneath the high entrance: no ground tunnel.
 prism('LowerEscarpment',[(-131,11),(-127,15),(-118,13),(-104,13),(-96,10),(-95,-12),(-130,-14)],7.8,7.8)
 block('CaveFloor',(-111,7.88,-1),(25,.26,23),'cavepath')
 prism('WestCliff',[(-132,12),(-127,14),(-123,11),(-122,3),(-124,-12),(-133,-14)],16,16)
 prism('EastCliff',[(-101,12),(-96,14),(-92,10),(-93,-13),(-100,-14),(-100,3)],17,17)
 # Entrance arch is an actual opening with broad faceted shoulders and roof.
 prism('EntranceWest',[(-125,12),(-116,12),(-116,9),(-124,8)],13,5)
 prism('EntranceEast',[(-106,12),(-98,11),(-98,8),(-106,9)],13,5)
 block('EntranceLintel',(-111,13.2,10.5),(11,2.4,3))
 block('RoofWest',(-120,14,-1),(8,2,22))
 block('RoofEast',(-102,14,-1),(8,2,22))
 block('RoofRear',(-111,14,-8),(12,2,8))
 block('RoofFront',(-111,14,5),(12,2,6))
 # Broad sloping facets form the interior vault rather than a rectangular room.
 cross=[(-10,0),(-9,3),(-7,5),(-5,6),(5,6),(7,5),(9,3),(10,0)]
 triangles=[]
 for i in range(len(cross)-1):
  if i==3:continue # central skylight
  x1,y1=cross[i];x2,y2=cross[i+1]
  a=(-111+x1,8+y1,-10);b=(-111+x2,8+y2,-10);c=(-111+x2,8+y2,9);d=(-111+x1,8+y1,9)
  triangles.extend([(a,b,c),(a,c,d)])
 lines=[]
 for tri in triangles:
  for v in tri:lines.append('v '+' '.join(map(str,v)))
 for i in range(len(triangles)):lines.append('f '+' '.join(str(i*3+j+1) for j in range(3)))
 asset=g['ROOT']/'assets/environment/cave/vault.obj';asset.write_text('\n'.join(lines)+'\n')
 target=g['ROOT']/'editor/SceneEditor/EXTERNAL/Touma/SafariZone/Cave/vault.obj';target.write_text(asset.read_text())
 vault=g['resource']('res://EXTERNAL/Touma/SafariZone/Cave/vault.obj','Mesh')
 vaultmat=sub('StandardMaterial3D','albedo_color = Color(0.28,0.34,0.36,1)\ncull_mode = 2\nroughness = 1.0')
 node('FacetedVault','MeshInstance3D',par,'mesh = '+vault+'\nmaterial_override = '+vaultmat)
 for i,(x,z) in enumerate([(-122,-5),(-122,4),(-100,-4),(-100,5)]):
  prism('InteriorRock'+str(i),[(x-.8,z-1.5),(x+1,z-1),(x+1.5,z+1),(x-.5,z+1.8)],9.1,1.1)
  g['prefab']('CaveMossFlowers'+str(i),'Decorations/Flowers',(x,9.15,z),(.13,.13,.13))
 # Small skylight left open at center, safely above the player's walking space.
 block('RearWest',(-120,10.7,-11),(8,5.4,2))
 block('RearEast',(-102,10.7,-11),(8,5.4,2))
 block('RearLintel',(-111,13,-11),(12,2,2))
 for i,(x,z,y,w,d) in enumerate([(-128,11,16,8,8),(-96,4,17,8,18),(-119,-6,15,8,10),(-103,-6,15,8,10)]):
  block('GrassCap'+str(i),(x,y+.08,z),(w,.16,d),'cavemoss',False)
 def beam(name,a,b,width,height,key='cavewood',solid=True):
  dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
  node(name,'Node3D',par,f'position = {vec(((a[0]+b[0])/2,(a[2]+b[2])/2,(a[1]+b[1])/2))}\nrotation_degrees = Vector3({-math.degrees(math.atan2(b[2]-a[2],length))},{math.degrees(math.atan2(dx,dz))},0)')
  box('Beam',(0,0,0),(width,height,math.dist(a,b)+.1),key,solid,parent=par+'/'+name)
 routes=list(zip(APPROACH,APPROACH[1:]))+list(zip(EXIT,EXIT[1:]))
 for i,(a,b) in enumerate(routes):
  beam('WalkSurface'+str(i),(a[0],a[1],a[2]-.15),(b[0],b[1],b[2]-.15),4,.3)
  dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz);nx,nz=dz/length,-dx/length
  for side in (-1,1):
   # Leave clear turning landings rather than crossing the next stair flight.
   inset=min(2.4,length*.45)
   for rise in (.55,1.1):
    aa=(a[0]+dx*inset/length+nx*side*2.1,a[1]+dz*inset/length+nz*side*2.1,a[2]+(b[2]-a[2])*inset/length+rise)
    bb=(b[0]-dx*inset/length+nx*side*2.1,b[1]-dz*inset/length+nz*side*2.1,b[2]-(b[2]-a[2])*inset/length+rise)
    beam(f'Rail{i}_{side}_{rise}',aa,bb,.13,.13)
   for j in range(math.ceil(length/3)+1):
    t=j/math.ceil(length/3)
    if t*length<2.4 or (1-t)*length<2.4:continue
    x,z,y=a[0]+dx*t,a[1]+dz*t,a[2]+(b[2]-a[2])*t
    block(f'Post{i}_{side}_{j}',(x+nx*side*2.1,y+.6,z+nz*side*2.1),(.2,1.2,.2),'cavewood')
  # Stair treads remain visual over continuous slope collision, avoiding snags.
  if i<len(APPROACH)-1 and b[2]!=a[2]:
   n=math.ceil(length/.45)
   for j in range(n):
    t=(j+.5)/n;y=a[2]+(b[2]-a[2])*(j+1)/n
    beam(f'Tread{i}_{j}',(a[0]+dx*t-nx*1.95,a[1]+dz*t-nz*1.95,y),(a[0]+dx*t+nx*1.95,a[1]+dz*t+nz*1.95,y),length/n+.02,.1,solid=False)
 for i,(x,z,y) in enumerate([(-134,18,4),(-111,18,8)]):block('Landing'+str(i),(x,y-.15,z),(4.3,.3,4.3),'cavewood')
 # Statue stays outside the four-metre-wide central walking lane.
 prism('StatuePlinth',[(-107,-4),(-104,-4.2),(-102.8,-3),(-103,-.5),(-104.5,.2),(-107,-.5)],9.1,1.1)
 texture=g['resource']('res://EXTERNAL/Touma/SafariZone/Cave/bellsprout-statue.png','Texture2D')
 material=sub('StandardMaterial3D',f'transparency = 2\nalpha_scissor_threshold = 0.7\ncull_mode = 2\nalbedo_texture = {texture}\nroughness = 1.0\nbillboard_mode = 2')
 mesh=sub('QuadMesh','size = Vector2(2.8,4.2)')
 node('BellsproutStatue','MeshInstance3D',par,f'position = {vec((-105,10.95,-2))}\nmesh = {mesh}\nmaterial_override = {material}')
 block('BenchSeat',(-118.5,8.6,1),(3,.18,.9),'cavewood')
 block('BenchBack',(-118.5,9.2,.6),(3,1,.14),'cavewood')
 for i,x in enumerate((-119.5,-117.5)):block('BenchLeg'+str(i),(x,8.3,1),(.18,.6,.6),'cavewood')
 g['mats']['cavegold']=sub('StandardMaterial3D','albedo_color = Color(1,0.78,0.4,1)\nemission_enabled = true\nemission = Color(1,0.6,0.2,1)\nemission_energy_multiplier = 1.5')
 for i,(x,z) in enumerate([(-116,10),(-106,10),(-117,-9.8),(-105,-9.8)]):
  block('LanternFrame'+str(i),(x,10.2,z),(.35,.65,.35),'cavewood',False)
  block('LanternLight'+str(i),(x,10.2,z+.2),(.22,.44,.1),'cavegold',False)
  node('LanternGlow'+str(i),'OmniLight3D',par,f'position = {vec((x,10.2,z+1))}\nlight_color = Color(1,0.78,0.46,1)\nlight_energy = 0.55\nomni_range = 7\nshadow_enabled = false')
 node('CaveSign','Label3D',par,f'position = {vec((-135,2,29))}\ntext = "FOREST CAVE"\nfont_size = 42\npixel_size = 0.008\noutline_size = 0')
 for i,(px,pz) in enumerate([(-118,5),(-117,-6),(-104,4),(-103,-6),(-119,-7),(-102,-7)]):
  g['prefab']('CaveInteriorPlant'+str(i),'Decorations/Flowers',(px,8.1,pz),(.2,.2,.2))
 g['prefab']('CaveFlowersInteriorA','Decorations/Flowers',(-119,8.1,-4),(.14,.14,.14))
 g['prefab']('CaveFlowersInteriorB','Decorations/Flowers',(-102,8.1,2),(.14,.14,.14))
 grass_texture=g['resource']('res://EXTERNAL/Touma/SafariZone/Frontage/tall-grass.png','Texture2D')
 grass_mat=sub('StandardMaterial3D',f'transparency = 2\nalpha_scissor_threshold = 0.85\ncull_mode = 2\nalbedo_texture = {grass_texture}\nroughness = 1')
 grass_mesh=sub('QuadMesh','size = Vector2(1,1)')
 for bed,(cx,cz) in enumerate([(-118,4),(-117,-6),(-103,4),(-104,-7)]):
  for j in range(9):
   px=cx+(j%3-1)*.45;pz=cz+(j//3-1)*.45
   for angle in (0,90):node(f'CaveGrass{bed}_{j}_{angle}','MeshInstance3D',par,f'position = {vec((px,8.5,pz))}\nrotation_degrees = Vector3(0,{angle},0)\nmesh = {grass_mesh}\nmaterial_override = {grass_mat}')
 node('ForestExitSign','Label3D',par,f'position = {vec((-111,11.4,-9.8))}\ntext = "NORTHWEST FOREST"\nfont_size = 36\npixel_size = 0.008\noutline_size = 0')
 for i,(x,z,y) in enumerate([(-128,8,16.2),(-95,5,17.2),(-120,-5,15.2),(-104,-5,15.2)]):
  g['prefab']('CaveSkylineTree'+str(i),'FunctionalObjects/TreeCFunctional',(x,y,z),(1.1,1.1,1.1))
 for i,(x,z) in enumerate([(-127,18),(-120,16),(-101,15),(-94,16),(-138,22)]):
  g['prefab']('CaveFlowers'+str(i),'Decorations/Flowers',(x,.08,z),(.16,.16,.16))
 for i,(x,z,y) in enumerate([(-138,27,0),(-120,15,8),(-120,3,8)]):
  block('PerchPost'+str(i),(x,y+1.2,z),(.23,2.4,.23),'cavewood')
  g['prefab']('CavePerch'+str(i),'FunctionalObjects/HopGroundHangout',(x,y+2.45,z),(.6,1,.6))
 return {'height_m':8,'approach':APPROACH,'exit':EXIT,'gate':False,'statue':'Imagegen cutout on stone plinth'}
