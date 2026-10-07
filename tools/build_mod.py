"""Build the complete local mod from the roster and installed config schemas."""
import csv,json,copy,sys,zlib,random,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from read_pck import Pack
from art import render,anchor
ROOT=Path(__file__).resolve().parents[1]
center_assets=ROOT/'editor/SceneEditor/EXTERNAL/Touma/SafariZone/Center'
center_assets.mkdir(parents=True,exist_ok=True)
for asset in (ROOT/'assets/environment/center').glob('*.png'):
 shutil.copyfile(asset,center_assets/asset.name)
woodland_assets=ROOT/'editor/SceneEditor/EXTERNAL/Touma/SafariZone/Woodland'
woodland_assets.mkdir(parents=True,exist_ok=True)
for scene in (ROOT/'assets/environment/woodland').glob('*.tscn'):shutil.copyfile(scene,woodland_assets/scene.name)
frontage_assets=ROOT/'editor/SceneEditor/EXTERNAL/Touma/SafariZone/Frontage'
frontage_assets.mkdir(parents=True,exist_ok=True)
for asset in (ROOT/'assets/environment/frontage').glob('*.png'):shutil.copyfile(asset,frontage_assets/asset.name)
OUT=ROOT/'dist/Touma/SafariZone'; OUT.mkdir(parents=True,exist_ok=True)
p=Pack(sys.argv[1])
def vanilla(n):return json.loads(p.read('Config/'+n+'.json'))
def uid(s):return zlib.crc32(('touma.safarizone.'+s).encode())
def save(typ,key,d):
 d['config_info']={'config_instance_id':uid(typ+'.'+key),'config_type_id':typ}
 (OUT/(typ+'_'+key+'.json')).write_text(json.dumps(d,indent=2)+'\n');return d['config_info']['config_instance_id']
strings={}
def loc(key,text):strings[key]=text;return {'id':uid('loc.'+key)}
zones=[('grass','Southwest Grasslands','Woodland',(-42,42),'#88ac62'),('water','Southeast Wetlands','Marsh',(42,42),'#72a5a0'),('forest','Northwest Forest','Woodland',(-42,-42),'#507d61'),('cliffs','Northeast Highlands','Bluff',(42,-42),'#b6ad8e')]
bids={}
for key,name,base,center,col in zones:
 d=vanilla('Biome_'+base);d['name']=loc('zone.'+key,name);d['special_items']=[]
 rgb=tuple(int(col[i:i+2],16)/255 for i in (1,3,5));d['primary_color']=dict(zip(['red','green','blue'],rgb));d['secondary_color']=dict(zip(['red','green','blue'],[v*.7 for v in rgb]))
 bids[key]=save('Biome',key,d)
roster=list(csv.DictReader(open(ROOT/'data/roster.csv')))
# Retire generated species outputs while retaining source artwork and all other assets.
active_names={r['name'] for r in roster}
for config in OUT.glob('BirdSpecies_*.json'):
 if config.stem[len('BirdSpecies_'):] not in active_names:config.unlink()
if (OUT/'birds').exists():
 for directory in (OUT/'birds').iterdir():
  if directory.name not in active_names:
   if directory.is_symlink():directory.unlink()
   elif directory.is_dir():shutil.rmtree(directory)
