"""Ungated Wetlands Rest with native services and no indoor landing areas."""
CENTER=(38,42)
HALF_WIDTH=10
HALF_DEPTH=9
REQUIRED_STARS=0

def contains(p,margin=0):
 return abs(p[0]-CENTER[0])<HALF_WIDTH+1+margin and abs(p[1]-CENTER[1])<HALF_DEPTH+1+margin

def build(g):
 node,sub,vec,mat,box=[g[n] for n in ['node','sub','vec','mat','box']]
 for key,color in [('gatecream','#e3dac3'),('gategreen','#749263'),('gateroof','#668477'),('gateyellow','#d9bf78'),('gategrout','#c4aa68'),('gateblue','#729baa'),('gatewood','#ac7b4e'),('gatedark','#514b42'),('gatewhite','#fff5dc'),('gatepot','#b8794b')]:g['mats'][key]=mat(color)
 unit=sub('BoxMesh','size = Vector3(1, 1, 1)')
 node('WetlandsGatehouse','Node3D','.',f'position = {vec((CENTER[0],0,CENTER[1]))}')
 parent='WetlandsGatehouse'
 def solid(name,pos,size,m):box('Gate'+name,pos,size,m,parent=parent)
 def detail(name,pos,size,m):
  node('Gate'+name,'MeshInstance3D',parent,f'position = {vec(pos)}\nscale = {vec(size)}\nmesh = {unit}\nmaterial_override = {g["mats"][m]}')
 def caption(name,text,pos,size=.009,ry=0):
  node('Gate'+name,'Label3D',parent,f'position = {vec(pos)}\nrotation_degrees = Vector3(0, {ry}, 0)\ntext = "{text}"\nfont_size = 42\npixel_size = {size}\noutline_size = 0\nmodulate = Color(0.98, 0.96, 0.87, 1)')
 def printface(name,pos,size,asset):
  texture=g['resource']('res://EXTERNAL/Touma/SafariZone/Center/'+asset+'.png','Texture2D')
  material=sub('StandardMaterial3D',f'albedo_texture = {texture}\ncull_mode = 2\nroughness = 0.9')
  mesh=sub('QuadMesh',f'size = Vector2({size[0]}, {size[1]})')
  node('Gate'+name,'MeshInstance3D',parent,f'position = {vec(pos)}\nmesh = {mesh}\nmaterial_override = {material}')
 solid('Floor',(0,.035,0),(20,.07,18),'gateyellow')
 for i in range(21):detail('FloorJointX'+str(i),(-10+i,.073,0),(.025,.004,18),'gategrout')
 for i in range(19):
  for j in range(20):detail(f'FloorJointZ{i}_{j}',(-9.5+j,.073,-9+i),(.975,.004,.025),'gategrout')
 detail('CarpetBorder',(0,.079,1),(9,.008,12),'gatewhite')
 detail('Carpet',(0,.085,1),(8.5,.005,11.5),'gateblue')
 for side in [-1,1]:
  solid('SideWall'+str(side),(side*9.8,2.4,0),(.4,4.8,18),'gatecream')
  # Front facade windows have genuine openings, with shallow glass panes.
  for end,width in [(1,5.6),(-1,4.4)]:
   z=end*8.8
   x=side*(10+width/2)/2;w=10-width/2
   if end==1:
    solid(f'FrontLower{side}',(x,1.25,z),(w,2.5,.4),'gatecream')
    solid(f'FrontUpper{side}',(x,4.15,z),(w,1.3,.4),'gatecream')
    for part in [-1,1]:solid(f'WindowPier{side}_{part}',(x+part*(w/2-.5),3,z),(1,1,.4),'gatecream')
    detail('FrontWindow'+str(side),(x,3,z+.01),(w-2,1,.04),'glass')
   else:solid('RearWall'+str(side),(x,2.4,z),(w,4.8,.4),'gatecream')
   solid(f'DoorHeader{end}_{side}',(side*width/4,4.1,z),(width/2,1.4,.4),'gatecream')
   detail(f'DoorJamb{end}_{side}',(side*(width/2+.1),1.8,z+end*.23),(.25,3.6,.22),'centerroof')
  detail('SideSageBand'+str(side),(side*10.015,1,0),(.025,.65,18),'gategreen')
  detail('IndoorSageBand'+str(side),(side*9.55,1,0),(.025,.55,17.2),'gategreen')
  detail('SideCornice'+str(side),(side*9.52,4.45,0),(.12,.2,17.2),'gategreen')
 solid('Ceiling',(0,4.68,0),(20.8,.2,18.8),'gatecream')
 # Pitched roof, eaves, plank seams: simple geometry consistent with the approved concept.
 roof=sub('PrismMesh','size = Vector3(22.5, 1.6, 20.5)')
 node('GateRoof','MeshInstance3D',parent,f'position = Vector3(0, 5.6, 0)\nmesh = {roof}\nmaterial_override = {g["mats"]["gateroof"]}')
 detail('RoofEaves',(0,4.79,0),(22.5,.02,20.5),'gatecream')
 for side in [-1,1]:
  detail('CeilingLightFrame'+str(side),(side*4.3,4.63,0),(2.5,.12,1.3),'frame')
  detail('CeilingLight'+str(side),(side*4.3,4.55,0),(2.25,.035,1.08),'gatewhite')
 detail('ExteriorSign',(0,4.15,9.13),(6.5,.95,.18),'gategreen')
 caption('ExteriorCaption','WETLANDS REST',(0,4.15,9.24),.009)
 detail('ExitSign',(0,3.95,-8.47),(5.4,.85,.12),'gategreen')
 caption('ExitCaption','WETLANDS',(0,3.95,-8.38),.009)
 for name,x,script in [('PhotoDropOff',-6,'DevelopOTron'),('Shop',6,'ShopInWorld')]:
  service=parent+'/Gate'+name
  g['scriptnode']('Gate'+name,'Node3D','Core/'+script,(x,.07,.4),('rotation_degrees = Vector3(0, 180, 0)\n_biome = '+str(g['bids']['grass'])) if script=='ShopInWorld' else 'rotation_degrees = Vector3(0, 180, 0)',parent=parent)
  node('InteractDistanceVolume','Area3D',service,'position = Vector3(0, 1, -1.7)\ncollision_layer = 0\ncollision_mask = 1\nmonitoring = true')
  shape=sub('BoxShape3D','size = Vector3(4.1, 2.4, 2.2)')
  node('Shape','CollisionShape3D',service+'/InteractDistanceVolume','shape = '+shape)
  box('CounterBase',(0,.65,0),(3.7,1.3,2.3),'gatecream',parent=service)
  box('CounterTop',(0,1.36,0),(4,.2,2.5),'gatewood' if script=='ShopInWorld' else 'gatecream',parent=service)
  if script=='ShopInWorld':
   node('shop','Node3D',service)
   node('Roof','MeshInstance3D',service+'/shop',f'visible = false\nmesh = {unit}\nmaterial_override = {g["mats"]["gatecream"]}')
  detail(name+'Board',(x,1.86,1.05),(2.4,.7,.09),'gatewood')
  caption(name+'Caption','SHOP' if script=='ShopInWorld' else 'PHOTO\\nDROP-OFF',(x,1.87,1.11),.006)
 # Shelf and Pokémon-themed seed packets, reusing the reviewed Center print assets.
 for j in range(2):
  detail('ShopShelf'+str(j),(6,2.6+j*.85,-1.5),(4.1,.12,.7),'gatewood')
  for k in range(4):
   x=4.7+k*.8;y=3+j*.85
   detail(f'Packet{j}_{k}',(x,y,-1.4),(.55,.65,.24),'gategreen' if k%2 else 'gateblue')
   printface(f'PacketLabel{j}_{k}',(x,y,-1.26),(.51,.61),'seed-green' if k%2 else 'seed-blue')
 detail('Printer',(-6.6,2.03,.4),(1.6,1.05,1.15),'gatecream')
 detail('PrinterFace',(-6.6,2.05,1),(1.35,.7,.035),'frame')
 detail('PrinterSlot',(-6.6,1.98,1.025),(1.0,.13,.025),'gatedark')
 detail('PrinterPaper',(-6.6,1.64,1.3),(.65,.05,.65),'gatewhite')
 printface('PhotoSample',(-5.5,1.2,1.61),(.65,.5),'bird-photo')
 detail('Camera',(6.8,1.89,.9),(.85,.6,.38),'gatewhite')
 detail('CameraLens',(6.8,1.89,1.14),(.4,.4,.17),'frame')
 for side in [-1,1]:detail('Binocular'+str(side),(5.2+side*.19,1.84,.9),(.29,.42,.55),'frame')
 for side in [-1,1]:
  x=side*6
  from bench_landing_spots import add as bench_landing
  solid('BenchSeat'+str(side),(x,.6,-5.5),(3.6,.18,.85),'gatewood')
  solid('BenchBack'+str(side),(x,1.12,-5.87),(3.6,.8,.16),'gatewood')
  for leg in [-1,1]:solid(f'BenchLeg{side}_{leg}',(x+leg*1.4,.27,-5.5),(.18,.54,.65),'gatewood')
  # Simple potted foliage assembled from native grass plus thick green leaf shapes.
  for z in [-7,6]:
   solid(f'Pot{side}_{z}',(side*8.1,.43,z),(.75,.86,.75),'gatepot')
   for j in range(4):detail(f'PotLeaf{side}_{z}_{j}',(side*8.1+(j%2-.5)*.38,1.15+j*.12,z),(.65,.18,.55),'plantleaf')
 printface('ReserveMap',(-6,3.2,-8.54),(3.5,2.5),'reserve-map')
 printface('WetlandsPoster',(6,3.2,-8.54),(3.1,2.3),'poster-wildlife')
 bench_landing(g,'GateOutsideBench',[(CENTER[0]+6,.69,CENTER[1]+10.4,3.6,.85)],(CENTER[0]+6,1.525,CENTER[1]+10.7,3.6,.16))
 solid('OutsideBench',(6,.6,10.4),(3.6,.18,.85),'gatewood')
 solid('OutsideBenchBack',(6,1.1,10.7),(3.6,.85,.16),'gatewood')
 for side in [-1,1]:solid('OutsideBenchLeg'+str(side),(6+side*1.3,.27,10.4),(.18,.54,.7),'gatewood')

 # Landscaping repeats the already-reviewed flowering hedge asset.
 hedge=g['resource']('res://EXTERNAL/Touma/SafariZone/Woodland/FloweringHedge.tscn','PackedScene')
 for i,(x,z) in enumerate([(-7,10.5),(-9,13),(9,13),(8,16)]):
  node('GateHedge'+str(i),None,parent,'position = '+vec((x,0,z)),hedge)
 for side in [-1,1]:
  tree=g['resource']('res://Scenes/FunctionalObjects/TreeCFunctional.tscn','PackedScene')
  node('GateTree'+str(side),None,parent,f'position = {vec((side*13,0,13))}\nscale = Vector3(1.7, 1.7, 1.7)',tree)
 detail('MapFrame',(-6,3.2,-8.59),(3.7,2.7,.08),'gatewood')
 detail('PosterFrame',(6,3.2,-8.59),(3.3,2.5,.08),'gatewood')

 # Stock interactive board uses the game's generic photography quest pool.
 g['prefab']('WetlandsQuestBoard','CoreGameplay/QuestBoard',(CENTER[0]-4,0.09,CENTER[1]+12),(1,1,1))
