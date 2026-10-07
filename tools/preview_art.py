"""Render review boards for every species and every native sprite pose."""
import csv,math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from art import composite,SOURCE

ROOT=Path(__file__).resolve().parents[1]
LABELS=['Side','Wings up','Wings down','Front','Back']


def main():
 roster=list(csv.DictReader((ROOT/'data/roster.csv').open()))
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
 board=Image.new('RGB',(1440,math.ceil(len(roster)/6)*240),'#e8eee7');draw=ImageDraw.Draw(board)
 poses=Image.new('RGB',(5*240,len(roster)*230),'#e8eee7');pd=ImageDraw.Draw(poses)
 updated=[r for r in roster if (SOURCE/r['name']/'layout.json').exists()]
 fresh=Image.new('RGB',(5*240,((len(updated)+4)//5)*240),'#e8eee7');fd=ImageDraw.Draw(fresh)
 for i,r in enumerate(roster):
  for pose in range(5):
   sprite=composite(r,pose)
   sprite=sprite.crop(sprite.getbbox());sprite.thumbnail((202,177),Image.Resampling.LANCZOS)
   x=pose*240+(240-sprite.width)//2;y=i*230+30
   poses.paste(sprite,(x,y),sprite)
   pd.text((pose*240+12,i*230+7),r['name']+' / '+LABELS[pose],font=font,fill='#303342')
   if pose==0:
    xx=(i%6)*240;yy=(i//6)*240
    board.paste(sprite,(xx+(240-sprite.width)//2,yy+27),sprite)
    draw.text((xx+12,yy+207),f"#{int(r['dex']):03d} {r['name']}",font=font,fill='#303342')
    status='Imagegen' if r in updated else 'Previous artwork'
    draw.text((xx+12,yy+226),status,font=font,fill='#367755' if r in updated else '#68736c')
    if r in updated:
     j=updated.index(r);fx=(j%5)*240;fy=(j//5)*240
     fresh.paste(sprite,(fx+(240-sprite.width)//2,fy+27),sprite)
     fd.text((fx+12,fy+207),r['name'],font=font,fill='#303342')
 board.save(ROOT/'docs/roster-preview.png')
 poses.save(ROOT/'docs/roster-poses.png')
 fresh.save(ROOT/'docs/imagegen-roster-preview.png')
 print(f'Rendered {len(roster)} species and all {len(roster)*5} head/body pose composites.')


if __name__=='__main__':main()
