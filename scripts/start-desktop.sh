#!/usr/bin/env bash
# Start a private VNC/HTML5 GUI; never place port 6080 in public visibility.
set -euo pipefail
DATA_DIR="${HOME}/.config/ai-cloud-lab"
mkdir -p "${DATA_DIR}" "${HOME}/.vnc"
chmod 700 "${DATA_DIR}" "${HOME}/.vnc"
PASSWORD_FILE="${DATA_DIR}/vnc-password"
if [[ ! -s "${PASSWORD_FILE}" ]]; then
  # VNC legacy password auth uses only the first 8 bytes. Private GitHub port
  # authentication is the primary protection; never make 6080 public.
  python3 - <<'PYGEN' > "${PASSWORD_FILE}"
import secrets,string
alphabet=string.ascii_letters+string.digits
print(''.join(secrets.choice(alphabet) for _ in range(8)))
PYGEN
  chmod 600 "${PASSWORD_FILE}"
fi
if [[ ! -f "${HOME}/.vnc/passwd" ]]; then
  if command -v tigervncpasswd >/dev/null 2>&1; then vncpass=tigervncpasswd
  elif command -v vncpasswd >/dev/null 2>&1; then vncpass=vncpasswd
  else echo "VNC password utility missing; rebuild the devcontainer." >&2; exit 1
  fi
  "${vncpass}" -f < "${PASSWORD_FILE}" > "${HOME}/.vnc/passwd"
  chmod 600 "${HOME}/.vnc/passwd"
fi
cat > "${HOME}/.vnc/xstartup" <<'XSTART'
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
exec dbus-launch --exit-with-session startxfce4
XSTART
chmod 700 "${HOME}/.vnc/xstartup"
if ! pgrep -u "$(id -u)" -f 'Xtigervnc.*:1' >/dev/null; then
  vncserver :1 -geometry "${VNC_RESOLUTION:-1280x800}" -depth 24 -localhost yes -SecurityTypes VncAuth
fi
if ! python3 - <<'CHECK'
import socket,sys
s=socket.socket();s.settimeout(.5)
try: sys.exit(0 if s.connect_ex(('127.0.0.1',6080))==0 else 1)
finally: s.close()
CHECK
then
  nohup websockify --web /usr/share/novnc 127.0.0.1:6080 127.0.0.1:5901 \
    </dev/null >"${DATA_DIR}/novnc.log" 2>&1 &
  echo "$!" > "${DATA_DIR}/websockify.pid"
fi
printf '%s\n' 'Cloud desktop prepared: open port 6080 (PRIVATE) > /vnc.html' \
  'Display your temporary desktop password inside the Codespace: bash scripts/desktop-password.sh'
