"""Bounded, isolated native-game regression with machine-readable evidence."""
import argparse
import csv
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from payload import ROOT, NAMESPACE, verify

ANSI = re.compile(r'\x1b\[[0-9;]*m')


def clean(text):
    return ANSI.sub('', text)


def error_report(text):
    """Accept only the observed null-reference signature, never all startup errors."""
    lines = clean(text).splitlines()
    known, unexpected = [], []
    for index, line in enumerate(lines):
        if re.search(r'ERROR[: ]|^System\.\w+Exception:', line):
            context_lines = [line]
            for following in lines[index + 1:index + 5]:
                if 'ERROR' in following:
                    break
                context_lines.append(following)
            context = '\n'.join(context_lines)
            if 'System.NullReferenceException:' in context and 'GameCore.FinishLoadScene(' in context:
                known.append(context)
            else:
                unexpected.append(context)
    return {'localhost_startup_errors': known, 'unexpected_errors': unexpected}


def finalize(report, text):
    report.update(error_report(text))
    if report['unexpected_errors']:
        report['status'] = 'failed'
        report.setdefault('failure', 'Unexpected runtime or shutdown errors; see log')
    elif report['localhost_startup_errors'] and not report['allow_localhost_startup_error']:
        report['status'] = 'failed'
        report.setdefault('failure', 'Known localhost startup error was not explicitly allowed')
    return report


