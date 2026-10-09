"""Audit native Sprite3D perch clearance without changing saved character artwork."""
import csv,json,shutil
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
HOVER={'Yanmega','Volbeat','Illumise','Mothim','Vivillon','Combee','Butterfree','Ledyba','Beautifly','Dustox','Masquerain','Yanma','Volcarona'}
def attachment_mask(image):
 # Exclude tiny detached flecks when measuring the actual neck connection.
 mask=image.getchannel('A').point(lambda a:255 if a>=128 else 0)
 w,h=mask.size;pixels=mask.load();seen=set();result=Image.new('L',(w,h));dest=result.load();largest=[]
 for y in range(h):
  for x in range(w):
   if not pixels[x,y] or (x,y) in seen:continue
   pending=[(x,y)];seen.add((x,y));component=[]
   while pending:
    a,b=pending.pop();component.append((a,b))
    for c,d in ((a-1,b),(a+1,b),(a,b-1),(a,b+1)):
     if 0<=c<w and 0<=d<h and pixels[c,d] and (c,d) not in seen:seen.add((c,d));pending.append((c,d))
   if len(component)>len(largest):largest=component
 for a,b in largest:dest[a,b]=255
 return result

def main():
 report=[]
 for row in csv.DictReader((ROOT/'data/roster.csv').open()):
  name=row['name'];folder=ROOT/'assets/birds'/name
  original=ROOT/'assets/alignment-originals'/name
  original.mkdir(parents=True,exist_ok=True)
  for file in ('layout.json','head.png','body.png'):
   if not (original/file).exists():shutil.copyfile(folder/file,original/file)
  layout=json.loads((original/'layout.json').read_text())
  with Image.open(original/'body.png') as strip:
   bottoms=[]
   for frame in (0,3,4):
    alpha=strip.crop((frame*400,0,(frame+1)*400,400)).getchannel('A').point(lambda v:255 if v>=128 else 0)
    bounds=alpha.getbbox();bottoms.append(bounds[3] if bounds else 200)
  # Native centered frames use .01 m/pixel, prior to species scale.
  # Use the lowest opaque point across every resting direction, so none sinks.
  clearance=.12 if name in HOVER else .025
  target=max(bottoms);shifts=[0,0,0];turn_shifts=[0]*5
  if name!='Psyduck':
   with Image.open(original/'head.png') as heads:
    bounds=[heads.crop((i*150,0,(i+1)*150,150)).getbbox() for i in range(3)]
    lower=max(bottoms[i]-bounds[i][1] for i in range(3))
    upper=min(bottoms[i]+150-bounds[i][3] for i in range(3))
    if lower>upper:raise ValueError('Head registration cannot fit '+name)
    target=min(upper,max(lower,sorted(bottoms)[1]))
    shifts=[target-b for b in bottoms]
    packed=Image.new('RGBA',heads.size)
    for i,delta in enumerate(shifts):packed.alpha_composite(heads.crop((i*150,0,(i+1)*150,150)),(i*150,delta))
    # Head turns are independent of body direction. These species need a
    # shared neck baseline across head frames, even after foot registration.
    if name in {'Noctowl','Dustox','Gligar','Talonflame','Ho-Oh','Yveltal','Yanma','Masquerain','Fearow','Dodrio','Zapdos'}:
     frames=[packed.crop((i*150,0,(i+1)*150,150)) for i in range(3)]
     core_bounds=[f.getchannel('A').point(lambda v:255 if v>=128 else 0).getbbox() for f in frames]
     neck_bottom=core_bounds[0][3]
     registered=Image.new('RGBA',packed.size)
     for i,frame in enumerate(frames):
      delta=neck_bottom-core_bounds[i][3]
      if core_bounds[i][1]+delta<0 or core_bounds[i][3]+delta>150:raise ValueError('Head turn registration clips '+name)
      registered.alpha_composite(frame,(i*150,delta))
     packed=registered
    packed.save(folder/'head.png')
   with Image.open(original/'body.png') as bodies:
    packed=Image.new('RGBA',bodies.size)
    for i in range(5):
     delta=shifts[0 if i<3 else i-2]
     frame=bodies.crop((i*400,0,(i+1)*400,400))
     b=frame.getbbox()
     if b[1]+delta<0 or b[3]+delta>400:raise ValueError('Body registration clips '+name)
     packed.alpha_composite(frame,(i*400,delta))
    if name in {'Masquerain','Fearow','Dodrio','Zapdos'}:
     # Native heads turn independently. Register each body against all three
     # head silhouettes, preserving anatomy and keeping feet above the origin.
     head_strip=Image.open(folder/'head.png')
     for pose in range(5):
      frame=packed.crop((pose*400,0,(pose+1)*400,400))
      masks=[]
      for head_pose in range(3):
       canvas=Image.new('RGBA',(400,400))
       canvas.alpha_composite(head_strip.crop((head_pose*150,0,(head_pose+1)*150,150)),(125 if pose>=3 else layout['head_center'][0]-75,layout['head_center'][1]-75))
       masks.append(attachment_mask(canvas))
      for delta in sorted(range(-35,1),key=abs):
       shifted=Image.new('RGBA',(400,400));shifted.alpha_composite(frame,(0,delta))
       mask=attachment_mask(shifted)
       # Ignore isolated antialiasing pixels: require a substantial attachment.
       if all(ImageChops.multiply(h,mask).histogram()[255]>=8 for h in masks):break
      else:raise ValueError('Independent head turn remains detached: '+name+' '+str(pose))
      packed.paste(shifted,(pose*400,0));turn_shifts[pose]=delta
     # Keep all resting feet on one baseline after neck correction.
     rest_delta=min(turn_shifts[i] for i in (0,3,4))
     for pose in (0,3,4):
      frame=packed.crop((pose*400,0,(pose+1)*400,400))
      shifted=Image.new('RGBA',(400,400));shifted.alpha_composite(frame,(0,rest_delta-turn_shifts[pose]))
      packed.paste(shifted,(pose*400,0));turn_shifts[pose]=rest_delta
    packed.save(folder/'body.png')
  origin=round((target-200)/100+clearance,4)
  if name=='Psyduck':
   layout=json.loads((folder/'layout.json').read_text())
   origin=layout.get('body_position_y',0)
  layout['body_position_y']=origin
  if name in {'Masquerain','Fearow','Dodrio','Zapdos'}:layout['independent_turn_body_translation_pixels']=turn_shifts
  layout['alignment_policy']='waterline' if name=='Psyduck' else 'per-view registration; insect hover clearance' if name in HOVER else 'per-view registration'
  if name in {'Noctowl','Dustox','Gligar','Talonflame','Ho-Oh','Yveltal','Yanma','Masquerain','Fearow','Dodrio','Zapdos'}:layout['head_turn_alignment']='All head frames share the side-head neck baseline; independent head/body turns supported'
  (folder/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')
  report.append({'name':name,'source_rest_bottom_pixels':bottoms,'rest_bottom_pixels':[bottoms[i]+shifts[i]+turn_shifts[(0,3,4)[i]] for i in range(3)],'pose_translation_pixels':shifts,'independent_turn_body_translation_pixels':turn_shifts,'body_position_y':origin,'clearance_before_species_scale':[round(origin+(200-bottoms[i]-shifts[i]-turn_shifts[(0,3,4)[i]])/100,4) for i in range(3)],'waterline_exception':name=='Psyduck'})
 (ROOT/'docs/bird-alignment-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 from art import composite
 for row in csv.DictReader((ROOT/'data/roster.csv').open()):composite(row).save(ROOT/'assets/birds'/row['name']/'mockup.png')
 print(f'Audited {len(report)} species, three resting views each; kept floating duck waterline.')
if __name__=='__main__':main()
