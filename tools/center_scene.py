"""Approved playable Center, built as native 3D geometry and simple surface detail."""
import math
from map_layout import WAYPOINTS
CENTER=(-70,72)
SPAWN=(-70, 69)
DOOR_WIDTH=5.2

def build(g):
 node,sub,vec,mat,box,prefab,scriptnode=[g[n] for n in ['node','sub','vec','mat','box','prefab','scriptnode']]
 mats=g['mats'];cx,cz=CENTER
 for k,c in [('centerwall','#ddd2bb'),('centerroof','#cd5a48'),('roofseam','#a74738'),('glass','#71b7cb'),('glasslight','#a6d3dc'),('frame','#59696d'),('paver','#d1d2c8'),('grout','#b3b8ae'),('foundation','#a8ada6'),('plank','#a9794f'),('plankgrain','#906643'),('iron','#555e57'),('emblemwhite','#faf7e8'),('emblemblack','#4b4b45'),('mapgreen','#9abd75'),('mapwater','#63a7bb')]:mats[k]=mat(c)
 for k,c in [('tilewarm','#c5bdae'),('tilelight','#d7d1c5'),('wallbase','#b0a897'),('countercream','#e5dcc6'),('plantleaf','#548448'),('pot','#be794b')]:mats[k]=mat(c)
 unit=sub('BoxMesh','size = Vector3(1, 1, 1)')
 def detail(name,p,size,m,rx=0,ry=0,rz=0):
  node(name,'MeshInstance3D','.',f'position = {vec(p)}\nscale = {vec(size)}\nrotation_degrees = {vec((rx,ry,rz))}\nmesh = {unit}\nmaterial_override = {mats[m]}')
 # Continuous flat forecourt; joints have no collision lip.
 box('CenterForecourt',(cx,.035,85),(29,.07,12),'paver')
 for i in range(10):detail('PavingJointX'+str(i),(cx-14.5+i*3,.073,85),(.035,.005,12),'grout')
 for i in range(5):detail('PavingJointZ'+str(i),(cx,.074,79+i*3),(29,.005,.035),'grout')
 # Hollow shell: floor flush with the courtyard and a real five-meter doorway.
 box('CenterFloor',(cx,.035,cz),(22,.07,10),'paver')
 box('CenterBackWall',(cx,2.6,cz-4.8),(22,5.1,.4),'centerwall')
 for side in [-1,1]:
  box('CenterSideWall'+str(side),(cx+side*10.8,2.6,cz),(.4,5.1,10),'centerwall')
  box('CenterFrontWall'+str(side),(cx+side*6.8,2.6,cz+4.8),(8.4,5.1,.4),'centerwall')
 box('CenterDoorHeader',(cx,4.65,cz+4.8),(DOOR_WIDTH,1,.4),'centerwall')
 box('CenterCeiling',(cx,5.17,cz),(21.2,.16,9.2),'centerwall')
 for i in range(11):detail('IndoorJointX'+str(i),(cx-10+i*2,.076,cz),(.025,.005,9.2),'grout')
 for i in range(5):detail('IndoorJointZ'+str(i),(cx,.076,cz-4+i*2),(21.2,.005,.025),'grout')
 # Facade joints stop at the opening; sliding glass leaves are parked beside it.
 for side in [-1,1]:
  for i,y in enumerate([1.35,2.55,3.75,4.95]):
   detail(f'FacadeCourse{side}_{i}',(cx+side*6.8,y,cz+5.012),(8.4,.024,.018),'grout')
   detail(f'SideCourse{side}_{i}',(cx+side*11.012,y,cz),(.02,.024,10),'grout')
  detail('DoorJamb'+str(side),(cx+side*2.72,2.08,cz+5.06),(.24,4.16,.18),'centerroof')
  detail('OpenDoorFrame'+str(side),(cx+side*3.75,2.05,cz+5.18),(2.05,3.96,.14),'frame')
  detail('OpenDoorGlass'+str(side),(cx+side*3.75,2.05,cz+5.27),(1.87,3.78,.06),'glass')
  detail('DoorHandle'+str(side),(cx+side*2.99,1.65,cz+5.32),(.06,.55,.045),'emblemwhite')
  x=cx+side*7.6
  detail('WindowFrame'+str(side),(x,2.65,cz+5.065),(3.1,2.35,.12),'frame')
  detail('WindowGlass'+str(side),(x,2.65,cz+5.14),(2.85,2.1,.065),'glass')
  detail('WindowGlint'+str(side),(x-.35,2.65,cz+5.181),(.15,1.9,.015),'glasslight',rz=-35)
 detail('DoorTrack',(cx,4.17,cz+5.16),(10,.18,.22),'frame')
 for side in [-1,1]:
  detail('InteriorCornice'+str(side),(cx+side*10.54,4.85,cz),(.1,.25,9.2),'centerroof')
 detail('InteriorFrontTrim',(cx,4.85,cz+4.55),(21.2,.25,.1),'centerroof')
 detail('InteriorBackTrim',(cx,4.85,cz-4.55),(21.2,.25,.1),'centerroof')
 # Detail the room as in the approved concept, with furnishings in the spawn view.
 for i in range(11):
  for j in range(5):detail(f'FloorTile{i}_{j}',(cx-10+i*2,.076,cz-4+j*2),(1.97,.006,1.97),'tilewarm' if (i+j)%3==0 else 'tilelight')
 for i in range(11):detail('CeilingJointX'+str(i),(cx-10+i*2,5.075,cz),(.025,.01,9.2),'grout')
 for j in range(5):detail('CeilingJointZ'+str(j),(cx,5.075,cz-4+j*2),(21.2,.01,.025),'grout')
 for side in [-1,1]:
  detail('FrontWainscot'+str(side),(cx+side*6.8,.62,cz+4.57),(8.4,1.1,.08),'wallbase')
  detail('SideWainscot'+str(side),(cx+side*10.55,.62,cz),(.08,1.1,9.2),'wallbase')
  detail('InteriorWindowFrame'+str(side),(cx+side*6.9,2.8,cz+4.53),(2.25,2.35,.16),'frame')
  detail('InteriorWindowGlass'+str(side),(cx+side*6.9,2.8,cz+4.42),(1.98,2.08,.06),'glass')
  detail('InteriorWindowGlint'+str(side),(cx+side*6.9-.4,2.8,cz+4.37),(.15,1.8,.025),'glasslight',rz=-30)
  detail('InnerDoorJamb'+str(side),(cx+side*2.75,2.05,cz+4.48),(.3,4.1,.26),'centerroof')
  detail('InnerParkedFrame'+str(side),(cx+side*3.75,2.05,cz+4.42),(1.8,3.85,.15),'frame')
  detail('InnerParkedGlass'+str(side),(cx+side*3.75,2.05,cz+4.31),(1.55,3.6,.065),'glass')
  detail('InnerDoorHandle'+str(side),(cx+side*3.04,1.65,cz+4.25),(.07,.6,.04),'emblemwhite')
 detail('InnerDoorHeader',(cx,4.2,cz+4.45),(5.8,.42,.28),'centerroof')
 # Imagegen illustrations on physical print surfaces; stock gameplay remains native.
 def printface(name,pos,size,asset,ry=180,rx=0):
  tex=g['resource']('res://EXTERNAL/Touma/SafariZone/Center/'+asset+'.png','Texture2D')
  material=sub('StandardMaterial3D',f'albedo_texture = {tex}\nroughness = 0.9\ncull_mode = 2')
  mesh=sub('QuadMesh',f'size = Vector2({size[0]}, {size[1]})')
  node(name,'MeshInstance3D','.',f'position = {vec(pos)}\nrotation_degrees = {vec((rx,ry,0))}\nmesh = {mesh}\nmaterial_override = {material}')
 def caption(name,text,pos,size=.008,ry=180):
  node(name,'Label3D','.',f'position = {vec(pos)}\nrotation_degrees = Vector3(0, {ry}, 0)\ntext = "{text}"\nfont_size = 44\npixel_size = {size}\noutline_size = 0\nmodulate = Color(0.98, 0.96, 0.89, 1)')
 def service(name,x,script,biome_id=None):
  scriptnode(name,'Node3D','Core/'+script,(x,.07,cz+1),f'_biome = {biome_id}' if biome_id else '')
  node('InteractDistanceVolume','Area3D',name,'position = Vector3(0, 1, -1.7)\ncollision_layer = 0\ncollision_mask = 1\nmonitoring = true')
  shape=sub('BoxShape3D','size = Vector3(4.1, 2.4, 2.2)')
  node('Shape','CollisionShape3D',name+'/InteractDistanceVolume','shape = '+shape)
  box('CounterBase',(0,.65,0),(3.7,1.3,2.3),'countercream',parent=name)
  box('CounterFoot',(0,.17,-.015),(3.78,.26,2.35),'centerroof',parent=name)
  box('CounterTop',(0,1.36,0),(3.96,.2,2.5),'plank' if script=='ShopInWorld' else 'countercream',parent=name)
  detail(name+'FrontPanel',(x,.77,cz-.16),(3.45,.88,.035),'emblemwhite')
  for i in range(4):detail(name+'WoodGrain'+str(i),(x,1.535,cz+.08+i*.52),(3.75,.005,.018),'plankgrain' if script=='ShopInWorld' else 'grout')
  return name
 shop=service('CenterShop',cx+5,'ShopInWorld',g['bids']['grass'])
 node('shop','Node3D',shop)
 node('Roof','MeshInstance3D',shop+'/shop',f'visible = false\nmesh = {unit}\nmaterial_override = {mats["centerwall"]}')
 # Broad wooden display shelving behind the left counter, facing the player.
 sx,sz=cx+5,cz+3.5
 box('ShopShelfBack',(sx,2.15,sz),(4.15,3.65,.16),'plankgrain')
 for side in [-1,1]:box('ShopShelfSide'+str(side),(sx+side*2.08,2.15,sz-.27),(.16,3.65,.7),'plank')
 for j in range(4):box('ShopShelfBoard'+str(j),(sx,.45+j*.92,sz-.25),(4.3,.14,.8),'plank')
 box('ShopShelfDivider',(sx+.6,2.15,sz-.25),(.14,3.4,.8),'plank')
 for j in range(3):
  for k in range(5):
   x=sx-1.6+k*.7;y=.88+j*.92
   box(f'SeedPacket{j}_{k}',(x,y,sz-.35),(.53,.7,.28),'mapgreen' if k%2==0 else 'glass')
   printface(f'SeedLabel{j}_{k}',(x,y,sz-.499),(.49,.64),'seed-green' if k%2==0 else 'seed-blue')
 detail('ShopSignBoard',(sx,4.04,sz-.68),(4.7,.78,.18),'centerroof');caption('ShopCaption','SHOP',(sx,4.04,sz-.785),.01)
 # Cylinders give camera lenses and binoculars a recognizable silhouette.
 def cylinder(name,pos,radius,height,m,rx=90):
  mesh=sub('CylinderMesh',f'top_radius = {radius}\nbottom_radius = {radius}\nheight = {height}\nradial_segments = 16')
  node(name,'MeshInstance3D','.',f'position = {vec(pos)}\nrotation_degrees = Vector3({rx}, 0, 0)\nmesh = {mesh}\nmaterial_override = {mats[m]}')
 for setno,(x,z,y) in enumerate([(sx-1,cz+.8,1.82),(sx+1,sz-.4,2.14)]):
  for side in [-1,1]:
   cylinder(f'BinocularBarrel{setno}_{side}',(x+side*.19,y,z),.17,.6,'frame')
   cylinder(f'BinocularRim{setno}_{side}',(x+side*.19,y,z-.32),.18,.055,'iron')
   cylinder(f'BinocularLens{setno}_{side}',(x+side*.19,y,z-.353),.13,.015,'glass')
  detail('BinocularBridge'+str(setno),(x,y,z),(.45,.12,.2),'frame')
 detail('DisplayCamera',(sx+.75,1.87,cz+.9),(.82,.6,.35),'emblemwhite')
 detail('DisplayCameraTop',(sx+.75,2.2,cz+.9),(.35,.1,.25),'frame')
 cylinder('CameraLensRim',(sx+.75,1.87,cz+.65),.25,.23,'frame');cylinder('CameraLens',(sx+.75,1.87,cz+.52),.18,.02,'glass')
 printface('CounterSeedDisplay',(sx,1.94,cz+.15),(.65,.75),'seed-blue')
 # Cream development printer, dark inset opening, buttons, photo emerging and tray.
 px,pz=cx-5,cz+1
 service('CenterPhotoDropOff',px,'DevelopOTron')
 box('PhotoMachine',(px+.5,2.04,pz+.12),(1.85,1.06,1.25),'countercream')
 detail('PrinterFrontPanel',(px+.5,2,pz-.525),(1.6,.75,.035),'frame')
 detail('PrinterSlot',(px+.5,1.96,pz-.553),(1.16,.14,.025),'emblemblack')
 detail('PrinterButton',(px+1.17,2.44,pz-.56),(.16,.08,.03),'mapgreen')
 detail('PrinterStatus',(px-.13,2.44,pz-.56),(.24,.07,.03),'grout')
 detail('PrinterPaper',(px+.5,1.75,pz-.66),(.7,.65,.05),'emblemwhite',rx=-30)
 printface('PrinterPhoto',(px+.5,1.725,pz-.706),(.56,.47),'bird-photo',rx=-30)
 box('PhotoTray',(px-.9,1.61,pz-.05),(1.0,.16,.75),'plank')
 for j in range(3):
  detail('TrayPrintBacking'+str(j),(px-1.2+j*.28,1.87,pz-.13+j*.03),(.35,.44,.04),'emblemwhite')
  printface('TrayBirdPhoto'+str(j),(px-1.2+j*.28,1.89,pz-.16+j*.03),(.28,.3),'bird-photo' if j%2==0 else 'seed-green')
 detail('PhotoWallSign',(cx-10.5,3.3,cz+1.4),(3.0,1.25,.12),'plantleaf',ry=90);caption('PhotoCaption','PHOTO\\nDROP-OFF',(cx-10.425,3.3,cz+1.4),.009,ry=90)
 from bench_landing_spots import add as bench_landing
 # A visible right-side waiting bench beneath the framed reserve map.
 bx,bz=cx-3.9,cz+3.7
 for j in range(4):box('IndoorBenchSeat'+str(j),(bx,.6,bz-.42+j*.24),(2.1,.12,.19),'plank')
 for j in range(3):box('IndoorBenchBack'+str(j),(bx,.98+j*.22,bz+.55),(2.1,.16,.12),'plank')
 for side in [-1,1]:box('IndoorBenchLeg'+str(side),(bx+side*.8,.3,bz),(.14,.6,.75),'iron')
 bench_landing(g,'IndoorBench',[(bx,.66,bz-.42+j*.24,2.1,.19) for j in range(4)],(bx,1.50,bz+.55,2.1,.12))
 detail('InteriorMapFrame',(cx,2.8,cz-4.46),(4.1,3.05,.14),'plank')
 printface('InteriorMap',(cx,2.8,cz-4.375),(3.86,2.81),'reserve-map',ry=0)
 for side,asset in [(-1,'poster-wildlife'),(1,'poster-wildlife')]:
  x=cx+side*4.25
  detail('RearPosterFrame'+str(side),(x,2.8,cz-4.46),(2.65,2.65,.14),'plank')
  printface('RearPoster'+str(side),(x,2.8,cz-4.375),(2.43,2.43),asset,ry=0)
 # Potted plants with thick leaves; simple real 3D, not billboard foliage.
 def plant(name,x,z,y=0,scale=1):
  cylinder(name+'Pot',(x,y+.35*scale,z),.38*scale,.65*scale,'pot',rx=0)
  cylinder(name+'Soil',(x,y+.685*scale,z),.32*scale,.025,'soil',rx=0)
  cylinder(name+'Stem',(x,y+1.1*scale,z),.045*scale,.85*scale,'plantleaf',rx=0)
  for i in range(7):
   angle=i*math.pi*2/7
   mesh=sub('SphereMesh',f'radius = {0.25*scale}\nheight = {0.5*scale}\nradial_segments = 12\nrings = 6')
   node(name+'Leaf'+str(i),'MeshInstance3D','.',f'position = {vec((x+math.cos(angle)*.28*scale,y+(1+i%3*.22)*scale,z+math.sin(angle)*.28*scale))}\nscale = Vector3(1, 0.35, 1.9)\nrotation_degrees = Vector3(0, {i*360/7}, 25)\nmesh = {mesh}\nmaterial_override = {mats["plantleaf"]}')
 plant('DoorPlant',cx+3.6,cz+2.5,scale=.8)
 plant('PhotoPlant',cx-6.8,cz+3.65,scale=.8)
 plant('ShelfPlant',sx+1.7,sz-.2,y=3.3,scale=.45)
 for i,x in enumerate([-5,5]):
  for j,z in enumerate([-2,2]):
   detail(f'CeilingLampFrame{i}_{j}',(cx+x,5.03,cz+z),(2.6,.12,1.4),'frame')
   detail(f'CeilingLamp{i}_{j}',(cx+x,4.956,cz+z),(2.32,.035,1.12),'emblemwhite')
 # Two sloped roof panels, tile rows and restrained vertical seams.
 angle=math.degrees(math.atan2(3,6))
 for side in [-1,1]:
  detail('CenterRoof'+str(side),(cx,6.85,cz+side*3),(24,.42,6.75),'centerroof',rx=side*angle)
  for row in range(4):
   dz=.7+row*1.5;y=8.55-dz*.5
   detail(f'RoofCourse{side}_{row}',(cx,y,cz+side*dz),(24,.025,.045),'roofseam',rx=side*angle)
  for col in range(9):detail(f'RoofTile{side}_{col}',(cx-11+col*2.75,7.05,cz+side*3),(.04,.025,6.75),'roofseam',rx=side*angle)
 detail('CenterFascia',(cx,5.35,cz+6.02),(24,.6,.24),'centerroof')
 detail('CenterRidge',(cx,8.45,cz),(24,.15,.2),'centerroof')
 # Raised circular emblem, with real depth instead of a billboard.
 def disc(name,x,y,z,r,m):
  mesh=sub('CylinderMesh',f'top_radius = {r}\nbottom_radius = {r}\nheight = 0.07\nradial_segments = 48')
  node(name,'MeshInstance3D','.',f'position = {vec((x,y,z))}\nrotation_degrees = Vector3(90, 0, 0)\nmesh = {mesh}\nmaterial_override = {mats[m]}')
 ez=cz+6.22;ey=5.25
 disc('EmblemBacking',cx,ey,ez,1.16,'emblemwhite');disc('EmblemRim',cx,ey,ez+.06,1.02,'emblemblack');disc('EmblemFace',cx,ey,ez+.12,.94,'emblemwhite')
 pts=[(.94*math.cos(i*math.pi/24),.94*math.sin(i*math.pi/24)) for i in range(25)]
 polygon=', '.join(str(round(v,5)) for p in pts for v in p)
 node('EmblemRedHalf','CSGPolygon3D','.',f'position = {vec((cx,ey,ez+.17))}\npolygon = PackedVector2Array({polygon})\ndepth = 0.02\nmaterial = {mats["centerroof"]}')
 detail('EmblemStripe',(cx,ey,ez+.2),(1.87,.12,.025),'emblemblack');disc('EmblemButtonRim',cx,ey,ez+.24,.32,'emblemblack');disc('EmblemButton',cx,ey,ez+.3,.23,'emblemwhite')
 # Benches: slatted wood, metal legs and solid seats/backrests.
 for side in [-1,1]:
  x=cx+side*11.6;z=83.2
  for j in range(4):box(f'BenchSeat{side}_{j}',(x,.6,z-.45+j*.28),(4.3,.14,.22),'plank')
  for j in range(3):box(f'BenchBack{side}_{j}',(x,.95+j*.24,z-.65),(4.3,.18,.12),'plank')
  for end in [-1,1]:
   box(f'BenchLeg{side}_{end}',(x+end*1.55,.26,z),( .12,.52,.8),'iron')
   box(f'BenchSupport{side}_{end}',(x+end*1.55,.9,z-.7),(.12,1.3,.12),'iron')
  bench_landing(g,'CenterBench'+str(side),[(x,.677,z-.45+j*.28,4.3,.22) for j in range(4)],(x,1.52,z-.65,4.3,.12))
  for j in range(4):detail(f'BenchGrain{side}_{j}',(x,.677,z-.45+j*.28),(4.1,.002,.018),'plankgrain')
 # Low planters frame the seating, keeping the center route open.
 for side in [-1,1]:
  x=cx+side*16;z=81.2
  box('Planter'+str(side),(x,.35,z),(2.8,.7,4.2),'foundation')
  detail('PlanterSoil'+str(side),(x,.715,z),(2.5,.035,3.9),'soil')
  for j in range(5):prefab(f'CenterFlowers{side}_{j}','Decorations/Flowers',(x,.95,z-1.45+j*.7),(.07,.07,.07))
 from park_perches import flat
 # Illustrated reserve map, shared with the indoor maps; outdoor location overlay.
 bx,bz=cx+16.7,84
 for side in [-1,1]:box('MapPost'+str(side),(bx+side*1.6,1.6,bz),(.22,3.2,.25),'plank')
 detail('MapBoard',(bx,2.45,bz),(3.8,2.8,.2),'plank');detail('MapInset',(bx,2.45,bz+.115),(3.35,2.35,.025),'mapgreen')
 printface('OutdoorReserveMap',(bx,2.45,bz+.15),(3.35,2.35),'reserve-map',ry=0)
 node('MapLocation','Label3D','.',f'position = {vec((bx-.875,1.478,bz+.18))}\ntext = "●"\nfont_size = 48\npixel_size = 0.0025\noutline_size = 4\nmodulate = Color(0.85, 0.16, 0.12, 1)')
 node('MapLocationCaption','Label3D','.',f'position = {vec((bx-.875,1.35,bz+.18))}\ntext = "YOU ARE HERE"\nfont_size = 28\npixel_size = 0.0016\noutline_size = 3')
 flat(g,'ReserveMapLanding',(bx,3.86,bz),3.4,.15)
 node('MapCaption','Label3D','.',f'position = {vec((bx,3.95,bz+.05))}\ntext = "SAFARI ZONE"\nfont_size = 36\npixel_size = 0.006\noutline_size = 3')
 # Small, fixed entrance sign; giant floating welcome text and arch are removed.
 sx,sz=cx-19.5,89
 box('ReserveSignPost',(sx,.95,sz),(.18,1.9,.18),'plank');detail('ReserveSign',(sx,1.6,sz),(3.2,.85,.15),'plank')
 flat(g,'ReserveSignLanding',(sx,2.035,sz),2.8,.10)
 node('ReserveSignText','Label3D','.',f'position = {vec((sx,1.6,sz+.09))}\ntext = "RESERVE  >"\nfont_size = 28\npixel_size = 0.005\noutline_size = 2')
 x,z=SPAWN;scriptnode('PlayerSpawn','Node3D','Core/PlayerSpawnPoint',(x,1.2,z),'rotation_degrees = Vector3(0, 180, 0)')
