# Open only on demand in GitHub Codespaces. No GPU, paid servers, or paid APIs.
FROM mcr.microsoft.com/devcontainers/javascript-node:1-22-bookworm
ARG DEBIAN_FRONTEND=noninteractive
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    xfce4 xfce4-terminal mousepad thunar \
    tigervnc-standalone-server tigervnc-tools novnc websockify \
    dbus-x11 xauth xfonts-base fonts-dejavu-core \
    firefox-esr ffmpeg curl ca-certificates procps python3-pip \
    && rm -rf /var/lib/apt/lists/*
