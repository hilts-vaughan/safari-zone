"""Drive only an explicitly selected disposable X11 display for game validation."""
import ctypes as C,os,sys,time,subprocess
assert os.environ.get('DISPLAY','') not in ['',':0',':1'], 'Refuse to control a personal desktop'
x=C.CDLL('libX11.so.6');xt=C.CDLL('libXtst.so.6');x.XOpenDisplay.restype=C.c_void_p;x.XOpenDisplay.argtypes=[C.c_char_p];d=x.XOpenDisplay(None);assert d
x.XStringToKeysym.argtypes=[C.c_char_p];x.XStringToKeysym.restype=C.c_ulong;x.XKeysymToKeycode.argtypes=[C.c_void_p,C.c_ulong];x.XKeysymToKeycode.restype=C.c_uint
x.XFlush.argtypes=[C.c_void_p];xt.XTestFakeKeyEvent.argtypes=[C.c_void_p,C.c_uint,C.c_int,C.c_ulong];xt.XTestFakeMotionEvent.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_ulong];xt.XTestFakeButtonEvent.argtypes=[C.c_void_p,C.c_uint,C.c_int,C.c_ulong]
def key(name):
 code=x.XKeysymToKeycode(d,x.XStringToKeysym(name.encode()));assert code,name
 xt.XTestFakeKeyEvent(d,code,1,0);x.XFlush(d);time.sleep(.12)
 xt.XTestFakeKeyEvent(d,code,0,0);x.XFlush(d);time.sleep(.12)
def text(s):
 for c in s:key({' ':'space',"'":'apostrophe','-':'minus',',':'comma','.':'period'}.get(c,c))
if __name__=='__main__':
 if sys.argv[1]=='key':key(sys.argv[2])
 elif sys.argv[1]=='chord':
  code=x.XKeysymToKeycode(d,x.XStringToKeysym(sys.argv[2].encode()));assert code
  xt.XTestFakeKeyEvent(d,code,1,0);x.XFlush(d);time.sleep(.5);key(sys.argv[3]);time.sleep(.5)
  xt.XTestFakeKeyEvent(d,code,0,0);x.XFlush(d)
 elif sys.argv[1]=='hold':
  code=x.XKeysymToKeycode(d,x.XStringToKeysym(sys.argv[2].encode()));assert code
  xt.XTestFakeKeyEvent(d,code,1,0);x.XFlush(d);time.sleep(float(sys.argv[3]))
  xt.XTestFakeKeyEvent(d,code,0,0);x.XFlush(d)
 elif sys.argv[1]=='text':text(sys.argv[2])
 elif sys.argv[1] in ['command','command-open']:
  key('grave');time.sleep(.3);text(sys.argv[2]);key('Return');time.sleep(.4)
  if sys.argv[1]=='command':key('grave')
 elif sys.argv[1]=='submit':text(sys.argv[2]);key('Return')
 elif sys.argv[1]=='click':
  xt.XTestFakeMotionEvent(d,-1,int(sys.argv[2]),int(sys.argv[3]),0);xt.XTestFakeButtonEvent(d,1,1,0);xt.XTestFakeButtonEvent(d,1,0,0);x.XFlush(d)
