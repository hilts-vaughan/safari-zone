"""Validate scene resources against native and officially exported mod packs."""
import re

def check_resource(path,native,custom):
 key=path.removeprefix('res://')
 if not key.startswith('EXTERNAL/'):
  assert any(key+s in native for s in ['', '.remap', '.import']),path
  return
 assert key.startswith('EXTERNAL/Touma/SafariZone/'),path
 assert key in custom,path
 if key+'.import' in custom:
  imports=custom[key+'.import'].decode()
  targets=re.findall(r'^path(?:\.\w+)?="res://([^"]+)"',imports,re.M)
  assert targets,('Missing imported resource target',path)
  for target in targets:assert target in custom,('Missing compiled asset',target)
