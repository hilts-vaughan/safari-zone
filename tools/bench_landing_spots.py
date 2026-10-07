"""Flat native landing areas inset into bench slats and backrest tops."""
def add(g,name,seats,back):
    for i,(x,y,z,w,d) in enumerate(seats+[back]):
        g['prefab'](name+'Landing'+str(i),'FunctionalObjects/RockHangout',
                    (x,y+.01,z),(w-.12,1,max(.06,d-.03)))

def build(g):
    box=g['box'];node=g['node'];node('JunctionBenches','Node3D','.')
    for i,(x,z) in enumerate([(-85,52),(-64,48),(-48,65)]):
        for j in range(4):box(f'GardenBench{i}Seat{j}',(x,.6,z-.45+j*.28),(3.6,.14,.22),'plank',parent='JunctionBenches')
        for j in range(3):box(f'GardenBench{i}Back{j}',(x,.95+j*.24,z-.65),(3.6,.18,.12),'plank',parent='JunctionBenches')
        for side in [-1,1]:
            box(f'GardenBench{i}Leg{side}',(x+side*1.25,.26,z),(.12,.52,.8),'iron',parent='JunctionBenches')
            box(f'GardenBench{i}Support{side}',(x+side*1.25,.9,z-.7),(.12,1.3,.12),'iron',parent='JunctionBenches')
        add(g,'GardenBench'+str(i),[(x,.67,z-.45+j*.28,3.6,.22) for j in range(4)],(x,1.52,z-.65,3.6,.12))
    return {'new_benches':3,'existing_benches_supported':7}
