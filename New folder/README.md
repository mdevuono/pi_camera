# IPCam PWA

Live IP/USB camera viewer — iPhone PWA served from Raspberry Pi, accessible anywhere via Tailscale.

## Stack

```
SJCAM USB Camera
    │  MJPEG
    ▼
ffmpeg (ipcam-ffmpeg.service)
    │  transcodes MJPEG → H.264 Baseline
    │  writes HLS segments to /tmp/hls/
    ▼
Flask :5050 (ipcam-flask.service)
    │  serves PWA at /cams
    │  serves HLS files at /hls/
    ▼
Safari on iPhone
    │  native HLS playback
    ▼
Tailscale
    └─ http://100.72.88.110:5050/cams  (works on LAN and remotely)
```

## Pi Details

- **Hostname:** mdevuono_pi
- **Tailscale IP:** 100.72.88.110
- **App URL:** http://100.72.88.110:5050/cams

## Stream Settings

- Resolution: 1920×1080
- Framerate: 30fps
- Codec: H.264 Baseline (libx264, ultrafast)
- Bitrate: 1 Mbps
- HLS segment duration: 2s, rolling window of 3 segments

## Fresh Install Steps

### 1. Copy files to Pi

```powershell
# From Windows PowerShell in the ipcam-pwa folder:
ssh mdevuono_pi@100.72.88.110 "mkdir -p /home/mdevuono_pi/ipcam-pwa/static /home/mdevuono_pi/ipcam-pwa/templates"
scp -r . mdevuono_pi@100.72.88.110:/home/mdevuono_pi/ipcam-pwa/
```

### 2. Python venv

```bash
cd /home/mdevuono_pi/ipcam-pwa
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### 3. Install systemd services

```bash
sudo cp ipcam-ffmpeg.service /etc/systemd/system/
sudo cp ipcam-flask.service  /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ipcam-ffmpeg ipcam-flask
sudo systemctl start ipcam-ffmpeg
sleep 5
sudo systemctl start ipcam-flask
```

### 4. Verify

```bash
ls /tmp/hls/                                    # should show .ts files and stream.m3u8
curl -I http://127.0.0.1:5050/hls/stream.m3u8  # should return 200
```

### 5. Open on iPhone

Navigate to `http://100.72.88.110:5050/cams` in Safari.
To install as home screen app: Share → Add to Home Screen.

## Useful Commands

```bash
# Service status
sudo systemctl status ipcam-ffmpeg
sudo systemctl status ipcam-flask

# Live logs
sudo journalctl -u ipcam-ffmpeg -f
sudo journalctl -u ipcam-flask -f

# Restart after changes
sudo systemctl restart ipcam-ffmpeg
sudo systemctl restart ipcam-flask

# Check stream health
ffprobe -analyzeduration 10M -probesize 10M /tmp/hls/stream.m3u8 2>&1 | grep "Video:"
```

## Changing Resolution / Framerate

Edit `/etc/systemd/system/ipcam-ffmpeg.service` and update `-video_size` and `-framerate`.
Available resolutions from SJCAM: 1920x1080, 1280x720, 640x480, 320x240 — all at 30fps.

```bash
sudo systemctl daemon-reload
sudo systemctl restart ipcam-ffmpeg
```
