"""Dense supported bird landing garden east of the Highlands scaffold."""
import math
CENTER=(124,-65)
def reserved(p):
 return ((p[0]-124)/10)**2+((p[1]+65)/10)**2<1

def build(g):
 from park_perches import flat
 from sculpted_terrain import surface
 node,sub,vec,box,prefab=[g[k] for k in ('node','sub','vec','box','prefab')]
 parent='HighlandsBirdNook';node(parent,'Node3D','.')
 supports=[]
 def block(name,x,z,h,w,d,material='arrivalwood',base=0):
  y,_=surface(x,z);y+=base
  box(name,(x,y+h/2,z),(w,h,d),material,parent=parent)
  flat(g,'BirdNookLanding'+name,(x,y+h+.01,z),w*.8,d*.8)
  supports.append((x,y+h,z))
 def branch_tree(i,x,z,h):
  y,_=surface(x,z)
  box('PerchTrunk'+str(i),(x,y+h/2,z),(.3,h,.3),'arrivalwood',parent=parent)
  for j,(side,level) in enumerate([(-1,.45),(1,.68),(-1,.9)]):
   block(f'Branch{i}_{j}',x+side*.8,z,h*.03,1.8,.32,base=h*level)
 # Branch silhouettes use supported stock flat hangouts, avoiding native branch lookup failures.
 branch_tree(0,121,-66,3.8);branch_tree(1,117,-70,2.4)
 for i,(x,z,h) in enumerate([(117,-60,.7),(119,-59,1),(120.5,-61,.55)]):
  block('Stump'+str(i),x,z,h,.65,.65)
 for i,(x,z) in enumerate([(130,-63),(129,-70)]):
  block('Log'+str(i),x,z,.55,3.4,.8)
  for j,dx in enumerate([-.95,.95]):block(f'LogStub{i}_{j}',x+dx,z,.5,.3,.32,base=.55)
 for i,(x,z) in enumerate([(128,-58),(132,-59.5)]):
  block('Stone'+str(i),x,z,.42,2,1.4,'highstone')
 x,z=124,-72;y,_=surface(x,z)
 box('FeederPost',(x,y+1.1,z),(.18,2.2,.18),'arrivalwood',parent=parent)
 block('FeederTray',x,z,.12,1.3,.9,'plank',base=2.18)
 box('FeederRoof',(x,y+2.95,z),(1.6,.16,1.15),'arrivalwood',parent=parent)
 for side in (-1,1):box('FeederUpright'+str(side),(x+side*.5,y+2.6,z),(.09,.6,.09),'arrivalwood',parent=parent)
 mesh=sub('SphereMesh','radius = 0.5\nheight = 1\nradial_segments = 8\nrings = 4')
 plants=[(115,-60),(115,-64),(115,-68),(118,-73),(121,-74),(127,-74),(130,-73),(132,-70),(133,-66),(134,-62),(134,-58),(130,-57),(118,-58)]
 for i,(x,z) in enumerate(plants):
  y,_=surface(x,z)
  node('Shrub'+str(i),'MeshInstance3D',parent,f'position = {vec((x,y+.3,z))}\nscale = Vector3(2.2,0.9,1.7)\nmesh = {mesh}\nmaterial_override = {g["mats"]["leaf"]}')
  for j,(dx,dz) in enumerate([(-.7,.5),(.7,.5)]):
   fy,_=surface(x+dx,z+dz)
   prefab(f'BirdNookFlowers{i}_{j}','Decorations/Flowers',(x+dx,fy+.025,z+dz),(.12,.12,.12))
 return {'landing_surfaces':supports,'plant_groups':len(plants),'center':CENTER}
