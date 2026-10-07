"""Small picnic grove beyond Wetlands Rest's rear doorway."""
import math
TABLES=[(30.5,18),(45.5,18)]
TREES=[(28,13,1.15),(48,13,1.15)]
# Doorway forks around the planted island and rejoins on the northern lawn.
ROUTES=[[(38,33),(38,29),(33,26),(33,20),(38,17)],[(38,29),(43,26),(43,20),(38,17)]]

def contains(p,margin=0):
 x,z=p
 return 17-margin<x<59+margin and -5-margin<z<33+margin

def grade_mask(p):
 x,z=p
 # Feather the old tall ridge outside the entire new garden/hill footprint.
 d=max(17-x,x-59,-5-z,z-33,0)
 return min(1,d/6)

def build_hills(g):
 from sculpted_terrain import build
 # Low broad shoulders: avoid the old sheer gray face across the doorway view.
 return build(g,'GatePicnicHills',[(31,6,14,9,2.5),(48,4,12,9,3.0)],(17,60,-6,16),spacing=1.25,turf_color='#9bbb74',height_mask=lambda p:min(1,max(0,(17-p[1])/4)))

def build(g):
 from picnic_garden import table
 from sculpted_terrain import surface
 node,sub,vec,prefab=[g[k] for k in ['node','sub','vec','prefab']]
 parent='GatePicnicGrove';node(parent,'Node3D','.')
 for i,(x,z) in enumerate(TABLES):table(g,parent,'Gate'+str(i),x,z)
 for i,(x,z,s) in enumerate(TREES):
  y,_=surface(x,z);prefab(f'GatePicnicShade{i}','FunctionalObjects/TreeCFunctional',(x,y,z),(s,s,s))
 # Union the fork and table spurs before triangulation, preventing z-fighting.
 from path_surface import subtract,area
 links=[(a,b) for route in ROUTES for a,b in zip(route,route[1:])]+[((33,20),(30.5,18)),((43,20),(45.5,18))]
 pieces=[];accepted=[]
 for a,b in links:
  dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz);ux,uz=dx/length,dz/length
  nx,nz=-uz*1.2,ux*1.2;a=(a[0]-ux*.3,a[1]-uz*.3);b=(b[0]+ux*.3,b[1]+uz*.3)
  polygon=[(a[0]-nx,a[1]-nz),(b[0]-nx,b[1]-nz),(b[0]+nx,b[1]+nz),(a[0]+nx,a[1]+nz)]
  pending=[polygon]
  for old in accepted:pending=[part for poly in pending for part in subtract(poly,old)]
  pieces.extend(pending);accepted.append(polygon)
 vertices=[]
 for poly in pieces:
  for i in range(1,len(poly)-1):
   if area([poly[0],poly[i+1],poly[i]])>1e-7:
    vertices.extend(v for x,z in [poly[0],poly[i+1],poly[i]] for v in (x,.10,z))
 # Imported native mesh keeps the ground-level fork continuous.
 lines=[f'v {vertices[i]} {vertices[i+1]} {vertices[i+2]}' for i in range(0,len(vertices),3)]+['vn 0 1 0']
 lines += ['f '+' '.join(f'{i+j+1}//1' for j in range(3)) for i in range(0,len(vertices)//3,3)]
 content='\n'.join(lines)+'\n'
 for folder in [g['ROOT']/'assets/environment/terrain',g['ROOT']/'editor/SceneEditor/EXTERNAL/Touma/SafariZone/Terrain']:
  folder.mkdir(parents=True,exist_ok=True);(folder/'GatePicnicPaths.obj').write_text(content)
 mesh=g['resource']('res://EXTERNAL/Touma/SafariZone/Terrain/GatePicnicPaths.obj','Mesh')
 node('Paths','MeshInstance3D',parent,'mesh = '+mesh+'\nmaterial_override = '+g['mats']['path'])
 # Rounded low planting, all outside the walkable forks and table clearances.
 leaf=sub('SphereMesh','radius = 0.5\nheight = 1\nradial_segments = 10\nrings = 5')
 bushmat=g['mat']('#648c55');light=g['mat']('#80a767')
 bushes=[(37,23,.65),(39,23.5,.75),(38,21.5,.55),(23,16,.65),(53,16,.65),(25,8,.55),(34,7,.6),(47,4,.65),(54,6,.5)]
 for i,(x,z,s) in enumerate(bushes):
  y,_=surface(x,z)
  node(f'Bush{i}','MeshInstance3D',parent,f'position = {vec((x,y+s*.45,z))}\nscale = {vec((s*2.3,s*1.1,s*1.8))}\nmesh = {leaf}\nmaterial_override = {light if i%2 else bushmat}')
 # Flower edging softens the center and the shaded edges; never spans the paths.
 for i,(x,z) in enumerate([(37,24.5),(39,24.5),(37,21),(39,21),(24,17),(52,17),(25,9),(35,5),(46,7)]):
  y,_=surface(x,z);prefab(f'GatePicnicFlowers{i}','Decorations/Flowers',(x,y+.025,z),(.045,.045,.045))
 # A few small faceted outcrops replace large bare stone walls.
 rock=sub('SphereMesh','radius = 0.5\nheight = 1\nradial_segments = 6\nrings = 3')
 for i,(x,z,s) in enumerate([(22,6,.7),(55,3,.8),(51,8,.55)]):
  y,_=surface(x,z)
  node(f'HillStone{i}','MeshInstance3D',parent,f'position = {vec((x,y+s*.25,z))}\nscale = {vec((s*1.6,s*.8,s*1.2))}\nmesh = {rock}\nmaterial_override = {g["mats"]["rock"]}')
 return {'tables':2,'shade_trees':2,'planted_island':True,'rounded_bushes':len(bushes),'flower_groups':9,'small_outcrops':3,'hill_peaks':2,'fork_width_m':2.4,'table_landings':6}
