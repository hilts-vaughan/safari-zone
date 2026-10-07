"""Deterministic shared-vertex terrain; native imported meshes, no runtime scripts."""
import math
from pathlib import Path

def build(g, name, centers, bounds, allowed=lambda p: True, spacing=2.5, parent='.', respect_paths=True, rock_color='#938c7d', turf_color='#9bbb74', height_mask=lambda p:1.0):
 from map_layout import path_distance
 node,sub,vec,mat=[g[k] for k in ['node','sub','vec','mat']]
 xmin,xmax,zmin,zmax=bounds
 nx=math.ceil((xmax-xmin)/spacing);nz=math.ceil((zmax-zmin)/spacing)
 vertices={}
 for ix in range(nx+1):
  for iz in range(nz+1):
   x=xmin+(xmax-xmin)*ix/nx;z=zmin+(zmax-zmin)*iz/nz
   h=0
   if allowed((x,z)):
    for cx,cz,rx,rz,height in centers:
     d=math.sqrt(((x-cx)/rx)**2+((z-cz)/rz)**2)
     if d<1:
      # Joined broad shoulders with small asymmetric changes in slope.
      profile=max(0,1-d**1.7)**.65
      h=max(h,height*profile*(1+.055*math.sin(x*.61+z*.37)))
    if respect_paths:h*=min(1,max(0,(path_distance((x,z))-4.5)/3))
   h*=height_mask((x,z))
   vertices[ix,iz]=(round(x,4),round(h,4),round(z,4))
 SURFACES.append((vertices,nx,nz,bounds))
 rock=[];turf=[];faces=[]
 for ix in range(nx):
  for iz in range(nz):
   a,b,c,d=[vertices[p] for p in [(ix,iz),(ix,iz+1),(ix+1,iz+1),(ix+1,iz)]]
   for tri in [(a,b,c),(a,c,d)]:
    if max(v[1] for v in tri)<.08:continue
    u=[tri[1][j]-tri[0][j] for j in range(3)];v=[tri[2][j]-tri[0][j] for j in range(3)]
    normal=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    length=math.sqrt(sum(n*n for n in normal));normal=tuple(n/length for n in normal)
    (turf if normal[1]>.77 else rock).append((tri,normal))
    faces.extend(v for p in tri for v in p)
 assets=g['ROOT']/'assets/environment/terrain';assets.mkdir(parents=True,exist_ok=True)
 target=g['ROOT']/'editor/SceneEditor/EXTERNAL/Touma/SafariZone/Terrain';target.mkdir(parents=True,exist_ok=True)
 node(name,'Node3D',parent)
 path=name if parent=='.' else parent+'/'+name
 for label,triangles,color in [('Rock',rock,rock_color),('Turf',turf,turf_color)]:
  if not triangles:continue
  lines=[]
  for tri,n in triangles:
   for p in tri:lines.append('v '+' '.join(map(str,p)))
  for tri,n in triangles:lines.append('vn '+' '.join(str(round(v,5)) for v in n))
  for i in range(len(triangles)):
   lines.append('f '+' '.join(f'{i*3+j+1}//{i+1}' for j in range(3)))
  filename=name+label+'.obj';content='\n'.join(lines)+'\n'
  (assets/filename).write_text(content);(target/filename).write_text(content)
  mesh=g['resource']('res://EXTERNAL/Touma/SafariZone/Terrain/'+filename,'Mesh')
  node(label,'MeshInstance3D',path,'mesh = '+mesh+'\nmaterial_override = '+mat(color))
 shape=sub('ConcavePolygonShape3D','data = PackedVector3Array('+', '.join(map(str,faces))+')\nbackface_collision = true')
 node('Body','StaticBody3D',path,'collision_layer = 11\ncollision_mask = 0')
 node('Shape','CollisionShape3D',path+'/Body','shape = '+shape)
 return {'triangles':len(rock)+len(turf),'peaks':len(centers),'spacing_m':spacing}

# Build-time queries use the exact imported triangle grid, never analytic peak guesses.
SURFACES=[]
def surface(x,z):
 height=0;normal=1
 for vertices,nx,nz,bounds in SURFACES:
  xmin,xmax,zmin,zmax=bounds
  if not xmin<=x<xmax or not zmin<=z<zmax:continue
  fx=(x-xmin)/(xmax-xmin)*nx;fz=(z-zmin)/(zmax-zmin)*nz
  ix,iz=int(fx),int(fz);u,v=fx-ix,fz-iz
  a,b,c,d=[vertices[p] for p in [(ix,iz),(ix,iz+1),(ix+1,iz+1),(ix+1,iz)]]
  tri=(a,b,c) if v>=u else (a,c,d)
  y=a[1]+v*(b[1]-a[1])+u*(c[1]-b[1]) if v>=u else a[1]+u*(d[1]-a[1])+v*(c[1]-d[1])
  if y>height:
   height=y
   e=[tri[1][i]-tri[0][i] for i in range(3)];f=[tri[2][i]-tri[0][i] for i in range(3)]
   n=(e[1]*f[2]-e[2]*f[1],e[2]*f[0]-e[0]*f[2],e[0]*f[1]-e[1]*f[0])
   normal=n[1]/math.sqrt(sum(t*t for t in n))
 return height,normal

def flat_ground(p,radius=1):
 heights=[surface(p[0]+dx,p[1]+dz)[0] for dx,dz in [(0,0),(-radius,-radius),(-radius,radius),(radius,-radius),(radius,radius)]]
 return max(heights)<.08

def foliage(g):
 from map_layout import inside,pond_contains,path_distance
 from park_perches import flat
 count=0
 for x in range(-170,174,3):
  for z in range(-120,120,3):
   y,n=surface(x,z)
   if y<.5 or n<.9 or not inside((x,z)) or pond_contains((x,z),1) or path_distance((x,z))<5:continue
   nearby=[surface(x+dx,z+dz)[0] for dx,dz in [(-.45,-.45),(-.45,.45),(.45,-.45),(.45,.45)]]
   if max(nearby)-min(nearby)>.35:continue
   asset='Flowers' if count%4==0 else 'GreenGrassA'
   scale=.055 if asset=='Flowers' else .85
   g['prefab']('HilltopFoliage'+str(count),'Decorations/'+asset,(x,y+.03,z),(scale,scale,scale));count+=1
 return count
