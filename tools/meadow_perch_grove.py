"""Tall trees behind the Meadow boardwalk, with supported native flat bird hangouts."""
import math

TREES=[(-138,9,11),(-137,16,12),(-139,23,10),(-137,30,13),(-138,37,11),(-137,44,12),(-138,51,10)]

def build(g):
 from sculpted_terrain import surface
 from park_perches import flat
 node,sub,vec,box=[g[k] for k in ('node','sub','vec','box')]
 parent='MeadowPerchGrove';node(parent,'Node3D','.')
 crown=sub('SphereMesh','radius = 0.5\nheight = 1\nradial_segments = 7\nrings = 3')
 landings=[]
 def beam(name,a,b,width):
  dx,dy,dz=[b[k]-a[k] for k in range(3)]
  length=math.sqrt(dx*dx+dy*dy+dz*dz)
  node(name,'Node3D',parent,f'position = {vec(tuple((a[k]+b[k])/2 for k in range(3)))}\nrotation_degrees = Vector3({-math.degrees(math.atan2(dy,math.hypot(dx,dz)))},{math.degrees(math.atan2(dx,dz))},0)')
  box('Wood',(0,0,0),(width,width,length),'arrivaldark',False,parent=parent+'/'+name)
 for i,(x,z,h) in enumerate(TREES):
  base=surface(x,z)[0]+.025
  trunk=sub('CylinderMesh',f'top_radius = 0.20\nbottom_radius = 0.48\nheight = {h}\nradial_segments = 7')
  node('Trunk'+str(i),'MeshInstance3D',parent,f'position = {vec((x,base+h/2,z))}\nmesh = {trunk}\nmaterial_override = {g["mats"]["arrivaldark"]}')
  shape=sub('CylinderShape3D',f'radius = 0.43\nheight = {h}')
  body='TrunkBody'+str(i)
  node(body,'StaticBody3D',parent,f'position = {vec((x,base+h/2,z))}\ncollision_layer = 11\ncollision_mask = 0')
  node('Shape','CollisionShape3D',parent+'/'+body,'shape = '+shape)
  # Branch tips remain clear of crowns and trunk, with a generous bird footprint.
  for j,(side,level) in enumerate([(-1,.38),(1,.56),(-1,.73)]):
   y=base+h*level;tip=(x+side*3.2,y,z+.5)
   beam(f'Branch{i}_{j}',(x,y-.65,z),tip,.24)
   px=x+side*2.65
   box(f'BranchTip{i}_{j}',(px,y,z+.5),(1.3,.24,.55),'arrivaldark',False,parent=parent)
   landing=(px,y+.13,z+.5)
   flat(g,f'MeadowGroveLanding{i}_{j}',landing,1.05,.43);landings.append(landing)
  for j,(dx,dy,dz,w) in enumerate([(0,0,0,5),(-2,-.6,.3,3.8),(2,-.3,-.2,3.9),(0,1.8,.2,3.6)]):
   beam(f'CrownBranch{i}_{j}',(x,base+h*.78,z),(x+dx,base+h+dy,z+dz),.20)
   node(f'Crown{i}_{j}','MeshInstance3D',parent,f'position = {vec((x+dx,base+h+dy,z+dz))}\nscale = {vec((w,w*.68,w*.8))}\nmesh = {crown}\nmaterial_override = {g["mats"]["leaf"]}')
 return {'trees':len(TREES),'landing_surfaces':landings}
