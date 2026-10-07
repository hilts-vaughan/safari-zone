"""Deterministic reserve layout shared by scene generation, map and checks."""
import math,random,json
from woodland_section import contains as in_study
from gatehouse_scene import contains as in_gatehouse
from grasslands_layout import contains as in_grasslands
from frontage_scene import contains as in_frontage
from forest_gate_scene import contains as in_forest_checkpoint
from pathlib import Path
TARGET_AREA=168*168*2
FACILITIES={'grass':(-77,55),'forest':(-80,-43),'water':(64,45),'cliffs':(65,-48)}
WAYPOINTS={'entry':(-70,92),'centerwest':(-94,85),'centereast':(-50,85),'meadow':(-74,57),'westfork':(-23,15),'grove':(-113,-10),'forest':(-80,-43),'pond':(-52,-60),'woodlandapproach':(-5,-26),'woodlandwest':(-53,-43),'woodlandeast':(25,-45),'woodlandleftbranch':(-15,-43),'woodlandrightbranch':(5,-43),'northfork':(-5,-38),'hub':(-7,0),'southfork':(12,54),'gateapproach':(38,61),'gateentry':(38,55),'gateinterior':(38,47),'gateexit':(38,29),'wetland':(64,45),'marsh':(100,16),'ridge':(107,-39),'highland':(65,-48)}
WAYPOINTS['wetlandplaza']=(62,34)
WAYPOINTS.update(watergarden=(38,68),waterfall=(62,76),grottoleft=(51,63),grottoinside=(62,63),grottoright=(73,63))
WAYPOINTS.update(gatepicnicview=(38,36),gatepicnic=(38,28),gatepicnicleft=(33,23),gatepicnicright=(43,23))
WAYPOINTS['fountain']=(-74,-32)
WAYPOINTS['picnic']=(-65,-32)
WAYPOINTS['woodlandborder']=(-28,-26)
WAYPOINTS['highlandsreview']=(43,-55)
WAYPOINTS.update(grassoutereast=(-23,57),grasswest=(-123,57),grasswestnorth=(-123,15),grassnorthwest=(-107,14),grassnorthmiddle=(-74,14),grassnortheast=(-40,15),grasssouthwest=(-107,57),grasssouthmiddle=(-91,57),grasssouthright=(-57,57),grasssoutheast=(-40,57),grassleftfork=(-91,14),grassrightfork=(-57,14),grassstairapproach=(-123,62),grassstairs=(-129,62))
WAYPOINTS.update(forestgateapproach=(-111,5),forestgate=(-111,-3),forestgateexit=(-111,-11))
TRAILS=[['entry','centerwest','grasssouthwest','grasswest','grasswestnorth','grassnorthwest','grassleftfork','grassnorthmiddle','grassrightfork','grassnortheast','westfork','hub'],['entry','centereast','grasssoutheast','grassoutereast','westfork'],['grasssouthwest','grasssouthmiddle','meadow','grasssouthright','grasssoutheast','southfork'],['grasssouthmiddle','grassleftfork'],['grasssouthright','grassrightfork'],['grasswest','grassstairapproach','grassstairs'],['grassnorthwest','forestgateapproach','forestgate','forestgateexit','grove','forest','pond','woodlandwest','woodlandleftbranch','northfork'],['hub','woodlandapproach','northfork','woodlandrightbranch','woodlandeast','highland','ridge','marsh','wetland'],['hub','southfork','gateapproach','gateentry','gateinterior','gateexit','wetland'],['forest','woodlandwest','woodlandleftbranch','northfork'],['northfork','woodlandrightbranch','woodlandeast','marsh']]
PONDS=[(-48,-76,12,9),(82,68,9,7),(104,41,10,8),(36,75,8,6),(118,-2,7,5),(94,80,6,4),(111,67,6,5),(112,18,7,5)]

def area(points):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1])))/2

def outline(extended=True):
 p=[]
 for i in range(48):
  t=2*math.pi*i/48;r=1+.06*math.sin(3*t+.7)+.04*math.cos(5*t)
  p.append((165*r*math.cos(t),115*r*math.sin(t)))
 f=math.sqrt(TARGET_AREA/area(p));p=[(round(x*f,4),round(z*f,4)) for x,z in p]
 # Extend only the northeast perimeter to contain the new climbable terraces.
 # Original south/west coast, entrances and lake paths retain their vertices.
 return p[:37]+[(24,-119),(95,-119),(135,-105),(144,-70)]+p[46:] if extended else p

