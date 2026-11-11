#!/usr/bin/env bash
set -euo pipefail
: "${ANDROID_HOME:?Run setup_android.py --emulator first}"
mkdir -p artifacts
if [[ ! -r /dev/kvm || ! -w /dev/kvm ]]; then
  echo 'Hardware-accelerated Android validation requires readable/writable /dev/kvm' >&2
  exit 1
fi
# Both Java SDK tools and the emulator must use the same explicit directory.
export ANDROID_USER_HOME="$PWD/.tools/android-user"
export ANDROID_EMULATOR_HOME="$ANDROID_USER_HOME"
export ANDROID_AVD_HOME="$ANDROID_USER_HOME/avd"
mkdir -p "$ANDROID_AVD_HOME"
# A fresh AVD on every run; no snapshots or writable device state are cached.
printf 'no\n' | avdmanager create avd --name rust-ui-api36 --package 'system-images;android-36;google_apis;x86_64' --device pixel_7 --path "$ANDROID_AVD_HOME/rust-ui-api36.avd" --force
test -f "$ANDROID_AVD_HOME/rust-ui-api36.ini"
export ANDROID_SERIAL=emulator-5554
emulator -port 5554 -avd rust-ui-api36 -wipe-data -no-window -gpu swiftshader -no-snapshot -noaudio -no-boot-anim -accel on -memory 2048 > artifacts/android-emulator.log 2>&1 &
emulator_pid=$!
trap 'timeout 10s adb -s emulator-5554 emu kill >/dev/null 2>&1 || true; kill "$emulator_pid" 2>/dev/null || true; wait "$emulator_pid" 2>/dev/null || true' EXIT
EMULATOR_PID="$emulator_pid" python3 - <<'PY'
import subprocess,time,os
from pathlib import Path
end=time.monotonic()+600
while time.monotonic()<end:
    try: os.kill(int(os.environ['EMULATOR_PID']), 0)
    except ProcessLookupError:
        print(Path('artifacts/android-emulator.log').read_text(errors='replace')[-8192:])
        raise SystemExit('Android emulator exited before boot completed')
    try:
        result=subprocess.run(['adb','shell','getprop','sys.boot_completed'],capture_output=True,text=True,timeout=10)
    except subprocess.TimeoutExpired:
        time.sleep(2)
        continue
    if result.stdout.strip()=='1':break
    time.sleep(2)
else:
    print(Path('artifacts/android-emulator.log').read_text(errors='replace')[-8192:])
    raise SystemExit('Android emulator boot timed out')
PY
adb shell input keyevent 82
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
python3 scripts/android_smoke.py --apk artifacts/rust-ui-android-x86_64-debug.apk --test-apk artifacts/android-instrumentation.apk
python3 scripts/android_smoke.py --apk artifacts/android-restricted-fixture.apk --test-apk artifacts/android-instrumentation.apk --denial
