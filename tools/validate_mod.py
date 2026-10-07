"""Check every shipped config, path, sprite strip, biome reference and ID."""
import json,sys,re,csv
from pathlib import Path
from PIL import Image,ImageChops,ImageFilter
from art import anchor,SOURCE
from read_pck import Pack
root=Path(__file__).resolve().parents[1];out=root/'dist/Touma/SafariZone';p=Pack(sys.argv[1])
vanilla={};errors=[]
for n in p.files:
 if n.startswith('Config/') and n.endswith('.json'):
  d=json.loads(p.read(n));info=d.get('config_info',{});vanilla[info.get('config_instance_id')]=info.get('config_type_id')
configs=[json.loads(n.read_text()) for n in out.glob('*.json')];ids={}
for d in configs:
 info=d['config_info'];i=info['config_instance_id'];assert i not in vanilla and i not in ids,('ID collision',i);ids[i]=info['config_type_id']
allids=vanilla|ids
base_strings={int(i) for i in json.loads(p.read('Config/LocalizationIdTable_IdTable.json'))['ids_to_slugs']}
localization=next(d for d in configs if d['config_info']['config_type_id']=='LocaleExtension');strings={t['id'] for t in localization['ids_to_translations']}
assert not strings & base_strings, 'Localization ID collision'
assert len(strings)==len(localization['ids_to_translations'])
def walk(v):
 if isinstance(v,dict):
  if 'path' in v and v['path']:
   path=v['path']
   if path.startswith('mods://'):assert (root/'dist'/path[7:]).is_file(),path
   elif path.startswith('res://'):assert any(path[6:]+suffix in p.files for suffix in ['','.import','.remap']),path
  for k,x in v.items():
   if k in ['name','display_name','description'] and isinstance(x,dict) and x.get('id'):assert x['id'] in strings or x['id'] in allids or d['config_info']['config_type_id']=='BirdSpecies' and k=='special_pose_name'
   walk(x)
 elif isinstance(v,list):
  for x in v:walk(x)
for d in configs:
 walk(d)
 if d['config_info']['config_type_id']=='BirdSpecies':
  for i in d['preferred_biomes']:assert ids[i]=='Biome'
  for i in d['preferred_seeds']:assert i in allids
  assert allids[d['rarity']]=='Rarity'
  for e in d['supported_perch_points_weights']:assert allids[e['perch_point']]=='PerchPointType' and e['weight']>0
for folder in (out/'birds').iterdir():
 for file,count in [('head.png',3),('body.png',5)]:
  im=Image.open(folder/file);assert im.mode=='RGBA' and im.size==((450,150) if count==3 else (2000,400)),(folder,file,im.size)
  for j in range(count):assert im.crop((j*im.width//count,0,(j+1)*im.width//count,im.height)).getbbox()
 if (SOURCE/folder.name/'layout.json').exists():
  hx,hy=anchor({'name':folder.name})
  heads=Image.open(folder/'head.png');bodies=Image.open(folder/'body.png')
  for pose in range(5):
   head_poses=range(3) if folder.name in {'Noctowl','Dustox','Gligar','Talonflame','Ho-Oh','Yveltal','Yanma'} else [0 if pose<3 else pose-2]
   for head_pose in head_poses:
    head_frame=heads.crop((head_pose*150,0,(head_pose+1)*150,150))
    registered=Image.new('RGBA',(400,400));registered.alpha_composite(head_frame,(125 if pose>=3 else round(hx)-75,round(hy)-75))
    head_mask=registered.getchannel('A').point(lambda a:255 if a>=128 else 0)
    body_mask=bodies.crop((pose*400,0,(pose+1)*400,400)).getchannel('A').point(lambda a:255 if a>=128 else 0)
    assert ImageChops.multiply(head_mask.filter(ImageFilter.MaxFilter(7)),body_mask).getbbox(),(folder.name,pose,head_pose,'Detached head/neck gap exceeds three pixels')

from scene_assets import check_resource
custom={}
for asset_pack in out.glob('*_assets.pck'):
 exported=Pack(asset_pack)
 custom.update({name:exported.read(name) for name in exported.files})
for path in re.findall(r'path="(res://[^"]+)"',(out/'SafariZone.tscn').read_text()):check_resource(path,p.files,custom)
birds=[d for d in configs if d['config_info']['config_type_id']=='BirdSpecies']
roster=list(csv.DictReader((root/'data/roster.csv').open()))
assert {d['scientific_name'] for d in birds}=={f"Pokémon #{int(r['dex']):03d} · Generation {1 if int(r['dex'])<=151 else 2 if int(r['dex'])<=251 else 3 if int(r['dex'])<=386 else 4 if int(r['dex'])<=493 else 5 if int(r['dex'])<=649 else 6 if int(r['dex'])<=721 else 7 if int(r['dex'])<=809 else 8}" for r in roster}
assert len(birds)==len(roster)
active_names={r['name'] for r in roster}
assert {f.name for f in (out/'birds').iterdir()}==active_names,'Retired or missing species artwork'
assert {f.stem[len('BirdSpecies_'):] for f in out.glob('BirdSpecies_*.json')}==active_names,'Retired or missing species configs'
print(f'PASS: {len(configs)} configs; {len(birds)} birds; 4 biome references; {len(strings)} localized strings; all asset paths, strips, and IDs checked against installed game.')
