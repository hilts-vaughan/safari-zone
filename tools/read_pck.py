"""Read the installed game's Godot v3 pack without modifying it."""
import struct
from pathlib import Path
class Pack:
 def __init__(self,path):
  self.f=open(path,'rb'); f=self.f
  magic,version,major,minor,patch,flags,self.base,directory=struct.unpack('<6I2Q',f.read(40))
  assert magic==0x43504447 and version==3
  f.seek(directory); count=struct.unpack('<I',f.read(4))[0]; self.files={}
  for _ in range(count):
   n=struct.unpack('<I',f.read(4))[0]; name=f.read(n).rstrip(b'\0').decode(); offset,size=struct.unpack('<QQ',f.read(16)); f.read(20); self.files[name]=(offset,size)
 def read(self,name):
  o,s=self.files[name];self.f.seek(self.base+o);return self.f.read(s)
if __name__=='__main__':
 import sys
 p=Pack(sys.argv[1])
 for n in p.files:
  if any(x.lower() in n.lower() for x in sys.argv[2:]):print(n)