def wait_for(process, log, pattern, timeout, offset=0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        text = clean(log.read_text(errors='replace'))
        match = re.search(pattern, text[offset:])
        if match:
            return match
        if process.poll() is not None:
            raise RuntimeError(f'Game exited ({process.returncode}) before: {pattern}')
        time.sleep(.2)
    raise TimeoutError(f'No log evidence within {timeout}s: {pattern}')


def command(text, action='submit'):
    subprocess.run([sys.executable, str(ROOT / 'tools/ui_driver.py'), action, text], check=True, timeout=15)


def run(args):
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    log = output / 'game.log'
    report = {'status': 'failed', 'mode': args.roster, 'spawns': {}, 'checks': {},
              'allow_localhost_startup_error': args.allow_localhost_startup_error,
              'limitations': ['No fixed game RNG seed is available.', 'Multiplayer is not covered.' if args.normal_ui and args.center_review else 'Photo scoring and multiplayer are not covered.' if args.normal_ui else 'Normal UI launch, photo scoring, and multiplayer are not covered.']}
    process = None
    try:
        report['payload_hashes'] = verify(ROOT / 'dist' / NAMESPACE, ROOT / 'docs/build-manifest.json')
        subprocess.run([sys.executable, str(ROOT / 'tools/validate_mod.py'), str(args.game_dir / 'FlockAround.pck')], check=True, timeout=60)
        # Check the local host port before launch; never kill unrelated hosts.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.bind(('0.0.0.0', 1027))
        with tempfile.TemporaryDirectory(prefix='flock-regression-') as temporary:
            work = Path(temporary)
            save = work / 'data/SecretPlan/FlockAround'
            save.mkdir(parents=True)
            shutil.copytree(ROOT / 'dist' / NAMESPACE, save / 'Mods' / NAMESPACE)
            settings = json.loads((ROOT / 'tests/fixtures/runtime-settings.json').read_text())
            level = json.loads((ROOT / 'dist' / NAMESPACE / 'Level_SafariZone.json').read_text())
            settings['preferred_lobby_settings']['level'] = level['config_info']['config_instance_id']
            if args.normal_ui:
                settings['preferred_lobby_settings']['lobby_mode'] = 2
            if args.gate_picnic_walk or args.bridge_walk or args.watergarden_walk or args.center_review or args.woodland_walk or args.gate_review or args.forest_gate_review or args.grasslands_review:
                for action,code in [('interact',69),('move_forward',87),('move_left',65),('move_right',68),('secondary_action',70),('primary_action',82)]:
                    settings['action_to_keybinds_v2'][action]=[{'type':1,'keycode':code,'mouse_button':0,'joy_button':0,'joy_axis':0,'axis_value':0.0}]
            (save / 'settings.json').write_text(json.dumps(settings))
            fixture={'format_version':6,'has_seen_telemetry_consent':True}
            if args.gate_stars:
                remaining=args.gate_stars;table={}
                for file in sorted((ROOT/'dist'/NAMESPACE).glob('BirdSpecies_*.json')):
                    species=json.loads(file.read_text())['config_info']['config_instance_id']
                    count=min(3,remaining)
                    if not count:break
                    table[f"{species}:1:{level['config_info']['config_instance_id']}"]={'photo':'GATE_REGRESSION_FIXTURE','star_count':count}
                    remaining-=count
                if remaining:raise ValueError('Requested gate fixture exceeds one pose per species')
                fixture['guidebook']={'table':table}
                # Real, minimal photo payload prevents missing-file errors while seed scores test the threshold.
                import base64,io
                from PIL import Image
                buffer=io.BytesIO();Image.new('RGB',(32,32),'#729baa').save(buffer,format='PNG')
                photos=save/'Photos';photos.mkdir()
                (photos/'GATE_REGRESSION_FIXTURE.json').write_text(json.dumps({'image':{'format':'Png','image_bytes':base64.b64encode(buffer.getvalue()).decode()},'photo_metadata':{},'birds':[],'points_of_interest':[],'players':[]}))
            (save / 'save.json').write_text(json.dumps(fixture))
            if args.water_review:
                # Add a read-only position probe to this disposable scene only.
                from map_layout import PONDS
                (save/'water-pockets.json').write_text(json.dumps(PONDS))
                shutil.copyfile(ROOT/'tools/water_review.gd',save/'water-review.gd')
                scene=save/'Mods'/NAMESPACE/'SafariZone.tscn'
                content=scene.read_text()
                offset=content.index('[ext_resource ')
                content=content[:offset]+'[ext_resource type="Script" path="user://water-review.gd" id="WaterReview"]\n\n'+content[offset:]
                content+='\n[node name="WaterRegressionProbe" type="Node" parent="."]\nscript = ExtResource("WaterReview")\n'
                scene.write_text(content)
            env = dict(os.environ, XDG_DATA_HOME=str(work / 'data'), XDG_CONFIG_HOME=str(work / 'config'), SteamAppId='3618030')
            with log.open('w') as stream:
                process = subprocess.Popen(['stdbuf', '-oL', '-eL', str(args.game_dir / 'FlockAround'), '--rendering-method', args.rendering_method,
                    '--windowed', '--resolution', '1280x720', '--audio-driver', 'Dummy', '--', '--enablemods', *([] if args.normal_ui else ['--localhost'])],
                    cwd=args.game_dir, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
                try:
                    if args.normal_ui:
                        wait_for(process,log,r'Done Instantiate for res://Scenes/UI/MainMenu.tscn',args.timeout)
                        time.sleep(3)
                        subprocess.run(['import','-window','root',str(output/'normal-main-menu.png')],check=True)
                        subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'key','Return'],check=True)
                        time.sleep(2)
                        subprocess.run(['import','-window','root',str(output/'normal-create-menu.png')],check=True)
                        subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'key','Return'],check=True)
                    wait_for(process, log, r'LOAD: Loading Scrim flag gameplay_loading unset', args.timeout)
                    report['checks']['gameplay_ready'] = True
                    if args.normal_ui: report['checks']['normal_offline_menu_launch'] = True
                    command('loadingscrim fullclear', 'command-open')
                    wait_for(process, log, r'>>> loadingscrim fullclear', args.timeout)
                    def key(name):
                        subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'key',name],check=True)
                        time.sleep(.4)
                    def capture(name):
                        subprocess.run(['import','-window','root',str(output/(name+'.png'))],check=True,timeout=15)
                    if args.center_review:
                        def settled_position():
                            offset=len(log.read_text(errors='replace'));command('position');time.sleep(.5)
                            found=re.findall(r'#\s+(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)\s*$',clean(log.read_text(errors='replace')[offset:]),re.M)
                            if not found:raise RuntimeError('No Center position evidence')
                            return list(map(float,found[-1]))
                        time.sleep(2)
                        pos=settled_position();report['center_spawn_position']=pos
                        if abs(pos[0]+70)>1 or abs(pos[2]-69)>1 or not 0<=pos[1]<=.2:raise RuntimeError('Player did not spawn inside Center')
                        report['checks']['center_spawn_inside']=True
                        key('grave');capture('center-interior')
                        subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'hold','w','3'],check=True)
                        key('grave');pos=settled_position();report['center_walkout_position']=pos
                        if pos[2]<78 or abs(pos[0]+70)>2:raise RuntimeError('Could not walk through Center doorway')
                        report['checks']['center_door_walkthrough']=True
                        command('warp -70,1.5,72');key('grave');time.sleep(1);capture('center-back-wall');key('grave')
                        command('warp -65,1.5,71.2');key('grave');time.sleep(1);key('e');time.sleep(1);capture('center-shop-popup')
                        wait_for(process,log,r'THMB: Clearing thumbnail scene and spawning Seeds_',args.timeout)
                        report['checks']['center_shop_opened']=True
                        key('Escape');time.sleep(.3);key('grave');command('warp -75,1.5,71.2');key('grave');time.sleep(1);capture('center-photo-prompt');key('e')
                        wait_for(process,log,r'No photos to develop',args.timeout)
                        report['checks']['center_photo_interaction_empty_film']=True
                        subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'chord','f','r'],check=True)
                        wait_for(process,log,r'Taking photo ',args.timeout)
                        report['checks']['center_camera_captured_film']=True
                        time.sleep(1);capture('center-film-captured');key('e');time.sleep(4);capture('center-photo-development')
                        key('e');key('Escape');key('grave')
                    if args.map_review:
                        from map_layout import WAYPOINTS
                        report['map_screenshots'] = []
                        report['map_positions'] = {}
                        for name in args.map_review_points.split(','):
                            x,z=WAYPOINTS[name]
                            offset=len(log.read_text(errors='replace'))
                            command(f'warp {x},1.5,{z}')
                            subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'key','grave'],check=True)
                            time.sleep(2)
                            subprocess.run(['import','-window','root',str(output/f'map-{name}.png')],check=True,timeout=15)
                            report['map_screenshots'].append(f'map-{name}.png')
                            subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'key','grave'],check=True)
                            command('position')
                            deadline=time.monotonic()+5
                            while '>>> position' not in clean(log.read_text(errors='replace')[offset:]) and time.monotonic()<deadline:
                                time.sleep(.2)
                            text=clean(log.read_text(errors='replace')[offset:])
                            positions=re.findall(r'#\s+(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)\s*$',text,re.M)
                            if not positions:
                                raise RuntimeError(f'No settled position evidence for {name}; see log')
                            px,py,pz=map(float,positions[-1]);report['map_positions'][name]=[px,py,pz]
                            if abs(px-x)>3 or abs(pz-z)>3 or not -.25<=py<=2:
                                raise RuntimeError(f'Ground/warp check failed at {name}: {px,py,pz}')
                        report['checks']['map_landmark_ground_checks'] = True
                    if args.gate_picnic_walk:
                        report['gate_picnic_walks'] = {}
                        for side,keyname,x in [('left','a',33),('right','d',43)]:
                            command('warp 38,1.5,36')
                            key('grave');time.sleep(1)
                            capture('gate-picnic-doorway-'+side)
                            for movement,duration in [('w','1.7'),(keyname,'1.0'),('w','2.2')]:
                                subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'hold',movement,duration],check=True)
                            capture('gate-picnic-walk-'+side)
                            key('grave')
                            offset=len(log.read_text(errors='replace'));command('position');time.sleep(1)
                            found=re.findall(r'#\s+(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)\s*$',clean(log.read_text(errors='replace')[offset:]),re.M)
                            if not found:raise RuntimeError('No picnic walk position evidence')
                            pos=list(map(float,found[-1]));report['gate_picnic_walks'][side]=pos
                            if pos[2]>18 or abs(pos[0]-x)>1.0 or not -.25<=pos[1]<=.3:
                                raise RuntimeError(f'Picnic {side} route blocked: {pos}')
                        report['checks']['gate_picnic_both_forks_walked']=True
                    if args.bridge_walk:
                        command('warp 22.6,1.5,80')
                        key('grave');time.sleep(1)
                        capture('garden-bridge-approach')
                        subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'hold','w','3'],check=True)
                        capture('garden-bridge-walk-exit')
                        key('grave')
                        offset=len(log.read_text(errors='replace'));command('position');time.sleep(1)
                        found=re.findall(r'#\s+(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)\s*$',clean(log.read_text(errors='replace')[offset:]),re.M)
                        if not found:raise RuntimeError('No bridge walk position evidence')
                        px,py,pz=map(float,found[-1]);report['bridge_walk_exit']=[px,py,pz]
                        if pz>70.8 or abs(px-22.6)>1 or not -.25<=py<=.5:
                            raise RuntimeError(f'Garden bridge traversal failed: {px,py,pz}')
                        report['checks']['garden_bridge_walked']=True
                    if args.watergarden_walk:
                        command('warp 51,1.5,63')
                        key('grave');time.sleep(1)
                        subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'hold','d','6'],check=True)
                        capture('watergarden-walk-exit')
                        key('grave')
                        offset=len(log.read_text(errors='replace'));command('position');time.sleep(1)
                        found=re.findall(r'#\s+(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)\s*$',clean(log.read_text(errors='replace')[offset:]),re.M)
                        if not found:raise RuntimeError('No water garden walk position evidence')
                        px,py,pz=map(float,found[-1]);report['watergarden_walk_exit']=[px,py,pz]
                        if px<73 or abs(pz-63)>1.5 or not -.25<=py<=.5:
                            raise RuntimeError(f'Water garden passage traversal failed: {px,py,pz}')
                        report['checks']['watergarden_passage_walked']=True
                    if args.woodland_walk:
                        command('warp -5,1.5,-26')
                        subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'key','grave'],check=True)
                        time.sleep(1)
                        subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'hold','w','3'],check=True)
                        subprocess.run(['import','-window','root',str(output/'woodland-walk.png')],check=True,timeout=15)
                        subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'key','grave'],check=True)
                        offset=len(log.read_text(errors='replace'));command('position');time.sleep(1)
                        positions=re.findall(r'#\s+(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)\s*$',clean(log.read_text(errors='replace')[offset:]),re.M)
                        if not positions:raise RuntimeError('No woodland walk position evidence')
                        px,py,pz=map(float,positions[-1])
                        report['woodland_walk_position']=[px,py,pz]
                        if abs(px+5)>2 or pz>-38 or not -.25<=py<=2:raise RuntimeError('Woodland approach walkthrough failed')
                        report['checks']['woodland_approach_walkthrough']=True
                    if args.frontage_review:
                        report['frontage_positions']={}
                        samples=[('garden',-70,92,.0),('west-gateway',-96.3,80,.0),('east-gateway',-47.8,79,.0)]
                        samples += [(f'spiral-turn-{i+1}',-40,91.1,.75+3*i) for i in range(5)]
                        samples += [('tower-deck',-35.9,89,15)]
                        for name,x,z,height in samples:
                            command(f'warp {x},{height+1.2},{z}')
                            subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'key','grave'],check=True)
                            time.sleep(1.5)
                            subprocess.run(['import','-window','root',str(output/('frontage-'+name+'.png'))],check=True,timeout=15)
                            subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'key','grave'],check=True)
                            offset=len(log.read_text(errors='replace'));command('position');time.sleep(.6)
                            found=re.findall(r'#\s+(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)\s*$',clean(log.read_text(errors='replace')[offset:]),re.M)
                            if not found:raise RuntimeError('Missing frontage position evidence: '+name)
                            pos=list(map(float,found[-1]));report['frontage_positions'][name]=pos
                            if abs(pos[0]-x)>1 or abs(pos[2]-z)>1 or abs(pos[1]-height)>.25:
                                raise RuntimeError('Frontage native grounding failed: '+name+' '+str(pos))
                        report['checks']['frontage_gateways_and_five_spiral_turns_grounded']=True
                        report['checks']['frontage_15m_deck_grounded']=True
                    if args.grasslands_review:
                        def grass_key(name):
                            subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'key',name],check=True)
                        def grass_capture(name):
                            subprocess.run(['import','-window','root',str(output/(name+'.png'))],check=True,timeout=15)
                        def grass_position():
                            offset=len(log.read_text(errors='replace'));command('position');time.sleep(1)
                            found=re.findall(r'#\s+(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)\s*$',clean(log.read_text(errors='replace')[offset:]),re.M)
                            if not found:raise RuntimeError('No grasslands walkthrough position evidence')
                            return list(map(float,found[-1]))
                        command('warp -91,1.5,57');grass_key('grave');time.sleep(2);grass_capture('grasslands-fork');grass_key('grave')
                        command('warp -129,1.5,62');grass_key('grave');time.sleep(2);grass_capture('grasslands-stairs')
                        subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'hold','w','5.1'],check=True)
                        time.sleep(1);grass_capture('grasslands-stairs-climbed');grass_key('grave')
                        p=grass_position();report['grasslands_stair_position']=p
                        if abs(p[0]+129)>1.5 or p[2]>41 or not 3.3<=p[1]<=3.8:
                            raise RuntimeError('Grasslands stairs did not reach elevated walkway: '+str(p))
                        report['checks']['grasslands_stairs_climbed']=True
                        command('warp -129,5,30');grass_key('grave');time.sleep(2);grass_capture('grasslands-deck');grass_key('grave')
                        p=grass_position();report['grasslands_deck_position']=p
                        if not 3.3<=p[1]<=3.8:raise RuntimeError('Observation deck grounding failed: '+str(p))
                        report['checks']['grasslands_deck_grounded']=True
                        command('warp -74,1.5,52');grass_key('grave');time.sleep(2);grass_capture('grasslands-tall-grass');grass_key('grave')
                    if args.forest_gate_review:
                        def forest_key(name):
                            subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'key',name],check=True);time.sleep(.4)
                        command('list players')
                        wait_for(process,log,str(args.gate_stars)+r' stars',args.timeout)
                        command('warp -111,1.5,-1.6');forest_key('grave');time.sleep(1)
                        subprocess.run(['import','-window','root',str(output/'forest-gate-before.png')],check=True)
                        forest_key('e');time.sleep(2)
                        subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'hold','w','1.5'],check=True)
                        subprocess.run(['import','-window','root',str(output/'forest-gate-after.png')],check=True)
                        forest_key('grave');offset=len(log.read_text(errors='replace'));command('position');time.sleep(1)
                        found=re.findall(r'#\s+(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)\s*$',clean(log.read_text(errors='replace')[offset:]),re.M)
                        if not found:raise RuntimeError('No forest gate position evidence')
                        pos=list(map(float,found[-1]));report['forest_gate_position']=pos
                        if args.gate_stars<10:
                            if pos[2]<-2.3:raise RuntimeError('Forest gate allowed passage below 10 stars')
                            report['checks']['forest_gate_blocks_below_10']=True
                        else:
                            if pos[2]>-4:raise RuntimeError('Forest gate failed to open at 10 stars')
                            report['checks']['forest_gate_opens_at_10']=True
                    if args.gate_review:
                        def gate_key(name):
                            subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'key',name],check=True);time.sleep(.4)
                        def gate_capture(name):
                            subprocess.run(['import','-window','root',str(output/(name+'.png'))],check=True,timeout=15)
                        def gate_position():
                            offset=len(log.read_text(errors='replace'));command('position');time.sleep(1)
                            found=re.findall(r'#\s+(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)\s*$',clean(log.read_text(errors='replace')[offset:]),re.M)
                            if not found:raise RuntimeError('No gate walkthrough position evidence')
                            return list(map(float,found[-1]))
                        command('list players')
                        wait_for(process,log,str(args.gate_stars)+r' stars',args.timeout)
                        report['gate_fixture_stars']=args.gate_stars
                        command('warp 38,1.5,35');gate_key('grave');time.sleep(1);gate_capture('gate-star-prompt');gate_key('e');time.sleep(2)
                        gate_capture('gate-after-interact')
                        subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'hold','w','1.5'],check=True)
                        gate_key('grave');pos=gate_position();report['gate_walk_position']=pos
                        if pos[2]>32:raise RuntimeError('Wetlands Rest exit blocked free passage')
                        report['checks']['wetlands_rest_free_passage']=True
                        command('warp 44,1.5,45');gate_key('grave');time.sleep(1);gate_key('e');time.sleep(1);gate_capture('gate-shop-popup')
                        wait_for(process,log,r'THMB: Clearing thumbnail scene and spawning Seeds_',args.timeout)
                        report['checks']['gate_shop_opened']=True
                        gate_key('Escape');gate_key('grave');command('warp 32,1.5,45');gate_key('grave');time.sleep(1);gate_key('e')
                        wait_for(process,log,r'No photos to develop',args.timeout)
                        report['checks']['gate_photo_empty_film']=True
                        subprocess.run([sys.executable,str(ROOT/'tools/ui_driver.py'),'chord','f','r'],check=True)
                        wait_for(process,log,r'Taking photo ',args.timeout)
                        deadline=time.monotonic()+6
                        captured=None
                        while time.monotonic()<deadline:
                            captured=json.loads((save/'save.json').read_text()).get('film',{}).get('content')
                            if captured:break
                            time.sleep(.3)
                        if not captured:raise RuntimeError('Captured film was not persisted before development')
                        report['gate_photo_film_before']=captured
                        gate_key('e');time.sleep(4);gate_capture('gate-photo-development')
                        deadline=time.monotonic()+5
                        while time.monotonic()<deadline:
                            saved=json.loads((save/'save.json').read_text())
                            if saved.get('film') and saved['film'].get('content')==[]:break
                            time.sleep(.3)
                        report['gate_photo_film_after']=saved.get('film')
                        report['gate_photo_wallet_after']=saved.get('wallet')
                        if saved.get('film',{}).get('content')!=[]:raise RuntimeError('Gate photo counter did not clear captured film')
                        report['checks']['gate_photo_development_invoked']=True
                        gate_key('e');gate_key('Escape');gate_key('grave')
                    names = [row['name'] for row in csv.DictReader((ROOT / 'data/roster.csv').open())] if args.roster == 'all' else ['Ho-Oh', 'Pidgey', 'Braviary']
                    for name in args.inspect:
                        if name not in names and not (args.water_review and name=='Psyduck'):names.append(name)
                    for name in names:
                        command('spawn ' + name.lower().replace('-', ''))
                        match = wait_for(process, log, r'Spawning ' + re.escape(name) + r' with ID (\d+)', args.timeout)
                        report['spawns'][name] = int(match.group(1))
                    report['inspection_screenshots'] = []
                    for name in args.inspect:
                        if name not in report['spawns'] and not (args.water_review and name=='Psyduck'):
                            raise ValueError(f'Inspection species was not spawned by this mode: {name}')
                        # Earlier birds may migrate away during a full-roster run.
                        # Inspect a freshly spawned instance instead of a stale ID.
                        if args.water_review and name=='Psyduck':
                            # Inspect a natural resident without inflating the population.
                            match=wait_for(process,log,r'"bird":"Psyduck_(\d+)"',args.timeout)
                            bird_id=int(match.group(1));report['spawns'][name]=bird_id
                        else:
                            spawn_offset=len(clean(log.read_text(errors='replace')))
                            command('spawn ' + name.lower().replace('-', ''))
                            match=wait_for(process,log,r'Spawning '+re.escape(name)+r' with ID (\d+)',args.timeout,offset=spawn_offset)
                            bird_id=int(match.group(1));report['spawns'][name]=bird_id
                        command('spectate '+str(bird_id))
                        wait_for(process,log,rf'>>> spectate {bird_id}\b',args.timeout)
                        # Capture after the camera transition; this is review evidence,
                        # not a claim of deterministic pixels or a visual assertion.
                        deadline=time.monotonic()+1.5
                        while time.monotonic()<deadline:
                            if process.poll() is not None:
                                raise RuntimeError('Game exited during visual inspection')
                            time.sleep(.1)
                        filename='inspect-'+re.sub(r'[^A-Za-z0-9_-]','',name)+'.png'
                        subprocess.run(['import','-window','root',str(output/filename)],check=True,timeout=15)
                        report['inspection_screenshots'].append(filename)
                    # A deliberate observation window for movement/perch failures.
                    deadline = time.monotonic() + args.observe
                    while time.monotonic() < deadline:
                        if process.poll() is not None:
                            raise RuntimeError('Game exited during movement observation')
                        time.sleep(.2)
                    command('list birds')
                    wait_for(process, log, r'>>> list birds', args.timeout)
                    subprocess.run(['import', '-window', 'root', str(output / 'gameplay.png')], check=True, timeout=15)
                    text = clean(log.read_text(errors='replace'))
                    if args.water_review:
                        samples=[json.loads(m) for m in re.findall(r'WATER_REVIEW (\{[^\n]+\})',text)]
                        report['water_samples']=samples
                        populations=[json.loads(m) for m in re.findall(r'WATER_POPULATION (\{[^\n]+\})',text)]
                        report['water_populations']=populations
                        report['checks']['natural_psyduck_population_one_or_two']=bool(populations) and max(p['count'] for p in populations)<=2 and any(p['count']>=1 for p in populations)
                        report['checks']['water_bodies_above_surface']=bool(samples) and all(s.get('body_bottom_y') is not None and s['body_bottom_y']>=.125 for s in samples)
                        report['checks']['water_positions_sampled']=len(samples)>=20
                        report['checks']['water_birds_remained_in_ponds']=bool(samples) and all(s['inside'] for s in samples)
                        positions={}
                        for sample in samples:positions.setdefault(sample['bird'],[]).append(sample['position'])
                        report['checks']['water_birds_moved']=any(any(sum((a-b)**2 for a,b in zip(points[0],p))>.25 for p in points[1:]) for points in positions.values())
                    report['checks']['unclaimed_hangouts_zero'] = '0 hangouts are unclaimed' in text
                    biome_ids = [json.loads(path.read_text())['config_info']['config_instance_id'] for path in (ROOT / 'dist' / NAMESPACE).glob('Biome_*.json')]
                    report['checks']['all_biomes_have_hangouts'] = len(biome_ids) == 4 and all(re.search(rf'\b{value} has [1-9]\d* locations', text) for value in biome_ids)
                    report['checks']['all_configs_loaded'] = all('Touma/SafariZone/' + path.name in text for path in (ROOT / 'dist' / NAMESPACE).glob('*.json'))
                    report.update(error_report(text))
                    if report['unexpected_errors']:
                        raise RuntimeError('Unexpected runtime errors; see report and log')
                    if report['localhost_startup_errors'] and not args.allow_localhost_startup_error:
                        raise RuntimeError('Known localhost startup error; strict run failed (explicit allowance available)')
                    if not all(report['checks'].values()):
                        raise RuntimeError('One or more runtime assertions failed')
                    report['status'] = 'passed_with_known_startup_error' if report['localhost_startup_errors'] else 'passed'
                finally:
                    if process.poll() is None:
                        os.killpg(process.pid, signal.SIGTERM)
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid, signal.SIGKILL)
                            process.wait(timeout=5)
    except Exception as error:
        report['failure'] = str(error)
    finally:
        if log.exists():
            finalize(report, log.read_text(errors='replace'))
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f"{report['status']}: {output / 'report.json'}", flush=True)
    return 0 if report['status'].startswith('passed') else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-dir', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path, help='New directory for logs, screenshot, and report')
    parser.add_argument('--roster', choices=['smoke', 'all'], default='smoke')
    parser.add_argument('--inspect',default='',help='Comma-separated spawned species for spectate screenshots (visual review evidence only)')
    parser.add_argument('--normal-ui',action='store_true',help='Start through the normal menus in offline singleplayer instead of the localhost shortcut')
    parser.add_argument('--gate-picnic-walk',action='store_true',help='Walk from the rear gate doorway through both picnic forks')
    parser.add_argument('--forest-gate-review',action='store_true',help='Exercise the ten-star forest entrance')
    parser.add_argument('--gate-review',action='store_true',help='Exercise free passage through Wetlands Rest and its service counters')
    parser.add_argument('--gate-stars',type=int,default=0,help='Stars in the disposable gate-review guidebook fixture')
    parser.add_argument('--woodland-walk',action='store_true',help='Walk the northern fork approach and verify player progress')
    parser.add_argument('--grasslands-review',action='store_true',help='Capture the planted grasslands and verify native stair/ramp ascent and deck grounding')
    parser.add_argument('--bridge-walk',action='store_true',help='Walk across the ornamental pond bridge without jumping')
    parser.add_argument('--water-review',action='store_true',help='Inject a read-only position probe into a disposable scene and verify floating ducks stay in ponds')
    parser.add_argument('--frontage-review',action='store_true',help='Check both gateways, five spiral turns, and 15m tower deck in the native game')
    parser.add_argument('--center-review',action='store_true',help='Check interior spawn, walk through open doors, and exercise service counters')
    parser.add_argument('--watergarden-walk',action='store_true',help='Walk through both ends of the dry waterfall passage')
    parser.add_argument('--map-review',action='store_true',help='Warp to nine reserve landmarks, check settled height, and capture scenery without console overlay')
    parser.add_argument('--map-review-points',default='entry,meadow,forest,pond,hub,highland,ridge,wetland,marsh',help='Comma-separated map landmarks to review')
    parser.add_argument('--rendering-method',choices=['gl_compatibility','mobile','forward_plus'],default='gl_compatibility')
    parser.add_argument('--timeout', type=float, default=45, help='Deadline per readiness/spawn assertion')
    parser.add_argument('--observe', type=float, default=15, help='Movement observation seconds')
    parser.add_argument('--allow-localhost-startup-error', action='store_true')
    parser.add_argument('--inside-xvfb', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    args.game_dir = args.game_dir.resolve()
    args.inspect=[name.strip() for name in args.inspect.split(',') if name.strip()]
    if args.timeout <= 0 or args.observe < 0:
        parser.error('timeout must be positive and observe must be nonnegative')
    if args.inside_xvfb:
        if os.environ.get('DISPLAY', '') in ['', ':0', ':1']:
            parser.error('A disposable X11 display is required')
        return run(args)
    for name in ['xvfb-run', 'import', 'stdbuf']:
        if not shutil.which(name):
            parser.error(f'Missing executable: {name}')
    return subprocess.run(['xvfb-run', '-a', '-s', '-screen 0 1280x720x24', sys.executable,
                           str(Path(__file__).resolve()), *sys.argv[1:], '--inside-xvfb']).returncode


if __name__ == '__main__':
    sys.exit(main())
