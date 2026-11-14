import json, os, platform, subprocess
from pathlib import Path
from gi.repository import Gio

def run(args):
    r=subprocess.run(args,capture_output=True,text=True,timeout=10)
    return {'command':args,'returncode':r.returncode,'stdout':r.stdout.strip(),'stderr':r.stderr.strip()}
bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
r=bus.call_sync('org.gnome.Mutter.DisplayConfig','/org/gnome/Mutter/DisplayConfig','org.gnome.Mutter.DisplayConfig','GetCurrentState',None,None,0,5000,None).unpack()
report={'system':platform.platform(),'os_release':dict(platform.freedesktop_os_release()),'session':{k:os.environ.get(k) for k in ('XDG_SESSION_TYPE','XDG_CURRENT_DESKTOP','WAYLAND_DISPLAY','DISPLAY')},'mutter_serial':r[0],'outputs':[{'connector':m[0][0],'vendor':m[0][1],'product':m[0][2],'current_modes':[{'id':v[0],'width':v[1],'height':v[2],'refresh':v[3]} for v in m[1] if v[6].get('is-current')]} for m in r[1]],'logical_monitors':[{'x':m[0],'y':m[1],'scale':m[2],'transform':m[3],'primary':m[4],'outputs':[o[0] for o in m[5]]} for m in r[2]],'checks':[run(c) for c in [['rpm','-q','gtk3','mutter','gnome-shell','webkit2gtk4.1','webkitgtk6.0','orca','python3-pyatspi','gobject-introspection','mesa-dri-drivers','rust-ui-template'],['gsettings','get','org.gnome.desktop.interface','toolkit-accessibility'],['gsettings','get','org.gnome.desktop.a11y.applications','screen-reader-enabled'],['gsettings','get','org.gnome.desktop.interface','text-scaling-factor'],['gsettings','get','org.gnome.mutter','experimental-features'],['lspci','-nnk']]]}
# Keep only display adapters from PCI output, not unrelated devices.
pci=report['checks'][-1]['stdout'].splitlines(); keep=[]; active=False
for line in pci:
    if line and not line[0].isspace(): active=any(k in line for k in ('VGA compatible','3D controller','Display controller'))
    if active: keep.append(line)
report['checks'][-1]['stdout']='\n'.join(keep)
Path('artifacts/machine-'+__import__('sys').argv[1]+'.json').write_text(json.dumps(report,indent=2)+'\n')