legend_rarity=vanilla('Rarity_4_Epic');legend_rarity['count_per_pool']=1;legend_rarity['name']=loc('rarity.highlegend','Rare visitor')
legend_rarity_id=save('Rarity','HighLegend',legend_rarity)
psyduck_rarity=vanilla('Rarity_1_Common');psyduck_rarity['count_per_pool']=1
psyduck_rarity['name']=loc('rarity.pondregular','Pond regular')
psyduck_rarity_id=save('Rarity','PondRegular',psyduck_rarity)
rare={'common':2346948767,'uncommon':2418968707,'rare':1803097666,'epic':619254682}
for r in roster:
 render(r,OUT/'birds'/r['name']);d=json.loads((ROOT/'editor/Samples/NotExplosive/MarshWren/BirdSpecies_MarshWren.json').read_text())
 d['display_name']=loc('bird.'+r['name']+'.name',r['name']);d['description']=loc('bird.'+r['name']+'.description',f"{r['name']} — Pokédex #{int(r['dex']):03d}. A Pokémon-inspired visitor to the {dict((z[0],z[1]) for z in zones)[r['zone']]}. Listen for its call and photograph its perched and flying poses.")
 d['scientific_name']=f"Pokémon #{int(r['dex']):03d} · Generation {1 if int(r['dex'])<=151 else 2 if int(r['dex'])<=251 else 3 if int(r['dex'])<=386 else 4 if int(r['dex'])<=493 else 5 if int(r['dex'])<=649 else 6 if int(r['dex'])<=721 else 7 if int(r['dex'])<=809 else 8}"
 for prop,file in [('head_texture','head.png'),('body_texture','body.png'),('mockup_texture','mockup.png')]:d[prop]={'path':f"mods://Touma/SafariZone/birds/{r['name']}/{file}"}
 hx,hy=anchor(r)
 d['visuals_scene']={'path':''};d['visuals_config']={'head_position_in_side_pose':{'x':round((hx-200)/100,4),'y':round((200-hy)/100,4)},'body_position_y':0}
 layout_path=ROOT/'assets/birds'/r['name']/'layout.json'
 origin_y=json.loads(layout_path.read_text()).get('body_position_y',0) if layout_path.exists() else 0
 d['visuals_config']['body_position_y']=origin_y
 d['visuals_config']['head_position_in_side_pose']['y']+=origin_y
 d['tweet_sounds']=[{'path':f"mods://Touma/SafariZone/birds/{r['name']}/call.wav"}]
 d['rarity']=rare[r['rarity']];d['preferred_biomes']=[bids[r['zone']]];d['visuals_scale_factor']=float(r['scale'])
 if r['name'] in ['Combee','Yanma']:d['preferred_biomes'].append(bids['forest'])
 if r['name']=='Vivillon':d['preferred_biomes'].append(bids['water'])
 d['supported_perch_points_weights']=[{'perch_point':1069283163,'weight':.3},{'perch_point':1334782406,'weight':.6},{'perch_point':495710309,'weight':.05},{'perch_point':4191031092,'weight':.05}]
 if r['name']=='Ducklett':
  d['supported_perch_points_weights']=[{'perch_point':1069283163,'weight':.15},{'perch_point':1334782406,'weight':.85}]
  d['should_sink_when_flying']=False
 if r['name']=='Cramorant':
  d['supported_perch_points_weights']=[{'perch_point':1334782406,'weight':.65},{'perch_point':1069283163,'weight':.3},{'perch_point':4191031092,'weight':.05}]
 if r['name']=='Psyduck':
  d['rarity']=psyduck_rarity_id
  # Native BigWater swimming only: no seeds, player, tree, rock or land hangouts.
  d['supported_perch_points_weights']=[{'perch_point':1424542570,'weight':1.0}]
  d['spawn_type']=3806188274 # DistantWater; every authored spawn lies in a pond.
  d['movement_type']=1 # AlwaysFlightless
  d['preferred_seeds']=[]
  d['stat_ground_move_speed']=1.0
  d['stat_fly_speed']=1.0 # Native flightless transitions also use this speed.
  d['bird_animation_override']=[{'from':5,'to':8}] # Swim -> PenguinSwim
  d['should_sink_when_flying']=False # Floating body already has tucked feet.
 if r['zone']=='cliffs':d['supported_perch_points_weights']=[{'perch_point':1069283163,'weight':.45},{'perch_point':1334782406,'weight':.5},{'perch_point':4191031092,'weight':.05}]
 # Ground foragers spend more time in clearings; canopy specialists retain their mix.
 if r['name'] in ['Pidgey','Spearow',"Farfetch'd",'Doduo','Dodrio','Starly','Staravia','Fletchling','Hawlucha']:
  d['supported_perch_points_weights']=[{'perch_point':1069283163,'weight':.55},{'perch_point':1334782406,'weight':.4},{'perch_point':495710309,'weight':.04},{'perch_point':4191031092,'weight':.01}]
 if r['name'] in ['Gligar','Talonflame','Aerodactyl','Hawlucha']:
  rock_weight={'Gligar':.6,'Talonflame':.65,'Aerodactyl':.75,'Hawlucha':.4}[r['name']]
  d['supported_perch_points_weights']=[{'perch_point':1069283163,'weight':round(.95-rock_weight,2)},{'perch_point':1334782406,'weight':rock_weight},{'perch_point':4191031092,'weight':.05}]
 if r['name'] in ['Zapdos','Ho-Oh']:
  d['supported_perch_points_weights']=[{'perch_point':3526737011,'weight':1.0}]
  d['rarity']=legend_rarity_id # One pool entry each, versus three for ordinary epics.
  d['preferred_seeds']=[] # No seed lure can pull these high-only visitors onto the ground.
 d['stat_tweet_wait_time']={'base':9,'variance':4};d['stat_preferred_group_size']=1 if r['rarity']=='epic' else 3
 if r['zone']=='grass':d['stat_tweet_wait_time']={'base':16.875,'variance':7.5}
 d['stat_linger_time']={'base':45,'variance':10};d['stat_migration_time']={'base':70,'variance':20};d['view_distance']=20
 if r['name'] in ['Pidgey','Spearow',"Farfetch'd",'Doduo','Dodrio','Starly','Staravia','Fletchling','Hawlucha']:
  d['stat_linger_time']={'base':55,'variance':10}
 d['dimensions']['perched_front_back']={'foot_offset':0,'head_offset':.48,'center_offset':-.2,'size_offset':0}
 for pose in ['perched_side','flying_side','sideways']:
  d['dimensions'][pose]={'foot_offset':{'X':-1.2,'Y':.3},'head_offset':{'X':-.4,'Y':.5},'center_offset':{'X':-.2,'Y':-.3},'size_offset':0}
 if r['name']=='Pidgey':
  d['dimensions']['perched_front_back']['foot_offset']=0
  for pose in ['perched_side','flying_side','sideways']:
   d['dimensions'][pose]['foot_offset']={'X':0,'Y':0}
 d['flap_animation_speed']=5 if float(r['scale'])>1.3 else 10
 if r['name']=='Psyduck':
  d['view_distance']=6
  d['stat_linger_time']={'base':60,'variance':10}
  # Keep the common swimming population resident instead of walking across dry paths.
  d['stat_migration_time']={'base':86400,'variance':0}
  d['flap_animation_speed']=2
 d['whistle_colors']=[dict(zip(['red','green','blue'],[int(c[i:i+2],16)/255 for i in (1,3,5)])) for c in [r['body'],r['accent'],r['belly']]]
 save('BirdSpecies',r['name'],d)
