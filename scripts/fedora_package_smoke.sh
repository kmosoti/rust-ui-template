#!/usr/bin/env bash
set -euo pipefail
package=$(realpath "$1")
mode=${2:-production}
# Root installs packages; the actual UI/driver always run as the ordinary app user.
dnf -y --disablerepo='*' --setopt=install_weak_deps=False install "$package"
dnf -y --disablerepo='*' reinstall "$package"
rpm -q gtk3 webkit2gtk4.1 webkitgtk6.0
runuser -u app -- python3 scripts/check_linux_package.py --format rpm
fixture=()
prefix=fedora-production
if [[ "$mode" == restricted ]]; then
  fixture=(--denial-fixture)
  prefix=fedora-denied
fi
runuser -u app -- dbus-run-session -- env -u WAYLAND_DISPLAY GDK_BACKEND=x11 xvfb-run -a python3 scripts/native_smoke.py --display-backend x11 --artifact-prefix "$prefix-x11" "${fixture[@]}"
runuser -u app -- python3 scripts/wayland_smoke.py --atspi --artifact-prefix "$prefix-wayland-software" "${fixture[@]}"
dnf -y --disablerepo='*' remove rust-ui-template
test ! -e /usr/bin/rust-ui-native
