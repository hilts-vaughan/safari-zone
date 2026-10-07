"""Audit active sprite silhouettes at a shared scale; never resize each bird to fit."""
import csv,json,math
from pathlib import Path
from PIL import Image,ImageDraw
from art import composite
ROOT=Path(__file__).resolve().parents[1]
def main():
 rows=list(csv.DictReader((ROOT/'data/roster.csv').open()));records=[]
 board=Image.new('RGB',(1600,math.ceil(len(rows)/4)*400),'#e8eee7');draw=ImageDraw.Draw(board)
 for index,row in enumerate(rows):
  scale=float(row['scale']);poses=[]
  for pose in range(5):
   sprite=composite(row,pose);bounds=sprite.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()
   poses.append({'pose':pose,'bounds_px':list(bounds),'scaled_width_px':round((bounds[2]-bounds[0])*scale,2),'scaled_height_px':round((bounds[3]-bounds[1])*scale,2)})
  records.append({'name':row['name'],'scale':scale,'poses':poses})
  sprite=composite(row,0);bounds=poses[0]['bounds_px'];sprite=sprite.crop(bounds)
  sprite=sprite.resize((round(sprite.width*scale*.65),round(sprite.height*scale*.65)),Image.Resampling.LANCZOS)
  x=index%4*400;y=index//4*400
  board.paste(sprite,(x+200-sprite.width//2,y+310-sprite.height),sprite)
  draw.line((x+15,y+310,x+385,y+310),fill='#a9b7aa')
  draw.text((x+15,y+325),f"{row['name']} | scale {scale:.3f}",fill='#303342')
  draw.text((x+15,y+345),f"Side silhouette: {poses[0]['scaled_width_px']:.0f} x {poses[0]['scaled_height_px']:.0f} scaled px",fill='#303342')
 report={'method':'Alpha >= 128 bounds of assembled head/body across all five poses, multiplied by native visuals_scale_factor. Units are scaled texture pixels, not asserted world metres. Board uses one shared 0.65 display factor and ground baseline. Animated head turning/bobbing is excluded.','species':records}
 (ROOT/'docs/bird-size-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 board.save(ROOT/'docs/bird-size-comparison.png')
 print(f'Audited {len(records)} species, {len(records)*5} poses.')
if __name__=='__main__':main()