d=vanilla('Level_GooseLake');d.update(name=loc('map.name','Safari Zone'),show_in_level_select=True,sort_order=30,scene={'path':'mods://Touma/SafariZone/SafariZone.tscn'},main_menu_scene={'path':''},biomes=list(bids.values()),bird_population_cap=60,progression=save('ProgressionConfig','SafariZone',{'star_requirements_per_biome':[{'biome':bids['forest'],'required_stars':10}]}),required_dlc=0)
for k in ['at_least_one_bird_achievement','all_poses_achievement','all_3_star_achievement','all_shinies_achievement','one_photo_per_biome_achievement','all_points_of_interest']:d[k]=0
d['map']={'path':'mods://Touma/SafariZone/map.png'};save('Level','SafariZone',d)
save('LocalizationIdTableExtension','SafariZone',{'ids_to_slug':[{'id':uid('loc.'+k),'string':'touma.safarizone.'+k} for k in strings]})
save('LocaleExtension','SafariZoneEnglish',{'source_language':632594830,'ids_to_translations':[{'id':uid('loc.'+k),'translation':v} for k,v in strings.items()]})
# A scene containing only inline geometry and existing game resources needs no assets pack.
ext={};subs=[];nodes=[];counter=0
def resource(path,typ):
 if path not in ext:ext[path]=(str(len(ext)+1),typ)
 return 'ExtResource("'+ext[path][0]+'")'
def sub(typ,props):
 global counter
 counter+=1;id='S'+str(counter);subs.append(f'[sub_resource type="{typ}" id="{id}"]\n'+props);return f'SubResource("{id}")'
def node(name,typ,parent='.',props='',instance=None,index=None):
 h=f'[node name="{name}"'+(f' type="{typ}"' if typ else '')+(f' parent="{parent}"' if parent is not None else '')+(f' instance={instance}' if instance else '')+(f' index="{index}"' if index is not None else '')+']';nodes.append(h+'\n'+props)
def vec(p):return 'Vector3('+', '.join(str(v) for v in p)+')'
def mat(color):
 rgb=[int(color[i:i+2],16)/255 for i in (1,3,5)];return sub('StandardMaterial3D','albedo_color = Color('+', '.join(map(str,rgb))+', 1)\nroughness = 0.9')
mats={k:mat(c) for k,c in [('path','#d7c49b'),('wood','#6f543b'),('leaf','#5c8e51'),('rock','#a8a492'),('water','#499ead')]+[(z[0],z[4]) for z in zones]}
def box(name,pos,size,m,solid=True,parent='.'):
 node(name,'Node3D',parent,'position = '+vec(pos));par=name if parent=='.' else parent+'/'+name
 mesh=sub('BoxMesh','size = '+vec(size));node('Mesh','MeshInstance3D',par,f'mesh = {mesh}\nmaterial_override = {mats[m]}')
 if solid:
  node('Body','StaticBody3D',par,'collision_layer = 11\ncollision_mask = 0');s=sub('BoxShape3D','size = '+vec(size));node('Shape','CollisionShape3D',par+'/Body','shape = '+s)
def prefab(name,path,pos,scale=None,props=''):
 resource_path='res://Scenes/'+path+'.tscn';ref=resource(resource_path,'PackedScene')
 node(name,None,'.', 'position = '+vec(pos)+(('\nscale = '+vec(scale)) if scale else '')+('\n'+props if props else ''),ref)
def scriptnode(name,typ,path,pos,props='',parent='.'):
 node(name,typ,parent,'position = '+vec(pos)+'\nscript = '+resource('res://Scripts/'+path+'.cs','Script')+'\n'+props)
node('SafariZone','Node3D',None)
from map_scene import build as build_map_scene
build_map_scene(globals())
text='[gd_scene format=3]\n\n'+'\n'.join(f'[ext_resource type="{typ}" path="{path}" id="{id}"]' for path,(id,typ) in ext.items())+'\n\n'+'\n\n'.join(subs+nodes)+'\n'
(ROOT/'editor/SceneEditor/Levels/SafariZone.tscn').write_text(text)
(OUT/'SafariZone.tscn').write_text(text)
print(f'Built {len(roster)} birds, {len(zones)} biomes, {len(nodes)} scene nodes in {OUT}')
