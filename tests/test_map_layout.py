"""Spatial requirements for the expanded reserve."""
import unittest,sys,math,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from map_layout import *
class MapLayoutTests(unittest.TestCase):
 def test_double_area_and_all_landmarks_on_ground(self):
  self.assertGreaterEqual(area(outline())/(168*168),2)
  for p in WAYPOINTS.values():self.assertTrue(inside(p));self.assertFalse(pond_contains(p))
 def test_branching_connected_trail_network(self):
  adjacent={name:set() for name in WAYPOINTS}
  for trail in TRAILS:
   for a,b in zip(trail,trail[1:]):adjacent[a].add(b);adjacent[b].add(a)
  seen=set();todo=['entry']
  while todo:
   n=todo.pop()
   if n not in seen:seen.add(n);todo.extend(adjacent[n]-seen)
  self.assertEqual(seen,{name for trail in TRAILS for name in trail});self.assertGreaterEqual(sum(len(v)>=3 for v in adjacent.values()),3)
  for a,b in segments():
   for p in [a,b,((a[0]+b[0])/2,(a[1]+b[1])/2)]:self.assertTrue(inside(p));self.assertFalse(pond_contains(p,2.75))
 def test_trees_leave_trails_and_facilities_clear(self):
  model=layout();authored=(Path(__file__).resolve().parents[1]/'assets/environment/woodland/WoodlandPassage.tscn').read_text()
  authored_trees=len(re.findall(r'\[node name="(?:Skyline)?Tree\d+"',authored))
  from grasslands_layout import trees
  self.assertGreater(len(model['trees'])+authored_trees+len(trees()),150)
  for p,k,s in model['trees']:
   self.assertGreater(path_distance(p),7)
   self.assertTrue(all(math.dist(p,c)>18 for c in FACILITIES.values()))

 def test_center_does_not_block_trail_or_spawn(self):
  for a,b in segments():
   for t in [i/10 for i in range(11)]:
    x,z=a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])
    self.assertFalse(-82<x<-58 and 66<z<78, (x,z))
  x,z=WAYPOINTS['entry'];self.assertTrue(-88<x<-52 and 76<z<94)
  for p,k,s in layout()['trees']:self.assertFalse(-95<p[0]<-45 and 61<p[1]<97)

 def test_enclosures_keep_connected_trails_and_services_clear(self):
  from enclosure_layout import build_layout
  screens=build_layout()
  self.assertGreater(len(screens['ridges']),60)
  from grasslands_layout import hedges
  self.assertGreater(len(screens['hedges'])+len(hedges()),40)
  for group in screens.values():
   for screen in group:
    p,r=screen['p'],screen['radius']
    self.assertGreater(path_distance(p)-r,3.3)
    for c in FACILITIES.values():self.assertGreater(math.dist(p,c)-r,17)
    self.assertFalse(pond_contains(p,r+2))
 def test_tree_locations_not_buried_in_screens(self):
  from enclosure_layout import blocked
  for p,k,s in layout()['trees']:self.assertFalse(blocked(p,2))