def inside(p,poly=None):
 poly=poly or outline();x,z=p;hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>z)!=(b[1]>z) and x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit

def segment_distance(p,a,b):
 dx,dz=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dz)/(dx*dx+dz*dz)))
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dz)

def segments():
 result=[]
 for trail in TRAILS:
  for a,b in zip(trail,trail[1:]):
   a,b=WAYPOINTS[a],WAYPOINTS[b]
   if a==b:continue
   dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
   bend=1.6*math.sin(a[0]*.2+b[1]*.17) if in_grasslands(a) and in_grasslands(b) and a[1]>10 and b[1]>10 and a[1]<59 and b[1]<59 else 0 if in_grasslands(a) and in_grasslands(b) or a==WAYPOINTS['northfork'] or b==WAYPOINTS['northfork'] or a==WAYPOINTS['woodlandwest'] or b==WAYPOINTS['woodlandwest'] or a==WAYPOINTS['woodlandeast'] or b==WAYPOINTS['woodlandeast'] or in_study(a) and in_study(b) or a in [WAYPOINTS["gateentry"],WAYPOINTS["gateinterior"],WAYPOINTS["gateexit"]] or b in [WAYPOINTS["gateentry"],WAYPOINTS["gateinterior"],WAYPOINTS["gateexit"]] else 6*math.sin(a[0]+b[1]);mid=((a[0]+b[0])/2-bend*dz/length,(a[1]+b[1])/2+bend*dx/length)
   points=[((1-t)**2*a[0]+2*(1-t)*t*mid[0]+t*t*b[0],(1-t)**2*a[1]+2*(1-t)*t*mid[1]+t*t*b[1]) for t in [i/8 for i in range(9)]]
   result.extend(zip(points,points[1:]))
 return result
def path_distance(p):return min(segment_distance(p,a,b) for a,b in segments())
def pond_contains(p,margin=0):return any(((p[0]-x)/(rx+margin))**2+((p[1]-z)/(rz+margin))**2<1 for x,z,rx,rz in PONDS)
def biome(p):
 x,z=p;vertical=12*math.sin(z/28);horizontal=-5+12*math.sin(x/42)
 return ('forest' if x<vertical else 'cliffs') if z<horizontal else ('grass' if x<vertical else 'water')
def clear(p,r=0):
 return not in_gatehouse(p,r) and not in_forest_checkpoint(p,r) and not (-95-r<p[0]<-45+r and 61-r<p[1]<97+r) and path_distance(p)>5+r and all(math.dist(p,c)>16+r for c in FACILITIES.values()) and not pond_contains(p,3+r) and not (55-r<p[0]<78+r and -82-r<p[1]<-62+r)

def layout():
 from enclosure_layout import blocked
 rng=random.Random(3862026);poly=outline();plantingpoly=outline(False);trees=[];shrubs=[];details=[]
 # Spatial jitter, border belts, and biome-dependent density replace uniform scatter.
 for x in range(-165,170,5):
  for z in range(-115,120,5):
   p=(x+rng.uniform(-2,2),z+rng.uniform(-2,2))
   if in_frontage(p,2) or in_grasslands(p,3) or in_study(p,2) or not inside(p,plantingpoly) or not clear(p,2) or blocked(p,2):continue
   k=biome(p);edge=min(segment_distance(p,a,b) for a,b in zip(plantingpoly,plantingpoly[1:]+plantingpoly[:1]))
   chance=.94 if edge<12 else {'forest':.94,'grass':.82,'water':.68,'cliffs':.62}[k]
   if rng.random()<chance:trees.append((p,k,rng.uniform(.85,1.35)))
   elif rng.random()<.55:shrubs.append((p,k,rng.uniform(.8,1.4)))
 for _ in range(1400):
  p=(rng.uniform(-165,165),rng.uniform(-115,115))
  if not in_frontage(p,2) and not (-135<p[0]<-101 and 76<p[1]<95) and not in_grasslands(p,2) and not in_gatehouse(p,2) and not in_study(p,.5) and inside(p,plantingpoly) and clear(p,.5) and not blocked(p,.5) and all(math.dist(p,t[0])>2 for t in trees):details.append((p,biome(p),rng.random()))
 return {'outline':poly,'area':area(poly),'trees':trees,'shrubs':shrubs,'details':details}

