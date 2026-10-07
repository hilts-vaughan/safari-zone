"""Crop and register saved Imagegen components using reviewed attachment points.

No character geometry is drawn here. Original generated pixels and alpha are
preserved; only crops, uniform resampling and placement form native strips.
"""
import argparse
import json
from pathlib import Path
from PIL import Image
from art import ROOT, SOURCE


def extract(image,box,regions=None):
 if regions:
  tile=Image.new('RGBA',(box[2]-box[0],box[3]-box[1]))
  for region in regions:
   if not (box[0]<=region[0]<region[2]<=box[2] and box[1]<=region[1]<region[3]<=box[3]):
    raise ValueError('Crop region is outside its component box')
   tile.alpha_composite(image.crop(tuple(region)),(region[0]-box[0],region[1]-box[1]))
 else:tile=image.crop(tuple(box))
 # Near-transparent RGB noise must not determine crop bounds. Alpha is retained.
 core=tile.getchannel('A').point(lambda a:255 if a>=128 else 0)
 bounds=core.getbbox()
 if not bounds:raise ValueError('Component contains no visible pixels')
 return tile.crop(bounds),(box[0]+bounds[0],box[1]+bounds[1])


def placed(image,part,size,target,scale):
 tile,origin=extract(image,part['box'],part.get('regions'))
 tile=tile.resize((round(tile.width*scale),round(tile.height*scale)),Image.Resampling.LANCZOS)
 pivot=part['pivot'];left=round(target[0]-(pivot[0]-origin[0])*scale);top=round(target[1]-(pivot[1]-origin[1])*scale)
 core=tile.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()
 if left+core[0]<0 or top+core[1]<0 or left+core[2]>size[0] or top+core[3]>size[1]:
  raise ValueError(f'Visible component would be clipped: {left,top,core,size}')
 frame=Image.new('RGBA',size);frame.alpha_composite(tile,(left,top))
 return frame


def pack(species):
 directory=ROOT/'assets/imagegen'/species
 plan=json.loads((directory/'layout.json').read_text())
 image=Image.open(directory/plan.get('source_image','components.png')).convert('RGBA')
 scale=plan['scale'];neck=plan['neck'];pivot=plan.get('head_pivot',[75,115])
 center=[neck[0]-(pivot[0]-75),neck[1]-(pivot[1]-75)]
 heads=[placed(image,part,(150,150),part.get('target',pivot),plan.get('head_scale',scale)) for part in plan['heads']]
 bodies=[placed(image,part,(400,400),(200,neck[1]) if i>=3 else neck,part.get('scale',scale)) for i,part in enumerate(plan['bodies'])]
 mock=bodies[0].copy();mock.alpha_composite(heads[0],(round(center[0])-75,round(center[1])-75))
 strip_h=Image.new('RGBA',(450,150));strip_b=Image.new('RGBA',(2000,400))
 for i,frame in enumerate(heads):strip_h.alpha_composite(frame,(i*150,0))
 for i,frame in enumerate(bodies):strip_b.alpha_composite(frame,(i*400,0))
 dest=SOURCE/species;dest.mkdir(parents=True,exist_ok=True)
 strip_h.save(dest/'head.png');strip_b.save(dest/'body.png');mock.save(dest/'mockup.png')
 (dest/'layout.json').write_text(json.dumps({'head_center':center,'method':'Imagegen components, cropped and uniformly registered','source':str(directory.relative_to(ROOT))},indent=2)+'\n')
 provenance=json.loads((SOURCE/'provenance.json').read_text())
 provenance['species'][species]={'method':'built-in Imagegen','replacement_status':'packed; runtime review pending','source':str(directory.relative_to(ROOT))}
 (SOURCE/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
 print(f'Packed {species}: 3 head frames, 5 body frames; head center {center}')


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('species');pack(parser.parse_args().species)
