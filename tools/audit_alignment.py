"""Audit native Sprite3D perch clearance without changing saved character artwork."""
import csv,json,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
HOVER={'Yanmega','Volbeat','Illumise','Mothim','Vivillon','Combee','Butterfree','Ledyba','Beautifly','Dustox','Masquerain','Yanma','Volcarona'}
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
  target=max(bottoms);shifts=[0,0,0]
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
    if name in {'Noctowl','Dustox','Gligar','Talonflame','Ho-Oh','Yveltal','Yanma'}:
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
    packed.save(folder/'body.png')
  origin=round((target-200)/100+clearance,4)
  if name=='Psyduck':origin=layout.get('body_position_y',0)
  layout['body_position_y']=origin
  layout['alignment_policy']='waterline' if name=='Psyduck' else 'per-view registration; insect hover clearance' if name in HOVER else 'per-view registration'
  if name in {'Noctowl','Dustox','Gligar','Talonflame','Ho-Oh','Yveltal','Yanma'}:layout['head_turn_alignment']='All head frames share the side-head neck baseline; independent head/body turns supported'
  (folder/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')
  report.append({'name':name,'source_rest_bottom_pixels':bottoms,'rest_bottom_pixels':[bottoms[i]+shifts[i] for i in range(3)],'pose_translation_pixels':shifts,'body_position_y':origin,'clearance_before_species_scale':[round(origin+(200-bottoms[i]-shifts[i])/100,4) for i in range(3)],'waterline_exception':name=='Psyduck'})
 (ROOT/'docs/bird-alignment-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 from art import composite
 for row in csv.DictReader((ROOT/'data/roster.csv').open()):composite(row).save(ROOT/'assets/birds'/row['name']/'mockup.png')
 print(f'Audited {len(report)} species, three resting views each; kept floating duck waterline.')
if __name__=='__main__':main()
