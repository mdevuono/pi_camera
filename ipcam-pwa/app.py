"""
IPCam PWA - Flask backend
Serves the PWA at /cams and HLS stream files from /tmp/hls/
"""

import os
import subprocess
from flask import Flask, render_template, Response, send_from_directory
import logging

FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5050
HLS_DIR    = "/tmp/hls"
DEBUG      = False

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


@app.route("/cams")
def index():
    return render_template("index.html")


@app.route("/manifest.json")
def manifest():
    return app.send_static_file("manifest.json")


@app.route("/sw.js")
def service_worker():
    resp = Response(
        open("static/sw.js").read(),
        mimetype="application/javascript"
    )
    resp.headers["Service-Worker-Allowed"] = "/"
    return resp


@app.route("/hls/<path:filename>")
def hls_file(filename):
    """Serve HLS playlist and segment files written by ffmpeg."""
    response = send_from_directory(HLS_DIR, filename)
    response.headers["Cache-Control"] = "no-cache, no-store"
    response.headers["Access-Control-Allow-Origin"] = "*"
    if filename.endswith(".m3u8"):
        response.content_type = "application/vnd.apple.mpegurl"
    elif filename.endswith(".ts"):
        response.content_type = "video/MP2T"
    return response


@app.route("/api/health")
def health():
    result = subprocess.run(["pgrep", "-x", "ffmpeg"], capture_output=True)
    ffmpeg_ok  = result.returncode == 0
    playlist_ok = os.path.exists(os.path.join(HLS_DIR, "stream.m3u8"))
    return {"flask": True, "ffmpeg": ffmpeg_ok, "playlist": playlist_ok}


if __name__ == "__main__":
    os.makedirs(HLS_DIR, exist_ok=True)
    log.info("Starting IPCam PWA on %s:%d", FLASK_HOST, FLASK_PORT)
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=DEBUG)
