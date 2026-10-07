"""Authored grassland pockets and the elevated observation loop, in world metres."""
import math

POCKETS = [(-107, 35, 12, 16), (-74, 34, 12, 15), (-40, 34, 12, 14)]
HEIGHT = 3.5
WALKWAY = [(-129, 41, HEIGHT), (-129, 17, HEIGHT), (-122, 7, HEIGHT)]
STAIRS = ((-129, 59, 0), (-129, 41, HEIGHT))
RAMP = None
DECK = (-129, 30, 6.2, 8)

def contains(p, margin=0):
    return -149-margin < p[0] < -18+margin and 4-margin < p[1] < 64+margin

def hedges():
    """Continuous ellipse borders with two human-sized entrances per pocket."""
    result = []
    for pocket, (x, z, rx, rz) in enumerate(POCKETS):
        for i in range(56):
            t = 2*math.pi*(i+.5)/56
            # Leave north/south openings ~4.3m wide, not incidental cracks.
            if abs(math.cos(t)) < .19:
                continue
            a = (x+rx*math.cos(2*math.pi*i/56), z+rz*math.sin(2*math.pi*i/56))
            b = (x+rx*math.cos(2*math.pi*(i+1)/56), z+rz*math.sin(2*math.pi*(i+1)/56))
            result.append((pocket, a, b))
    return result

def trees():
    return [(x+dx, z+dz, pocket) for pocket,(x,z,_,_) in enumerate(POCKETS)
            for dx in [-5,5] for dz in [-8,0,8]]

def grass_patches():
    # Separate patches, leaving a clear central lane and space at tree trunks.
    return [(x+dx, z+dz, 5.2, 4.4, pocket) for pocket,(x,z,_,_) in enumerate(POCKETS)
            for dx in [-5,5] for dz in [-4,4]]

def walkway_samples(spacing=.6):
    points=[]
    for a,b in list(zip(WALKWAY,WALKWAY[1:]))+[STAIRS]:
        count=math.ceil(math.dist(a[:2],b[:2])/spacing)
        for i in range(count+1):
            t=i/count
            points.append([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t])
    return points
