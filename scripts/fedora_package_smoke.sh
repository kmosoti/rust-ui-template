#!/usr/bin/env bash
set -euo pipefail
package=$(realpath "$1")
mode=${2:-production}
# Root installs packages; the actual UI/driver always run as the ordinary app user.
dnf -y --setopt=install_weak_deps=False install "$package"
dnf -y reinstall "$package"
rpm -q gtk3 webkit2gtk4.1 webkitgtk6.0
runuser -u app -- python3 scripts/check_linux_package.py --format rpm
if [[ "$mode" == restricted ]]; then
  runuser -u app -- dbus-run-session -- xvfb-run -a python3 scripts/native_smoke.py --artifact-prefix fedora-denied --denial-fixture
else
  runuser -u app -- dbus-run-session -- xvfb-run -a python3 scripts/native_smoke.py --artifact-prefix fedora-production
fi
dnf -y remove rust-ui-template
test ! -e /usr/bin/rust-ui-native
