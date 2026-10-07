"""Small fountain rest beside the forest photo-development clearing."""
import math,random
CENTER=(-81,-49)
BENCHES=[(-87,-55),(-69,-55)]
def contains(p,margin=0):
 if math.dist(p,CENTER)<3.3+margin:return True
 return any(abs(p[0]-x)<2.1+margin and abs(p[1]-z)<1.3+margin for x,z in BENCHES)
def grade_mask(p):
 # Service access is already flat; blend only the furniture foundations.
 d=math.dist(p,CENTER)
 result=max(0,min(1,(d-3.3)/1.4))
 for x,z in BENCHES:
  edge=max(abs(p[0]-x)-2.2,abs(p[1]-z)-1.4)
  result=min(result,max(0,min(1,edge/1.2)))
 return result

def build(g):
 from fountain_garden import fountain
 from bench_landing_spots import add as bench_landing
 from map_layout import layout,path_distance
 from forest_garden import planting
 node,sub,vec,box=[g[k] for k in ['node','sub','vec','box']]
 parent='ForestServiceGarden';node(parent,'Node3D','.')
 fountain(g,parent,CENTER,'ForestService')
 for i,(x,z) in enumerate(BENCHES):
  for j in range(4):box(f'Bench{i}Seat{j}',(x,.60,z-.4+j*.26),(3.4,.14,.22),'plank',parent=parent)
  for j in range(3):box(f'Bench{i}Back{j}',(x,.96+j*.24,z-.66),(3.4,.18,.14),'plank',parent=parent)
  for side in (-1,1):
   box(f'Bench{i}Leg{side}',(x+side*1.15,.29,z),(.17,.58,.85),'iron',parent=parent)
   box(f'Bench{i}Support{side}',(x+side*1.15,.9,z-.72),(.14,1.3,.14),'iron',parent=parent)
  bench_landing(g,f'ForestServiceBench{i}',[(x,.67,z-.4+j*.26,3.4,.22) for j in range(4)],(x,1.53,z-.66,3.4,.14))
 # Islands frame the fountain's back and seat ends; service approach stays bare.
 trunks=[p for p,_,_ in layout()['trees']]+[(x,z) for x,z,_ in planting()[0]]
 rng=random.Random(1052031);grass=[];flowers=[]
 islands=[(-83,-53,1.4,1.2),(-79,-53,1.2,1),(-89.5,-55,1,1.1),(-84.5,-55.2,.8,1),(-71.5,-55.5,.8,1),(-66.5,-55.5,1,1)]
 for cx,cz,rx,rz in islands:
  for ix in range(-5,6):
   for iz in range(-5,6):
    x=cx+ix*.35;z=cz+iz*.35;p=(x,z)
    if ((x-cx)/rx)**2+((z-cz)/rz)**2>1 or contains(p,.25) or path_distance(p)<2.25:continue
    if any(math.dist(p,q)<1 for q in trunks):continue
    if any(math.dist(p,q)<2.8 for q in [(-88,-51),(-72,-51),(-73,-36)]):continue
    target=flowers if rng.random()<.45 else grass
    target.append((x,z,rng.uniform(.85,1.1) if target is grass else rng.uniform(.5,.7),rng.uniform(0,math.pi)))
 quad=sub('QuadMesh','size = Vector2(1,1)')
 for name,asset,points in [('Grass','tall-grass',grass),('Flowers','wildflowers',flowers)]:
  tex=g['resource']('res://EXTERNAL/Touma/SafariZone/Frontage/'+asset+'.png','Texture2D')
  material=sub('StandardMaterial3D',f'transparency = 2\nalpha_scissor_threshold = 0.85\ncull_mode = 2\nalbedo_texture = {tex}\nroughness = 1.0')
  buffer=[]
  for x,z,h,a in points:
   for turn in (0,math.pi/2):
    c,s=math.cos(a+turn),math.sin(a+turn);buffer.extend([c*.85,0,s,x,0,h,0,h/2+.025,-s*.85,0,c,z])
  mm=sub('MultiMesh',f'transform_format = 1\ninstance_count = {len(points)*2}\nmesh = {quad}\nbuffer = PackedFloat32Array('+', '.join(str(round(v,5)) for v in buffer)+')')
  node(name,'MultiMeshInstance3D',parent,f'multimesh = {mm}\nmaterial_override = {material}')
 return {'center':CENTER,'benches':2,'rim_perches':8,'bowl_perches':4,'bench_perches':10,'landing_rectangles':22,'grass_cards':len(grass)*2,'flower_cards':len(flowers)*2}
