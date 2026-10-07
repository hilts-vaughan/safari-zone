"""Native ten-star forest entrance and a continuous collision-backed natural boundary."""
import math
GATE=(-111,-3)
# Keep the starting-zone boundary and ten-star entrance; leave the lake and
# forest/highlands crossing open instead of building an eastern retaining wall.
WEST=[(-190,-8),(-150,-8),(-130,-5),(-113.5,-3)]
EAST=[(-108.5,-3),(-86,-3),(-58,-4),(-30,-7),(13,-9)]

def distance(p,a,b):
 dx,dz=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dz)/(dx*dx+dz*dz)))
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dz)
def contains(p,margin=0):
 return math.dist(p,GATE)<8+margin or any(distance(p,a,b)<6.5+margin for line in (WEST,EAST+[(17,-31),(8,-55),(0,-77),(0,-135)]) for a,b in zip(line,line[1:]))

def build(g):
 node,sub,vec,box=g['node'],g['sub'],g['vec'],g['box']
 for key,color in [('foresttimber','#ad8459'),('forestcap','#628366'),('forestfoot','#aaa99b')]:g['mats'][key]=g['mat'](color)
 node('ForestCheckpoint','Node3D','.')
 parent='ForestCheckpoint'
 count=0
 ridges=[];plantings=[]
 from sculpted_terrain import build as sculpt
 for line in (WEST,EAST):
  for a,b in zip(line,line[1:]):
   length=math.dist(a,b);angle=math.degrees(math.atan2(-(b[1]-a[1]),b[0]-a[0]))
   n=math.ceil(length/3)
   for i in range(n):
    t=(i+.5)/n;x=a[0]+t*(b[0]-a[0]);z=a[1]+t*(b[1]-a[1]);name=f'FenceBay{count}'
    # Broad overlapping shoulders replace timber except near the gateway and
    # occasional short connectors. Never carve trail holes through this barrier.
    natural=math.dist((x,z),GATE)>13 and count%24 not in (0,1)
    if natural:
     ridges.append((x,z,7.5,7.5,5.5+.8*math.sin(count*.43)))
     if count%5==0:plantings.append((x,z))
     count+=1
     continue
    node(name,'Node3D',parent,f'position = {vec((x,0,z))}\nrotation_degrees = Vector3(0, {angle}, 0)')
    par=parent+'/'+name;width=length/n+.08
    box('Foundation',(0,.17,0),(width,.34,.7),'forestfoot',parent=par)
    box('SolidTimber',(0,1.65,0),(width,2.7,.24),'foresttimber',parent=par)
    box('Cap',(0,3.03,0),(width,.12,.38),'forestcap',parent=par)
    for j in range(math.ceil(width/.3)):
     # Shallow grooves articulate planks; the continuous backing is the collider.
     box('Plank'+str(j),(-width/2+(j+.5)*width/math.ceil(width/.3),1.65,.145),(.025,2.65,.03),'wood',False,parent=par)
    for side in (-1,1):box('Post'+str(side),(side*width/2,1.6,0),(.22,3.2,.38),'foresttimber',parent=par)
    count+=1
 terrain=sculpt(g,'ForestBoundaryRidge',ridges,(-199,26,-144,6),
               spacing=1.5,parent=parent,respect_paths=False,
               allowed=lambda p: math.dist(p,GATE)>10,
               rock_color='#65716f',turf_color='#92b16f')
 # Reuse the boundary's untextured rock/turf palette for articulated faces
 # and supported shelves on its forest-facing side. Gateway remains clear.
 from park_perches import flat
 from map_layout import path_distance
 shelf_count=0
 rock= g['mat']('#65716f'); turf=g['mat']('#92b16f')
 for j,(sx,sz) in enumerate([(-146,-8),(-134,-6),(-94,-3),(-80,-3),(-66,-4),(-50,-5),(-36,-7)]):
  height=10.0 if j<2 else 3.8+(j%3)*.45
  face=sub('CylinderMesh',f'top_radius = 1.0\nbottom_radius = 1.12\nheight = {height}\nradial_segments = 6')
  node('CliffFace'+str(j),'MeshInstance3D',parent,f'position = {vec((sx,height/2,sz-4))}\nscale = Vector3(5.4,1,5)\nmesh = {face}\nmaterial_override = {rock}')
  vertices=[]
  for y,r in [(-height/2,1.12),(height/2,1)]:
   for k in range(6):vertices.extend([r*math.sin(k*math.pi/3),y,r*math.cos(k*math.pi/3)])
  collider=sub('ConvexPolygonShape3D','points = PackedVector3Array('+', '.join(map(str,vertices))+')')
  node('CliffBody'+str(j),'StaticBody3D',parent,f'position = {vec((sx,height/2,sz-4))}\nscale = Vector3(5.4,1,5)\ncollision_layer = 11\ncollision_mask = 0')
  node('Shape','CollisionShape3D',parent+'/CliffBody'+str(j),'shape = '+collider)
  cap=sub('CylinderMesh','top_radius = 1.0\nbottom_radius = 1.0\nheight = 0.10\nradial_segments = 6')
  node('CliffGrassCap'+str(j),'MeshInstance3D',parent,f'position = {vec((sx,height+.025,sz-4))}\nscale = Vector3(5.4,1,5)\nmesh = {cap}\nmaterial_override = {turf}')
  px,pz=sx,sz-10
  if path_distance((px,pz))<3.5:continue
  top=9.6 if j<2 else 3.3+(j%3)*.55
  thickness=4.0 if j<2 else 1.3
  ledge=sub('CylinderMesh',f'top_radius = 1.0\nbottom_radius = 0.40\nheight = {thickness}\nradial_segments = 6')
  node('StoneShelf'+str(j),'MeshInstance3D',parent,f'position = {vec((px,top-thickness/2,pz))}\nscale = Vector3(2.6,1,1.65)\nmesh = {ledge}\nmaterial_override = {rock}')
  node('ShelfGrassCap'+str(j),'MeshInstance3D',parent,f'position = {vec((px,top+.025,pz))}\nscale = Vector3(2.6,1,1.65)\nmesh = {cap}\nmaterial_override = {turf}')
  # Centered rectangle lies wholly within the six-sided ledge's top.
  box('ShelfSolidTop'+str(j),(px,top-.06,pz),(3.2,.12,1.8),'forestfoot',parent=parent)
  flat(g,'CliffShelfLanding'+str(j),(px,top+.085,pz),3.2,1.8)
  shelf_count+=1
 terrain['bird_shelves']=shelf_count
 # Retire ridge trees: their guessed elevation left unsupported trunks above the lake.
 x,z=GATE
 for side in (-1,1):
  box('GateFoot'+str(side),(x+side*2.65,.2,z),(.7,.4,.7),'forestfoot',parent=parent)
  box('GatePost'+str(side),(x+side*2.65,2.05,z),(.42,3.7,.42),'foresttimber',parent=parent)
 box('Lintel',(x,3.65,z),(6.2,.3,.75),'foresttimber',parent=parent)
 from park_perches import flat
 flat(g,'ForestLintelLanding',(x,4.02,z),5.8,.9)
 box('MossRoof',(x,3.9,z),(6.8,.22,1.35),'forestcap',False,parent=parent)
 gate=g['resource']('res://Scenes/FunctionalObjects/BiomeGateSmallFunctional.tscn','PackedScene')
 node('ForestStarGate',None,parent,f'position = {vec((x,0,z))}\n_biomeEnum = {g["bids"]["forest"]}',gate)
 for side in (1,-1):
  box('Sign'+str(side),(x,3.4,z+side*.42),(4.6,.55,.1),'forestcap',False,parent=parent)
  node('Title'+str(side),'Label3D',parent,f'position = {vec((x,3.4,z+side*.49))}\nrotation_degrees = Vector3(0, {0 if side==1 else 180}, 0)\ntext = "NORTHWEST FOREST"\nfont_size = 36\npixel_size = 0.006\noutline_size = 0')
 box('Plaque',(x+3.55,1.4,z+1),(1.5,1.1,.16),'foresttimber',parent=parent)
 node('Requirement','Label3D',parent,f'position = {vec((x+3.55,1.45,z+1.1))}\ntext = "10 STARS"\nfont_size = 38\npixel_size = 0.007\noutline_size = 0')
 from bench_landing_spots import add as bench_landing
 bench_landing(g,'ForestBench',[(x-6,.67,z+4-.45+j*.28,3.6,.22) for j in range(4)],(x-6,1.52,z+4-.65,3.6,.12))
 for j in range(4):box('BenchSeat'+str(j),(x-6,.6,z+4-.45+j*.28),(3.6,.14,.22),'foresttimber',parent=parent)
 for j in range(3):box('BenchBack'+str(j),(x-6,.95+j*.24,z+4-.65),(3.6,.18,.12),'foresttimber',parent=parent)
 g['mats']['forestiron']=g['mat']('#44494b')
 for side in (-1,1):
  box('BenchLeg'+str(side),(x-6+side*1.25,.26,z+4),(.12,.52,.8),'forestiron',parent=parent)
  box('BenchSupport'+str(side),(x-6+side*1.25,.9,z+4-.7),(.12,1.3,.12),'forestiron',parent=parent)
 for i,px in enumerate((x-8,x+8)):
  box('PerchPost'+str(i),(px,1.25,z+5),(.25,2.5,.25),'foresttimber',parent=parent)
  g['prefab']('ForestGatePerch'+str(i),'FunctionalObjects/HopGroundHangout',(px,2.53,z+5),(.5,1,.5))
 for i in range(14):
  px=x-10+i*1.5
  if abs(px-x)<3.5:continue
  g['prefab']('ForestGateFlowers'+str(i),'Decorations/Flowers',(px,.08,z+1.8),(.1,.1,.1))
 for i,(tx,tz) in enumerate([(-103,-10),(-101,-18),(-98,-26),(-96,-34)]):
  if i==3:continue # This trunk occupied the retained hedge at the approach.
  g['prefab']('ForestGateTree'+str(i),'FunctionalObjects/'+('GaryOakTreeAFunctional' if i%2==0 else 'TreeCFunctional'),(tx,0,tz),(1.25,1.25,1.25))
 texture=g['resource']('res://EXTERNAL/Touma/SafariZone/Frontage/tall-grass.png','Texture2D')
 material=sub('StandardMaterial3D',f'transparency = 2\nalpha_scissor_threshold = 0.85\ncull_mode = 2\nalbedo_texture = {texture}\nroughness = 1.0')
 mesh=sub('QuadMesh','size = Vector2(1,1)')
 for bed,(cx,cz) in enumerate([(-119,2),(-103,2),(-98,5),(-101,-25)]+[(tx,tz+8) for tx,tz in plantings]):
  for i in range(7):
   for j in range(4):
    px=cx+(i-3)*.45;pz=cz+(j-1.5)*.45
    for angle in (0,90):
     node(f'TallGrass{bed}_{i}_{j}_{angle}','MeshInstance3D',parent,f'position = {vec((px,.65,pz))}\nrotation_degrees = Vector3(0,{angle+(i*17+j*23)%45},0)\nscale = Vector3(1.15,1.3,1.15)\nmesh = {mesh}\nmaterial_override = {material}')
 return {'gate':GATE,'required_stars':10,'fence_height':3.2,'fence_bays':count,'west':WEST,'east':EAST,'native_gate':True,'natural_ridge':terrain,'ridge_centers':len(ridges)}
