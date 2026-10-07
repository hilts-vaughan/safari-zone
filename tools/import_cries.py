"""Fetch pinned PokéAPI cries and convert saved originals to moderate-volume mono WAVs."""
import argparse,csv,json,hashlib,urllib.request,subprocess,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def fetch(url):
 request=urllib.request.Request(url,headers={'User-Agent':'SafariZone-local-mod/1.0'})
 with urllib.request.urlopen(request,timeout=45) as response:return response.read()
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--refresh',action='store_true',help='Fetch current upstream originals; default rebuilds verified saved originals offline')
 args=parser.parse_args()
 manifest=ROOT/'assets/audio/cries/sources.json'
 saved=json.loads(manifest.read_text()) if manifest.exists() else None
 if not args.refresh and saved is None:raise ValueError('No saved originals; use --refresh for first import')
 commit=json.loads(fetch('https://api.github.com/repos/PokeAPI/cries/commits/main'))['sha'] if args.refresh else saved['commit']
 prior={e['name']:e for e in saved['species']} if saved else {}
 rows=list(csv.DictReader((ROOT/'data/roster.csv').open()));sources=ROOT/'assets/audio/cries';sources.mkdir(parents=True,exist_ok=True)
 def process(row):
  name=row['name'];url=f"https://raw.githubusercontent.com/PokeAPI/cries/{commit}/cries/pokemon/latest/{row['dex']}.ogg"
  original=sources/(row['dex']+'.ogg')
  new_species=name not in prior
  data=fetch(url) if args.refresh or new_species else original.read_bytes()
  if not args.refresh and not new_species and hashlib.sha256(data).hexdigest()!=prior[name]['original_sha256']:raise ValueError('Original cry hash mismatch: '+name)
  if not data.startswith(b'OggS'):raise ValueError('Not OGG: '+name)
  original=sources/(row['dex']+'.ogg');original.write_bytes(data)
  # Preserve original pitch and duration; normalize each cry peak to -6 dBFS.
  probe=subprocess.run(['ffmpeg','-hide_banner','-i',str(original),'-af','volumedetect','-f','null','-'],capture_output=True,text=True,check=True)
  import re
  peak=float(re.search(r'max_volume: (-?[\d.]+) dB',probe.stderr)[1]);gain=-6-peak
  dest=ROOT/'assets/birds'/name/'call.wav'
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(original),'-af',f'volume={gain:.3f}dB','-ac','1','-ar','44100','-c:a','pcm_s16le',str(dest)],check=True)
  return {'name':name,'dex':int(row['dex']),'source_url':url,'original_sha256':hashlib.sha256(data).hexdigest(),'wav_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'gain_db':round(gain,3),'target_peak_dbfs':-6}
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:entries=list(pool.map(process,rows))
 record={'source':'https://github.com/PokeAPI/cries','commit':commit,'method':'Latest cries; original OGG retained. Mono 44.1kHz PCM WAV, peak normalized to -6 dBFS. Original pitch and duration retained.','species':entries}
 (sources/'sources.json').write_text(json.dumps(record,indent=2)+'\n')
 provenance_path=ROOT/'assets/birds/provenance.json';provenance=json.loads(provenance_path.read_text())
 for e in entries:provenance['species'][e['name']]['call_source']=e['source_url']
 provenance_path.write_text(json.dumps(provenance,indent=2)+'\n');print(f'Imported {len(entries)} species cries at pinned commit {commit}.')
if __name__=='__main__':main()
