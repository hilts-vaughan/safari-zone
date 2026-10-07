"""Union overlapping convex path pieces into one native, non-overlapping mesh."""
import math

def clip(poly,a,b,inside=True):
 def side(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  sp,sq=side(p),side(q);ip=sp>=-1e-9 if inside else sp<=1e-9;iq=sq>=-1e-9 if inside else sq<=1e-9
  if ip:out.append(p)
  if ip!=iq:
   t=sp/(sp-sq);out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
 return out

def area(p):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))/2 if len(p)>2 else 0

def subtract(poly,cutter):
 outside=[];remaining=poly
 for a,b in zip(cutter,cutter[1:]+cutter[:1]):
  piece=clip(remaining,a,b,False)
  if area(piece)>1e-7:outside.append(piece)
  remaining=clip(remaining,a,b)
  if area(remaining)<1e-7:break
 return outside

def build(g):
 from map_layout import segments,WAYPOINTS,FACILITIES,biome
 from frontage_scene import contains as front
 from grasslands_layout import contains as grass
 from woodland_section import contains as study
 from gatehouse_scene import CENTER,HALF_WIDTH,HALF_DEPTH
 polygons=[]
 for a,b in segments():
  mid=((a[0]+b[0])/2,(a[1]+b[1])/2);w=3.2 if front(mid) or grass(mid) else 3.6 if study(mid) else 3.4 if biome(mid)=='forest' else 5.5
  dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz);ux,uz=dx/length,dz/length;nx,nz=-uz*w/2,ux*w/2
  a=(a[0]-ux*.4,a[1]-uz*.4);b=(b[0]+ux*.4,b[1]+uz*.4)
  polygons.append([(a[0]-nx,a[1]-nz),(b[0]-nx,b[1]-nz),(b[0]+nx,b[1]+nz),(a[0]+nx,a[1]+nz)])
 def oval(x,z,rx,rz):return [(x+rx*math.cos(i*math.tau/32),z+rz*math.sin(i*math.tau/32)) for i in range(32)]
 for name,p in WAYPOINTS.items():
  if name in {"wetlandplaza","watergarden","waterfall","grottoleft","grottoinside","grottoright","gatepicnicview","gatepicnic","gatepicnicleft","gatepicnicright"}:continue # Review markers are not trail junctions.
  r=1.6 if front(p) or grass(p) else 1.9 if study(p) or biome(p)=='forest' else 3.6
  polygons.append(oval(*p,r,r))
 for key,p in FACILITIES.items():
  if key!='grass':polygons.append(oval(*p,15,14))
 # The building has its own tile floor. Trim paths at its footprint, including carpet.
 x,z=CENTER;building=[(x-HALF_WIDTH,z-HALF_DEPTH),(x+HALF_WIDTH,z-HALF_DEPTH),(x+HALF_WIDTH,z+HALF_DEPTH),(x-HALF_WIDTH,z+HALF_DEPTH)]
 accepted=[];pieces=[]
 for poly in polygons:
  candidates=subtract(poly,building)
  for prior in accepted:
   candidates=[piece for candidate in candidates for piece in subtract(candidate,prior)]
   if not candidates:break
  pieces.extend(candidates);accepted.append(poly)
 lines=[];triangles=[]
 for poly in pieces:
  for i in range(1,len(poly)-1):
   tri=[poly[0],poly[i+1],poly[i]] # Positive Y normal.
   if area(tri)>1e-7:triangles.append(tri)
 for tri in triangles:
  for x,z in tri:lines.append(f'v {x:.7f} 0.09 {z:.7f}')
 lines.append('vn 0 1 0')
 for i in range(len(triangles)):lines.append('f '+' '.join(f'{i*3+j+1}//1' for j in range(3)))
 target=g['ROOT']/'editor/SceneEditor/EXTERNAL/Touma/SafariZone/Terrain';target.mkdir(parents=True,exist_ok=True)
 assets=g['ROOT']/'assets/environment/terrain';assets.mkdir(parents=True,exist_ok=True)
 content='\n'.join(lines)+'\n'
 for folder in (target,assets):(folder/'ReservePaths.obj').write_text(content)
 mesh=g['resource']('res://EXTERNAL/Touma/SafariZone/Terrain/ReservePaths.obj','Mesh')
 g['node']('ReservePaths','MeshInstance3D','.','mesh = '+mesh+'\nmaterial_override = '+g['mats']['path'])
 return {'source_polygons':len(polygons),'triangles':len(triangles),'area_m2':round(sum(area(p) for p in pieces),3),'surface_y':.09}
