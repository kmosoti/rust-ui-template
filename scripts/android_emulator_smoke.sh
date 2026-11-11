#!/usr/bin/env bash
set -euo pipefail
: "${ANDROID_HOME:?Run setup_android.py --emulator first}"
mkdir -p artifacts
if [[ ! -r /dev/kvm || ! -w /dev/kvm ]]; then
  echo 'Hardware-accelerated Android validation requires readable/writable /dev/kvm' >&2
  exit 1
fi
# A fresh AVD on every run; no snapshots or writable device state are cached.
printf 'no\n' | avdmanager create avd --name rust-ui-api36 --package 'system-images;android-36;google_apis;x86_64' --device pixel_7 --force
emulator -avd rust-ui-api36 -no-window -gpu swiftshader -no-snapshot -noaudio -no-boot-anim -accel on -memory 2048 > artifacts/android-emulator.log 2>&1 &
emulator_pid=$!
trap 'kill "$emulator_pid" 2>/dev/null || true; wait "$emulator_pid" 2>/dev/null || true' EXIT
python3 - <<'PY'
import subprocess,time
end=time.monotonic()+600
while time.monotonic()<end:
    result=subprocess.run(['adb','shell','getprop','sys.boot_completed'],capture_output=True,text=True,timeout=10)
    if result.stdout.strip()=='1':break
    time.sleep(2)
else:raise SystemExit('Android emulator boot timed out')
PY
adb shell input keyevent 82
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
python3 scripts/android_smoke.py --apk artifacts/rust-ui-android-x86_64-debug.apk --test-apk artifacts/android-instrumentation.apk
python3 scripts/android_smoke.py --apk artifacts/android-restricted-fixture.apk --test-apk artifacts/android-instrumentation.apk --denial
