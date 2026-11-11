#!/usr/bin/env bash
# Install Ubuntu runtime/build prerequisites from one owned signed index set.
set -euo pipefail
elevate=(sudo)
if [[ $(id -u) == 0 ]]; then elevate=(); fi
apt_directory=$(mktemp -d /tmp/rust-ui-apt.XXXXXX)
cleanup() {
  result=$?
  trap - EXIT
  if ! "${elevate[@]}" rm -rf -- "$apt_directory"; then
    echo 'Owned apt metadata cleanup failed' >&2
    if [[ $result == 0 ]]; then result=1; fi
  fi
  exit "$result"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
chmod 755 "$apt_directory"
"${elevate[@]}" install -d -m 755 "$apt_directory/lists/partial"
# Retain Ubuntu's Signed-By, suites, components and validity/signature checks.
# The third-party mirror is selected for reachability, never as a trust root.
sed 's|mirror+file:/etc/apt/apt-mirrors.txt|https://mirrors.edge.kernel.org/ubuntu|g; s|mirror+file:/etc/apt/apt-security-mirrors.txt|https://mirrors.edge.kernel.org/ubuntu|g; s|http://azure.archive.ubuntu.com/ubuntu|https://mirrors.edge.kernel.org/ubuntu|g; s|https://azure.archive.ubuntu.com/ubuntu|https://mirrors.edge.kernel.org/ubuntu|g; s|http://archive.ubuntu.com/ubuntu|https://mirrors.edge.kernel.org/ubuntu|g; s|http://security.ubuntu.com/ubuntu|https://mirrors.edge.kernel.org/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources > "$apt_directory/ubuntu.sources"
options=(-o "Dir::Etc::sourcelist=$apt_directory/ubuntu.sources" -o Dir::Etc::sourceparts=- -o "Dir::State::lists=$apt_directory/lists" -o Dir::Cache::pkgcache= -o Dir::Cache::srcpkgcache= -o Acquire::GzipIndexes=false -o Acquire::http::Timeout=20 -o Acquire::https::Timeout=20 -o Acquire::Retries=1)
# Test-only transport configuration may supply the cloud environment CA; it
# never disables TLS, repository signatures or metadata validity checks.
if [[ -n ${RUST_UI_APT_CA:-} ]]; then options+=(-o "Acquire::https::CaInfo=$RUST_UI_APT_CA"); fi
"${elevate[@]}" apt-get "${options[@]}" update
"${elevate[@]}" apt-get "${options[@]}" indextargets --format '$(FILENAME) $(RELEASE) $(COMPONENT) $(ARCHITECTURE)'
"${elevate[@]}" apt-cache "${options[@]}" policy libwebkit2gtk-4.1-dev weston at-spi2-core
"${elevate[@]}" apt-get "${options[@]}" install -y libwebkit2gtk-4.1-dev libayatana-appindicator3-dev librsvg2-dev patchelf webkit2gtk-driver xvfb desktop-file-utils weston wayland-utils libgl1-mesa-dri libegl-mesa0 libglib2.0-bin python3-gi python3-pyatspi at-spi2-core fonts-noto-core
