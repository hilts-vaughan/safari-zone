"""Extra supported park perches; small stems leave the footpaths open."""
import math

def flat(g,name,pos,width,depth):
    g['prefab'](name,'FunctionalObjects/RockHangout',pos,(width,1,depth))

def rail(g,name,a,b,width,parent):
    dx,dy,dz=[b[i]-a[i] for i in range(3)]
    length=math.sqrt(dx*dx+dy*dy+dz*dz)
    angle=math.degrees(math.atan2(dx,dz));slope=-math.degrees(math.atan2(dy,math.hypot(dx,dz)))
    ref=g['resource']('res://Scenes/FunctionalObjects/RockHangout.tscn','PackedScene')
    mid=tuple((a[i]+b[i])/2+(width/2+.01 if i==1 else 0) for i in range(3))
    g['node'](name,None,parent,f'position = {g["vec"](mid)}\nrotation_degrees = Vector3({slope},{angle},0)\nscale = {g["vec"]((width*.7,1,max(.1,length-.2)))}',ref)

def build(g):
    g['node']('GrasslandStumps','Node3D','.')
    for i,(x,z,h) in enumerate([(-102,31,.65),(-79,30,.8),(-35,38,.55),(-69,38,.7)]):
        mesh=g['sub']('CylinderMesh',f'top_radius = 0.36\nbottom_radius = 0.46\nheight = {h}\nradial_segments = 7')
        g['node']('Stump'+str(i),'MeshInstance3D','GrasslandStumps',f'position = {g["vec"]((x,h/2,z))}\nmesh = {mesh}\nmaterial_override = {g["mats"]["arrivaldark"]}')
        shape=g['sub']('CylinderShape3D',f'radius = 0.4\nheight = {h}')
        g['node']('StumpBody'+str(i),'StaticBody3D','GrasslandStumps',f'position = {g["vec"]((x,h/2,z))}\ncollision_layer = 11\ncollision_mask = 0')
        g['node']('Shape','CollisionShape3D','GrasslandStumps/StumpBody'+str(i),'shape = '+shape)
        flat(g,'StumpLanding'+str(i),(x,h+.01,z),.42,.42)
    return {'stumps':4}