def preview(model,destination):
 from PIL import Image,ImageDraw,ImageFont
 im=Image.new('RGB',(1400,1050),'#e4e8dc');d=ImageDraw.Draw(im)
 def xy(p):return (700+p[0]*3.65,510+p[1]*3.65)
 d.polygon([xy(p) for p in model['outline']],fill='#91b66f',outline='#557f54',width=5)
 for p,k,_ in model['details']:
  c={'forest':'#6e975d','grass':'#b4c879','water':'#86a783','cliffs':'#c3b988'}[k];x,y=xy(p);d.ellipse((x-4,y-4,x+4,y+4),fill=c)
 for x,z,rx,rz in PONDS:
  a=xy((x-rx,z-rz));b=xy((x+rx,z+rz));d.ellipse((*a,*b),fill='#5ea9bd',outline='#aec895',width=7)
 from enclosure_layout import build_layout
 screens=build_layout()
 for h in screens['ridges']:
  x,y=xy(h['p']);r=h['radius']*3.65;d.ellipse((x-r,y-r,x+r,y+r),fill='#7b8178',outline='#638052',width=4)
 for kind,col in [('hedges','#3e7047'),('walls','#93968a')]:
  for h in screens[kind]:
   x,z=h['p'];a=math.radians(h['angle']);dx,dz=math.sin(a)*h['length']/2,math.cos(a)*h['length']/2
   d.line([xy((x-dx,z-dz)),xy((x+dx,z+dz))],fill=col,width=8)
 from woodland_section import plan,ORIGIN
 study=plan()
 for polygon in study['cliffs']:d.polygon([xy(p) for p in polygon],fill='#7b8178',outline='#638052',width=3)
 from grasslands_layout import hedges,trees,grass_patches,WALKWAY,STAIRS,RAMP
 for _,a,b in hedges():d.line([xy(a),xy(b)],fill='#46794b',width=5)
 for x,z,w,h,_ in grass_patches():d.rectangle((*xy((x-w/2,z-h/2)),*xy((x+w/2,z+h/2))),fill='#548448')
 for x,z,_ in trees():
  px,pz=xy((x,z));d.ellipse((px-9,pz-9,px+9,pz+9),fill='#47734d')
 for a,b in list(zip(WALKWAY,WALKWAY[1:]))+[STAIRS]:d.line([xy(a),xy(b)],fill='#a77c51',width=11)
 for a,b in segments():d.line([xy(a),xy(b)],fill='#dfce9f',width=12 if in_grasslands(((a[0]+b[0])/2,(a[1]+b[1])/2)) else 13 if in_study(((a[0]+b[0])/2,(a[1]+b[1])/2)) else 22)
 x,z=ORIGIN;d.ellipse((*xy((x+9,z-17)),*xy((x+25,z-7))),fill='#5ea9bd',outline='#aec895',width=3)
 for p in study['hedges']:
  x,y=xy(p);d.ellipse((x-7,y-5,x+7,y+5),fill='#3e7047')
 for p in study['trees']:
  x,y=xy(p);d.ellipse((x-9,y-9,x+9,y+9),fill='#47734d')
 for p,k,s in model['shrubs']:
  x,y=xy(p);d.ellipse((x-6,y-6,x+6,y+6),fill='#739653')
 for p,k,s in model['trees']:
  x,y=xy(p);d.ellipse((x-11*s,y-11*s,x+11*s,y+11*s),fill='#47734d',outline='#375f41',width=2)
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',23)
 for k,p in FACILITIES.items():
  x,y=xy(p);d.rounded_rectangle((x-16,y-10,x+16,y+10),4,fill='#846548');d.text((x-55,y+24),{'forest':'Forest Grove','grass':'Meadow','water':'Wetlands','cliffs':'Highlands'}[k],fill='#293f32',font=font)
 x,y=xy((38,42));d.rectangle((x-36,y-33,x+36,y+33),fill='#749263',outline='#e3dac3',width=3);d.text((x-75,y+37),'Gate · 50 stars',fill='#293f32',font=font)
 x,y=xy((-70,72));d.rounded_rectangle((x-40,y-18,x+40,y+18),4,fill='#ce6652');d.text((x-60,y-50),'Center',fill='#293f32',font=font)
 d.text((35,20),'Safari Zone — branching reserve',font=font,fill='#293f32');d.text((35,990),f'Ground area {model["area"]:,.0f} m² · 2× original · {len(model["trees"])} trees · {len(model["details"])} ground accents',font=font,fill='#293f32')
 im.save(destination)
