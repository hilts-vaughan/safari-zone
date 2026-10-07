"""Pack saved artwork; builds never draw or regenerate character designs.

Imagegen replacements are saved beneath assets/birds after visual review.
Existing released artwork remains there until a replacement is ready.
"""
import shutil
import json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/birds'


def anchor(r):
 layout=SOURCE/r['name']/'layout.json'
 return tuple(json.loads(layout.read_text())['head_center']) if layout.exists() else (160,112)


def head(r,pose):
 with Image.open(SOURCE/r['name']/'head.png') as strip:
  return strip.crop((pose*150,0,(pose+1)*150,150))


def body(r,pose):
 with Image.open(SOURCE/r['name']/'body.png') as strip:
  return strip.crop((pose*400,0,(pose+1)*400,400))


def composite(r,pose=0):
 im=body(r,pose)
 x,y=anchor(r)
 im.alpha_composite(head(r,0 if pose<3 else pose-2),(125 if pose>=3 else round(x)-75,round(y)-75))
 return im


def render(r,path):
 path.mkdir(parents=True,exist_ok=True)
 for name in ['head.png','body.png','mockup.png','call.wav']:
  shutil.copyfile(SOURCE/r['name']/name,path/name)
