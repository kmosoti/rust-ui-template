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
echo 'ANDROID_LIFECYCLE avd-create-start'
printf 'no\n' | timeout --kill-after=5s 120s avdmanager create avd --name rust-ui-api36 --package 'system-images;android-36;google_apis;x86_64' --device pixel_7 --path "$ANDROID_AVD_HOME/rust-ui-api36.avd" --force
test -f "$ANDROID_AVD_HOME/rust-ui-api36.ini"
echo 'ANDROID_LIFECYCLE avd-create-complete'
export ANDROID_SERIAL=emulator-5554
exec python3 scripts/android_emulator_runner.py
