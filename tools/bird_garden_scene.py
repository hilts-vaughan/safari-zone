"""Junction perch garden: feeder, snag, rails, logs, and dry ground clearings."""
import math

def build(g):
 node,sub,vec,box,prefab=[g[k] for k in ['node','sub','vec','box','prefab']]
 parent='JunctionBirdGarden';node(parent,'Node3D','.')
 def block(n,p,s,m='arrivalwood',solid=True):box(n,p,s,m,solid=solid,parent=parent)
 def landing(n,x,y,z,w,d):
  prefab(n,'FunctionalObjects/RockHangout',(x,y+.01,z),(w,1,d))
 def branch(n,a,b,width):
  delta=tuple(b[i]-a[i] for i in range(3));length=math.sqrt(sum(v*v for v in delta))
  mesh=sub('CylinderMesh',f'top_radius = {width*.65}\nbottom_radius = {width}\nheight = {length}\nradial_segments = 6')
  # Native +Y cylinder axis points toward the branch tip.
  yaw=math.degrees(math.atan2(delta[0],delta[2]));tilt=math.degrees(math.atan2(math.hypot(delta[0],delta[2]),delta[1]))
  node(n,'MeshInstance3D',parent,f'position = {vec(tuple((a[i]+b[i])/2 for i in range(3)))}\nrotation_degrees = Vector3({tilt},{yaw},0)\nmesh = {mesh}\nmaterial_override = {g["mats"]["arrivalwood"]}')
 # Feeding tray: broad flat rim, accessible from any side, no new shop logic.
 x,z=-86,63
 block('FeederPost',(x,.85,z),(.22,1.7,.22))
 block('FeedingTray',(x,1.7,z),(1.8,.12,1.2));landing('FeederLanding',x,1.76,z,1.6,1)
 for side in [-1,1]:
  block('RoofPost'+str(side),(x+side*.68,2.03,z),(.09,.65,.09),solid=False)
  mesh=sub('BoxMesh','size = Vector3(1.15,0.1,1.6)')
  node('FeederRoof'+str(side),'MeshInstance3D',parent,f'position = {vec((x+side*.48,2.52,z))}\nrotation_degrees = Vector3(0,0,{-side*22})\nmesh = {mesh}\nmaterial_override = {g["mats"]["arrivaldark"]}')
 # Short perch fence and deadwood stay outside the fork's walking corridor.
 for i in range(4):block('RailPost'+str(i),(-59+i*2, .65,63),(.2,1.3,.2))
 for i,y in enumerate([.5,1.12]):block('PerchRail'+str(i),(-56,y,63),(6.2,.16,.32),solid=False)
 landing('FenceLanding',-56,1.2,63,5.8,.26)
 x,z=-51,62
 block('SnagTrunk',(x,2.7,z),(.42,5.4,.42))
 for i,(sign,y) in enumerate([(-1,2.5),(1,3.7),(-1,4.9)]):
  branch('SnagArm'+str(i),(x,y-.4,z),(x+sign*1.35,y,z),.16)
  block('SnagTip'+str(i),(x+sign*1.4,y,z),(.7,.12,.38),solid=False)
  landing('SnagLanding'+str(i),x+sign*1.4,y+.06,z,.62,.3)
 # Logs provide low perches and a photographic focus on the central island.
 for i,(x,z) in enumerate([(-67,51),(-70,51.5),(-69,50)]):
  branch('RestLog'+str(i),(x-1,.24,z),(x+1,.24,z),.24)
  block('LogTop'+str(i),(x,.45,z),(1.7,.08,.34),solid=False)
  landing('LogLanding'+str(i),x,.49,z,1.5,.28)
 for i,(x,z) in enumerate([(-65,50),(-71,50),(-68,52)]):
  block('RestStone'+str(i),(x,.18,z),(.9,.36,.7),'arrivalstone')
  landing('StoneLanding'+str(i),x,.36,z,.75,.55)
 for i,(x,z) in enumerate([(-87,63),(-85,63),(-52,62),(-50,62),(-84,50),(-82,50)]):
  prefab('PerchGardenFlowers'+str(i),'Decorations/Flowers',(x,.2,z),(.06,.06,.06))
 # Shallow basin is scenery; it does not become a water habitat.
 x,z=-83,50
 block('BathBase',(x,.12,z),(.65,.24,.65),'arrivalstone')
 block('BathStem',(x,.65,z),(.24,1.05,.24),'arrivalstone')
 mesh=sub('CylinderMesh','top_radius = 0.7\nbottom_radius = 0.55\nheight = 0.16\nradial_segments = 12')
 node('Birdbath','MeshInstance3D',parent,f'position = {vec((x,1.2,z))}\nmesh = {mesh}\nmaterial_override = {g["mats"]["arrivalstone"]}')
 block('BathWater',(x,1.285,z),(.65,.01,.65),'arrivalwater',solid=False)
 landing('BirdbathRim',x+.52,1.28,z,.25,.5)
 clearings=[(-89,67,1.6),(-84,59,1.4),(-64,51,1.4),(-72,52,1.2),(-50,65,1.6),(-58,60,1.2)]
 # Small dry discs keep landing selection away from trunks, props, and flowers.
 for i,(x,z,r) in enumerate(clearings):
  prefab('JunctionGroundLanding'+str(i),'FunctionalObjects/HopGroundHangout',(x,.06,z),(r,1,r))
 return {'ground_clearings':clearings,'raised_landing_areas':12}
