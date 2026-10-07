"""Physical sightline screens with explicit clearance around the connected trails."""
import math,json
from pathlib import Path
from woodland_section import contains as in_study
from gatehouse_scene import contains as in_gatehouse
from grasslands_layout import contains as in_grasslands
from frontage_scene import contains as in_frontage
from map_layout import path_distance
from functools import lru_cache
@lru_cache(maxsize=1)
def build_layout():
 baseline=json.loads((Path(__file__).resolve().parents[1]/'data/enclosure-baseline.json').read_text())
 return {kind:[h for h in group if not in_frontage(h['p'],h['radius']+2) and not in_grasslands(h['p'],h['radius']+2) and not in_gatehouse(h['p'],h['radius']+2) and not in_study(h['p'],h['radius']) and path_distance(h['p'])-h['radius']>3.3] for kind,group in baseline.items()}

def blocked(p,margin=0):
 model=build_layout()
 return any(math.dist(p,h['p'])<h['radius']*(1.85 if key=='ridges' else 1)+margin for key,kind in model.items() for h in kind)
