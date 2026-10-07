import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from scene_assets import check_resource
class SceneAssetsTests(unittest.TestCase):
 def test_exported_texture_requires_compiled_import(self):
  key='EXTERNAL/Touma/SafariZone/image.png'
  files={key:b'png',key+'.import':b'[remap]\npath="res://.godot/imported/image.ctex"\n'}
  with self.assertRaises(AssertionError):check_resource('res://'+key,{},files)
  files['.godot/imported/image.ctex']=b'compiled'
  check_resource('res://'+key,{},files)
 def test_native_paths_must_exist(self):
  check_resource('res://native.tscn',{'native.tscn.remap':b''},{})
  with self.assertRaises(AssertionError):check_resource('res://missing.tscn',{}, {})
