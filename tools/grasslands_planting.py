"""Organic meadow islands with deterministic path, trunk and walkway clearance."""
import math,random
from functools import lru_cache
from grasslands_layout import POCKETS,trees,WALKWAY,STAIRS,RAMP,DECK

@lru_cache(maxsize=1)
def placements():
 from map_layout import path_distance,segment_distance,inside
 from frontage_scene import contains as in_frontage
 rng=random.Random(33704);grass=[];flowers=[];rocks=[]
 # Interior meadow islands plus the bare transition lawn on the Center side.
 beds=[(x+dx,z+dz,5.8,6.5) for x,z,_,_ in POCKETS for dx in [-5,5] for dz in [-5,5]]
 beds += [(-91,65,6,6),(-110,69,8,6),(-53,64,6,5),(-111,68,7,4),(-101,70,5,4),(-84,68,8,3.5),(-64,69,7,4),(-36,67,7,3.5),(-25,39,3,10)]
 routes=list(zip(WALKWAY,WALKWAY[1:]))+[STAIRS]
 trunks=[(x,z) for x,z,_ in trees()]
 def clear(x,z,margin=2.8):
  p=(x,z)
  return (inside(p) and path_distance(p)>margin and not (-83<x<-57 and 65<z<79) and z<76
          and min(segment_distance(p,a[:2],b[:2]) for a,b in routes)>2.8
          and min(math.dist(p,t) for t in trunks)>1.1
          and not (-134<x<-124 and 24<z<36))
 for bed,(x,z,rx,rz) in enumerate(beds):
  for ix in range(math.ceil(rx*2/.5)):
   for iz in range(math.ceil(rz*2/.5)):
    px=x-rx+(ix+.5)*.5+rng.uniform(-.12,.12);pz=z-rz+(iz+.5)*.5+rng.uniform(-.12,.12)
    d=((px-x)/rx)**2+((pz-z)/rz)**2
    edge=1+.12*math.sin(px*.8+pz*.7)
    if d>edge or not clear(px,pz):continue
    if d>.65 and rng.random()<.48 or rng.random()<.075:
     flowers.append((px,pz,rng.uniform(.7,1.0),rng.uniform(0,math.pi)))
    else:grass.append((px,pz,rng.uniform(1.05,1.55),rng.uniform(0,math.pi)))
  px,pz=x+rx*.4,z+rz*.2
  if clear(px,pz,4):rocks.append((px,pz,rng.uniform(1.8,2.7),rng.uniform(.9,1.4)))
 # Visible flowering fringe outside the low hedge ribbons.
 for x,z,rx,rz in POCKETS:
  for j in range(140):
   angle=rng.uniform(0,2*math.pi);r=rng.uniform(1.08,1.2)
   px=x+rx*r*math.cos(angle);pz=z+rz*r*math.sin(angle)
   if clear(px,pz):flowers.append((px,pz,rng.uniform(.65,.95),rng.uniform(0,math.pi)))
 # Keep flower cards clear of boulder silhouettes.
 grass=[p for p in grass if all(math.dist(p[:2],r[:2])>r[2]*.5 for r in rocks)]
 flowers=[p for p in flowers if all(math.dist(p[:2],r[:2])>r[2]*.45 for r in rocks)]
 return grass,flowers,rocks
