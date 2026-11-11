import json,os,pathlib,subprocess,sys,time
sys.path.insert(0,str(pathlib.Path.cwd()/'scripts'))
from owned_process import stop
prefix=sys.argv[1]
path=pathlib.Path('artifacts')
sentinel=path/(prefix+'-stop')
if sentinel.exists(): raise SystemExit('Existing stop marker; choose a unique prefix')
log=open(path/(prefix+'-app.log'),'w')
child=subprocess.Popen(['/usr/bin/rust-ui-native'],start_new_session=True,stdout=log,stderr=subprocess.STDOUT)
(path/(prefix+'-session.json')).write_text(json.dumps({'pid':child.pid,'application':'/usr/bin/rust-ui-native','GDK_BACKEND':os.environ.get('GDK_BACKEND'),'DISPLAY':os.environ.get('DISPLAY'),'started':time.time()},indent=2)+'\n')
print('Manual application PID',child.pid,flush=True)
try:
    deadline=time.monotonic()+1800
    while child.poll() is None and not sentinel.exists() and time.monotonic()<deadline: time.sleep(.25)
finally:
    stop(child,timeout=10);log.close()
