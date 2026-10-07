"""Native solid hedges, low stone walls and grass-topped faceted ridges."""
import math
from enclosure_layout import build_layout
from map_layout import biome

def build(g):
 node,sub,vec,mat,box,prefab=[g[n] for n in ['node','sub','vec','mat','box','prefab']];mats=g['mats'];model=build_layout()
 for k,c in [('hedge','#48764b'),('hedgelight','#6b9659'),('hedgedark','#355f45'),('ridge','#81766b'),('ridgecap','#79a45d'),('wallstone','#90958c'),('hedgeflower','#f3efdc')]:mats[k]=mat(c)
 native_bush=g['resource']('res://Art/Decorations/Foliage/SimpleBushA.glb','PackedScene')
 for k,path in [('hedge','hedgeMaterial'),('marshhedge','MarshHedgeMaterial')]:mats[k]=g['resource']('res://Art/Materials/'+path+'.tres','Material')
 leaf=sub('SphereMesh','radius = 0.5\nheight = 1.0\nradial_segments = 8\nrings = 4')
 mesh=sub('CylinderMesh','top_radius = 0.62\nbottom_radius = 1.0\nheight = 1.0\nradial_segments = 7')
 cap=sub('CylinderMesh','top_radius = 0.63\nbottom_radius = 0.63\nheight = 0.12\nradial_segments = 7')
 from fountain_garden import contains as in_fountain,grade_mask
 from picnic_garden import contains as in_picnic,grade_mask as picnic_grade
 from forest_service_garden import contains as in_service,grade_mask as service_grade
 from highlands_garden import contains as in_highlands,grade_mask as highland_grade
 from wetlands_clearing import contains as in_water_garden,grade_mask as wetland_grade
 from gate_picnic import contains as in_gate_picnic,grade_mask as gate_picnic_grade,build_hills
 for kind in ['hedges','walls']:
  for i,h in enumerate(model[kind]):
   # Older hedge pockets are wholly covered by later terrain. Remove both
   # foliage and the associated collider/hangout rather than raising a hedge.
   if kind=='hedges':continue # Retire obstacle hedges: their canopies intersect sculpted rock and block jumps.
   if in_gate_picnic(h['p'],h['radius']) or in_water_garden(h['p'],h['radius']) or in_highlands(h['p'],h['radius']) or in_fountain(h['p'],h['radius']) or in_picnic(h['p'],h['radius']) or in_service(h['p'],h['radius']):continue
   x,z=h['p'];length=h['length'];height=h['height'];name=kind+str(i)
   node(name,'Node3D','.',f'position = {vec((x,0,z))}\nrotation_degrees = Vector3(0, {h["angle"]}, 0)')
   box('Core',(0,height/2,0),(2.1,height,length),'hedge' if kind=='hedges' else 'wallstone',parent=name)
   if kind=='hedges':
    g['nodes'][-3] += '\nvisible = false'
    habitat=biome((x,z));material=mats['marshhedge' if habitat=='water' else 'hedge']
    for j in range(3):
     node('Bush'+str(j),None,name,f'position = {vec((0,0,(j-1)*length*.28))}\nscale = {vec((1.65,height/1.83,length*.45/1.266))}',native_bush)
     node('Cube',None,name+'/Bush'+str(j),'surface_material_override/0 = '+material,index=0)
    resource=g['resource']('res://Scenes/FunctionalObjects/RockHangout.tscn','PackedScene')
    node('CanopyLanding',None,name,f'position = Vector3(0,{height+.01},0)\nscale = {vec((.7,1,max(.3,length-.3)))}',resource)
    if habitat=='grass' or i%4==0:
     for j in range(3):node('Flower'+str(j),'MeshInstance3D',name,f'position = {vec((1.08,height*.7,(j-1)*length*.25))}\nscale = Vector3(0.18, 0.18, 0.18)\nmesh = {leaf}\nmaterial_override = {mats["hedgeflower"]}')
   else:
    for j in range(3):box('Cap'+str(j),(0,height+.06,(j-1)*length/3),(2.25,.16,length/3-.08),'rock',parent=name)
 from sculpted_terrain import build as sculpt
 from frontage_scene import contains as in_frontage
 from grasslands_layout import contains as in_grasslands
 from woodland_section import contains as in_study
 from gatehouse_scene import contains as in_gatehouse
 centers=[(h['p'][0],h['p'][1],h['radius']*1.8,h['radius']*1.8,h['height']*.55) for h in model['ridges']]
 sculpt(g,'ReserveSculptedRidges',centers,(-175,175,-125,125),
        allowed=lambda p:not in_frontage(p,3) and not in_grasslands(p,3) and not in_study(p,3) and not in_gatehouse(p,3),height_mask=lambda p:min(grade_mask(p),picnic_grade(p),service_grade(p),highland_grade(p),wetland_grade(p),gate_picnic_grade(p)))
 build_hills(g)
 return model
