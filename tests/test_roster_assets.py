"""Release invariants for perch registration and species-specific cry assets."""
import csv,json,hashlib,unittest,wave
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
class RosterAssetsTests(unittest.TestCase):
 def test_all_resting_directions_clear_native_perch_origin(self):
  for row in csv.DictReader((ROOT/'data/roster.csv').open()):
   with self.subTest(species=row['name']):
    folder=ROOT/'assets/birds'/row['name'];layout=json.loads((folder/'layout.json').read_text())
    if row['name']=='Psyduck':self.assertEqual(layout['alignment_policy'],'waterline');continue
    with Image.open(folder/'body.png') as strip:
     bottoms=[strip.crop((i*400,0,(i+1)*400,400)).getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()[3] for i in (0,3,4)]
    self.assertEqual(len(set(bottoms)),1)
    clearance=layout['body_position_y']+(200-bottoms[0])*.01
    self.assertGreaterEqual(clearance,.024)
    self.assertLessEqual(clearance,.121)
 def test_every_species_has_verified_distinct_pcm_cry(self):
  sources=json.loads((ROOT/'assets/audio/cries/sources.json').read_text());entries={e['name']:e for e in sources['species']}
  hashes=set()
  for row in csv.DictReader((ROOT/'data/roster.csv').open()):
   with self.subTest(species=row['name']):
    e=entries[row['name']];self.assertEqual(e['dex'],int(row['dex']))
    file=ROOT/'assets/birds'/row['name']/'call.wav';digest=hashlib.sha256(file.read_bytes()).hexdigest()
    self.assertEqual(digest,e['wav_sha256']);hashes.add(digest)
    with wave.open(str(file)) as wav:
     self.assertEqual((wav.getnchannels(),wav.getsampwidth(),wav.getframerate()),(1,2,44100));self.assertGreater(wav.getnframes(),1000)
  self.assertEqual(len(hashes),len(entries))
if __name__=='__main__':unittest.main()
