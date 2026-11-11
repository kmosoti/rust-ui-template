FROM fedora:44@sha256:15da97ed9aa94dd3d92c3925eb89520f6c80e07ea7ee24cba848d1f8b6912b3e
ARG APP_UID=1000
RUN dnf -y --setopt=install_weak_deps=False install webkit2gtk4.1 webkitgtk6.0 gtk3 dbus-x11 xorg-x11-server-Xvfb xorg-x11-xauth python3 desktop-file-utils shadow-utils && dnf clean all && useradd -m -u "$APP_UID" app
ENV HOME=/home/app
WORKDIR /work
