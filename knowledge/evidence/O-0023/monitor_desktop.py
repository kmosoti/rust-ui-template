"""Task-local owned-descendant DRM usage capture; no settings/input injection."""
import json, os, pathlib, subprocess, sys, time
sys.path.insert(0, str(pathlib.Path.cwd()/'scripts'))
from native_smoke import owned_process_snapshot
from owned_process import stop
prefix = sys.argv[1]
command = sys.argv[2:]
started = time.monotonic()
rows = []; capture_errors = {}; dropped_rows = 0
process = subprocess.Popen(command, start_new_session=True)
try:
    while process.poll() is None and time.monotonic()-started < 270:
        owned = owned_process_snapshot(process.pid)
        for item in owned['processes']:
            pid = item['pid']; base=pathlib.Path('/proc')/str(pid)
            try:
                for fd in list((base/'fdinfo').iterdir())[:256]:
                    fields = dict(line.split(':',1) for line in fd.read_text()[:16384].splitlines() if line.startswith('drm-') and ':' in line)
                    if not fields: continue
                    values={k:v.strip() for k,v in fields.items() if k in ('drm-driver','drm-pdev','drm-client-id') or k.startswith('drm-engine-')}
                    maps = [line.split()[-1] for line in (base/'maps').read_text().splitlines() if any(s in line for s in ('/dri/','libEGL','libGLX','libnvidia','libvulkan'))]
                    if len(rows) >= 50000:
                        dropped_rows += 1; continue
                    rows.append({'elapsed':round(time.monotonic()-started,6),'pid':pid,'name':item.get('Name'),'ppid':item.get('PPid'),'fd':fd.name,'device':str((base/'fd'/fd.name).resolve()),'drm':values,'graphics_libraries':sorted(set(maps))})
            except (OSError,ValueError) as error:
                key=type(error).__name__; capture_errors[key]=capture_errors.get(key,0)+1
        time.sleep(.1)
    if process.poll() is None: raise TimeoutError('desktop monitor deadline270s')
finally:
    stop(process,timeout=21)
    pathlib.Path('artifacts/'+prefix+'-gpu-fdinfo.json').write_text(json.dumps({'command':command,'interval_seconds':.1,'root_pid':process.pid,'returncode':process.returncode,'rows':rows,'capture_errors':capture_errors,'dropped_rows':dropped_rows,'hardware_gpu_verified':False,'method':'owned descendant /proc drm fdinfo; assess engine deltas before attributing'},indent=2)+'\n')
sys.exit(process.returncode)
