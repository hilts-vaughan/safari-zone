"""Three planted grassland pockets and a climbable timber observation loop."""
import math, random
from grasslands_layout import POCKETS, HEIGHT, WALKWAY, STAIRS, RAMP, DECK, hedges, trees, grass_patches

def build(g):
    node,sub,vec,mat,box,prefab=[g[n] for n in ['node','sub','vec','mat','box','prefab']]
    for key,color in [('grasshedge','#46794b'),('grassleaf','#659653'),('walktimber','#a77c51'),('walkgrain','#855f3e'),('walkstone','#a6aa96'),('grasscliff','#9c9486'),('grasscap','#88ac62')]:
        g['mats'][key]=mat(color)
    unit=sub('BoxMesh','size = Vector3(1, 1, 1)')
    node('GrasslandsGarden','Node3D','.')
    parent='GrasslandsGarden'
    def visual(name,pos,size,m,angle=0,par=parent):
        node(name,'MeshInstance3D',par,f'position = {vec(pos)}\nscale = {vec(size)}\nrotation_degrees = Vector3(0, {angle}, 0)\nmesh = {unit}\nmaterial_override = {g["mats"][m]}')
    def beam(name,a,b,width,height,m='walktimber',solid=False):
        dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
        angle=math.degrees(math.atan2(dx,dz))
        mid=((a[0]+b[0])/2,(a[2]+b[2])/2,(a[1]+b[1])/2)
        slope=math.degrees(math.atan2(b[2]-a[2],length))
        node(name,'Node3D',parent,f'position = {vec(mid)}\nrotation_degrees = Vector3({-slope}, {angle}, 0)')
        path=parent+'/'+name
        size=(width,height,math.dist(a,b)+.08)
        box('Beam',(0,0,0),size,m,solid=solid,parent=path)
        # Local landing strips inherit rail yaw and staircase slope.
        if name.startswith(('WalkRail','DeckOuterRail','DeckEndRail','OverlookEndRail','StairRail')) and (name.endswith('_1.1') or 'Rail' in name and not name.startswith(('WalkRail','StairRail')) or '_1.1South' in name or '_1.1North' in name):
            resource=g['resource']('res://Scenes/FunctionalObjects/RockHangout.tscn','PackedScene')
            node('Landing',None,path,f'position = Vector3(0,{height/2+.01},0)\nscale = {vec((width*.75,1,max(.15,size[2]-.3)))}',resource)
    # Continuous, collidable waist-high hedge ribbons; ornamental leaves stay opaque.
    leaf=sub('SphereMesh','radius = 0.5\nheight = 1.0\nradial_segments = 6\nrings = 3')
    foliage=[]
    for i,(pocket,a,b) in enumerate(hedges()):
        dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
        angle=math.degrees(math.atan2(dx,dz))
        x,z=(a[0]+b[0])/2,(a[1]+b[1])/2
        name='HedgeRibbon'+str(i)
        node(name,'Node3D',parent,f'position = {vec((x,0,z))}\nrotation_degrees = Vector3(0, {angle}, 0)')
        box('Core',(0,.3,0),(1.05,.6,length+.15),'grasshedge',parent=parent+'/'+name)
        # Inset flat canopy areas follow each ribbon's rotation and leaf tops.
        resource=g['resource']('res://Scenes/FunctionalObjects/RockHangout.tscn','PackedScene')
        node('HedgeLanding'+str(i),None,parent,f'position = {vec((x,.76,z))}\nrotation_degrees = Vector3(0,{angle},0)\nscale = {vec((.42,1,max(.2,length-.12)))}',resource)
        foliage_rng=random.Random(965+i)
        count=max(5,math.ceil(length/.19))
        for j in range(count):
            t=(j+.5)/count;px,pz=a[0]+dx*t,a[1]+dz*t
            for side in [-1,1]:
                for y in [.15,.33,.51]:
                    lift=foliage_rng.uniform(-.06,.06)
                    offset=.51+foliage_rng.uniform(-.03,.03)
                    foliage.append((px+side*dz/length*offset,y+lift,pz-side*dx/length*offset,.34,.27,.34,foliage_rng.random()*math.pi))
            for lateral in [-.33,0,.33]:
                foliage.append((px+dz/length*lateral,.6+foliage_rng.uniform(-.02,.04),pz-dx/length*lateral,.34,.24,.34,foliage_rng.random()*math.pi))
    def multimesh(name,mesh,material,instances):
        buffer=[]
        for x,y,z,sx,sy,sz,angle in instances:
            c,s=math.cos(angle),math.sin(angle)
            buffer.extend([c*sx,0,s*sz,x,0,sy,0,y,-s*sx,0,c*sz,z])
        mm=sub('MultiMesh',f'transform_format = 1\ninstance_count = {len(instances)}\nmesh = {mesh}\nbuffer = PackedFloat32Array('+', '.join(str(round(v,5)) for v in buffer)+')')
        node(name,'MultiMeshInstance3D',parent,f'multimesh = {mm}\nmaterial_override = {material}')
    multimesh('HedgeLeafClusters',leaf,g['mats']['grassleaf'],foliage)
    # Two deliberate rows of three native trees in every habitat pocket.
    for i,(x,z,pocket) in enumerate(trees()):
        prefab('GrasslandRowTree'+str(i),'FunctionalObjects/TreeCFunctional',(x,.04,z),(1.55,1.55,1.55),props=f'rotation_degrees = Vector3(0, {25 if i%2 else 205}, 0)')
        # Flat native Rock hangouts retain the established branch-lookup workaround.
        sign=1 if i%6<3 else -1
        box('GrasslandRestBranch'+str(i),(x+sign*.8,2.2,z),(2.1,.16,.55),'walkgrain',solid=False,parent=parent)
        prefab('GrasslandTreePerch'+str(i),'FunctionalObjects/RockHangout',(x+sign*1.15,2.29,z),(1.35,1,.48))
    for i,(x,z) in enumerate([(-107,57),(-74,14),(-40,57),(-23,15),(-123,15)]):
        prefab('GrasslandJunctionCherry'+str(i),'FunctionalObjects/CherryBlossomTreeAFunctional',(x+3.5,0,z-3.5),(1.1,1.1,1.1))
        from tree_landing_spots import add
        add(g,'GrasslandJunctionCherry'+str(i),x+3.5,z-3.5,1.1,cherry=True,parent=parent)
    # Native cutout grass texture: individual blades, no green translucent box/fog.
    texture=g['resource']('res://EXTERNAL/Touma/SafariZone/Frontage/tall-grass.png','Texture2D')
    grassmat=sub('StandardMaterial3D',f'transparency = 2\nalpha_scissor_threshold = 0.85\ncull_mode = 2\nalbedo_color = Color(1, 1, 1, 1)\nalbedo_texture = {texture}\nroughness = 1.0')
    grassmesh=sub('QuadMesh','size = Vector2(1.0, 1.0)')
    from grasslands_planting import placements
    grass,flowers,rocks=placements()
    blades=[]
    for px,pz,h,angle in grass:
        for turn in [0,math.pi/2]:blades.append((px,h/2+.025,pz,.85,h,1,angle+turn))
    for i,(x,z,w,d,pocket) in enumerate(grass_patches()):
        if i%4 or i==4:continue # Sparse grass destinations leave clear photography pockets preferred.
        prefab('TallGrassGroundPerch'+str(i),'FunctionalObjects/HopGroundHangout',(x,.06,z),(3.6,1,2.7))
    multimesh('TallGrassBlades',grassmesh,grassmat,blades)
    for i,(x,z,_,_) in enumerate(POCKETS):
        prefab('GrasslandOpenGroundPerch'+str(i),'FunctionalObjects/HopGroundHangout',(x,.06,z),(2.2,1,15))
    flowertexture=g['resource']('res://EXTERNAL/Touma/SafariZone/Frontage/wildflowers.png','Texture2D')
    flowermat=sub('StandardMaterial3D',f'transparency = 2\nalpha_scissor_threshold = 0.8\ncull_mode = 2\nalbedo_texture = {flowertexture}\nroughness = 1.0')
    flowercards=[]
    for px,pz,h,angle in flowers:
        for turn in [0,math.pi/2]:flowercards.append((px,h/2+.02,pz,h*.8,h,1,angle+turn))
    multimesh('MeadowWildflowers',grassmesh,flowermat,flowercards)
    rockmesh=sub('SphereMesh','radius = 0.5\nheight = 1.0\nradial_segments = 7\nrings = 3')
    for i,(px,pz,w,h) in enumerate(rocks):
        node('MeadowBoulder'+str(i),'MeshInstance3D',parent,f'position = {vec((px,h*.34,pz))}\nscale = {vec((w,h,w*.8))}\nmesh = {rockmesh}\nmaterial_override = {g["mats"]["grasscliff"]}')
        # Tight apex landing area stays on the rounded boulder's upper surface.
        prefab('MeadowBoulderLanding'+str(i),'FunctionalObjects/RockHangout',(px,h*.84+.01,pz),(w*.12,1,w*.096))
        shape=sub('SphereShape3D',f'radius = {min(w*.35,h*.45)}')
        node('MeadowBoulderBody'+str(i),'StaticBody3D',parent,f'position = {vec((px,h*.34,pz))}\ncollision_layer = 11\ncollision_mask = 0')
        node('Shape','CollisionShape3D',parent+'/MeadowBoulderBody'+str(i),'shape = '+shape)
    # A single sculpted spine has shared vertices and grassy sloping shoulders.
    from sculpted_terrain import build as sculpt
    terrain=sculpt(g,'GardenSculptedRidge',[(-145,z,9,14,h) for z,h in [(5,8),(18,9),(31,8),(44,8),(58,7.5)]],
                  (-155,-135,-9,72),parent=parent,spacing=2)
    # Timber floor has one continuous collision slab per run; planks are visual only.
    route=list(zip(WALKWAY,WALKWAY[1:]))
    for i,(a,b) in enumerate(route):
        beam('WalkFloor'+str(i),(a[0],a[1],a[2]-.13),(b[0],b[1],b[2]-.13),3.2,.26,solid=True)
        dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz);nx,nz=dz/length,-dx/length
        for sign in [-1,1]:
            for rise in [.55,1.1]:
                aa=(a[0]+sign*nx*1.62,a[1]+sign*nz*1.62,a[2]+rise)
                bb=(b[0]+sign*nx*1.62,b[1]+sign*nz*1.62,b[2]+rise)
                if i==0:
                    beam(f'WalkRail{i}_{sign}_{rise}South',aa,(aa[0],34.1,aa[2]),.13,.13,solid=True)
                    beam(f'WalkRail{i}_{sign}_{rise}North',(bb[0],25.9,bb[2]),bb,.13,.13,solid=True)
                else:beam(f'WalkRail{i}_{sign}_{rise}',aa,bb,.13,.13,solid=True)
        count=math.ceil(length/2.5)
        for j in range(count+1):
            t=j/count;x,z=a[0]+dx*t,a[1]+dz*t;y=a[2]+(b[2]-a[2])*t
            for sign in [-1,1]:
                px,pz=x+sign*nx*1.62,z+sign*nz*1.62
                from map_layout import path_distance
                if i==2 and path_distance((px,pz))<2.3:continue
                box(f'WalkPost{i}_{j}_{sign}',(px,(y+1.25)/2,pz),(.2,y+1.25,.2),'walktimber',parent=parent)
                if y>.5:box(f'WalkFoot{i}_{j}_{sign}',(px,.12,pz),(.45,.24,.45),'walkstone',parent=parent)
        for j in range(math.ceil(length/.4)):
            t=(j+.5)/math.ceil(length/.4);x,z=a[0]+dx*t,a[1]+dz*t;y=a[2]+(b[2]-a[2])*t+.007
            aa=(x-nx*1.58,z-nz*1.58,y);bb=(x+nx*1.58,z+nz*1.58,y)
            beam(f'WalkPlankJoint{i}_{j}',aa,bb,.014,.008,'walkgrain')
    # Closed overlook end, offset beyond the final walking sample.
    ex,ez,ey=WALKWAY[-1]
    box('OverlookLanding',(ex,HEIGHT-.13,ez),(3.6,.26,3.6),'walktimber',parent=parent)
    beam('OverlookEndRail',(ex-1.8,ez-1.8,ey+1.1),(ex+1.8,ez-1.8,ey+1.1),.16,.16,solid=True)
    x,z,w,d=DECK
    box('ObservationDeck',(x,HEIGHT-.13,z),(w,.26,d),'walktimber',parent=parent)
    for sign in [-1,1]:
        # Overlapping side rails guide passage on the main run; deck opens on its garden side.
        beam('DeckOuterRail'+str(sign),(x+sign*w/2,z-d/2,HEIGHT+1.1),(x+sign*w/2,z+d/2,HEIGHT+1.1),.16,.16,solid=True)
        for end in [-1,1]:
            box(f'DeckCorner{sign}_{end}',(x+sign*w/2,(HEIGHT+1.25)/2,z+end*d/2),(.25,HEIGHT+1.25,.25),'walktimber',parent=parent)
            # End rails stop at the walkway opening.
            beam(f'DeckEndRail{sign}_{end}',(x+sign*1.7,z+end*d/2,HEIGHT+1.1),(x+sign*w/2,z+end*d/2,HEIGHT+1.1),.16,.16,solid=True)
    for j in range(20):visual('DeckPlankJoint'+str(j),(x,HEIGHT+.008,z-d/2+(j+.5)*d/20),(w-.08,.008,.015),'walkgrain')
    for j,p in enumerate(WALKWAY[1:-1]):
        box('WalkCornerLanding'+str(j),(p[0],HEIGHT-.13,p[1]),(3.3,.26,3.3),'walktimber',parent=parent)
    a,b=STAIRS;count=28
    for j in range(count):
        t=(j+.5)/count;x,z=a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t;top=HEIGHT*(j+1)/count
        box('GrasslandStair'+str(j),(x,top/2,z),(3.2,top,18/count+.025),'walktimber',solid=False,parent=parent)
        visual('StairNosing'+str(j),(x,top+.004,z+.28),(3.16,.008,.06),'walkgrain')
    beam('StairWalkSurface',(a[0],a[1],-.13),(b[0],b[1],HEIGHT-.13),3.2,.26,solid=True)
    g['nodes'][-3]+='\nvisible = false'
    for sign in [-1,1]:
        for rise in [.55,1.1]:beam(f'StairRail{sign}_{rise}',(a[0]+sign*1.62,a[1],rise),(b[0]+sign*1.62,b[1],HEIGHT+rise),.13,.13,solid=True)
        for j in range(9):
            t=j/8;y=HEIGHT*t;z=a[1]+(b[1]-a[1])*t
            box(f'StairPost{sign}_{j}',(a[0]+sign*1.62,(y+1.25)/2,z),(.2,y+1.25,.2),'walktimber',parent=parent)
    return {'pockets':POCKETS,'row_trees':len(trees()),'hedge_segments':len(hedges()),'tall_grass_patches':len(grass_patches()),'grass_cards':len(blades),'flower_cards':len(flowercards),'boulders':len(rocks),'sculpted_ridge':terrain,'walkway_height_m':HEIGHT,'walkway':WALKWAY,'stairs':STAIRS,'ramp':RAMP,'deck':DECK}
