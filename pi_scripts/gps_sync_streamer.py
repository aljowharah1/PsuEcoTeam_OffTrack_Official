#!/usr/bin/env python3
"""
PSU Racing - GPS-Synced Camera Streamer
Captures USB camera frames with GPS timestamps for perfect sync with telemetry.

Run on Raspberry Pi:
    python3 gps_sync_streamer.py

Requirements:
    pip3 install opencv-python paho-mqtt pyserial flask
"""

import cv2
import json
import time
import threading
import serial
from datetime import datetime, timezone
from flask import Flask, Response
import paho.mqtt.client as mqtt

# ============== CONFIGURATION ==============
# Camera settings
CAMERA_DEVICE = "/dev/video8"  # USB Global Shutter Camera
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30
JPEG_QUALITY = 80

# GPS settings
GPS_PORT = "/dev/serial0"  # GPIO UART
GPS_BAUD = 9600

# MQTT settings
MQTT_BROKER = "8fac0c92ea0a49b8b56f39536ba2fd78.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "ShellJM"
MQTT_PASS = "psuEcoteam1st"
MQTT_TOPIC_VIDEO = "car/video"
MQTT_TOPIC_GPS = "car/pi_gps"

# HTTP Stream settings
HTTP_PORT = 8001

# ============== GLOBAL STATE ==============
class GPSState:
    def __init__(self):
        self.latitude = 0.0
        self.longitude = 0.0
        self.speed_knots = 0.0
        self.speed_kmh = 0.0
        self.heading = 0.0
        self.altitude = 0.0
        self.satellites = 0
        self.fix_quality = 0
        self.timestamp = None  # GPS timestamp (UTC)
        self.last_update = 0
        self.lock = threading.Lock()

    def to_dict(self):
        with self.lock:
            return {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "speed_kmh": self.speed_kmh,
                "heading": self.heading,
                "altitude": self.altitude,
                "satellites": self.satellites,
                "fix_quality": self.fix_quality,
                "gps_timestamp": self.timestamp.isoformat() if self.timestamp else None,
                "pi_timestamp": datetime.now(timezone.utc).isoformat()
            }

gps_state = GPSState()
frame_counter = 0
current_frame = None
frame_lock = threading.Lock()

# ============== NMEA PARSER ==============
def parse_nmea(sentence):
    """Parse NMEA sentences from GPS module."""
    global gps_state

    try:
        if not sentence.startswith('$'):
            return

        # Remove checksum
        if '*' in sentence:
            sentence = sentence.split('*')[0]

        parts = sentence.split(',')
        msg_type = parts[0]

        with gps_state.lock:
            # $GPGGA - Fix information
            if msg_type in ['$GPGGA', '$GNGGA']:
                if len(parts) >= 10:
                    # Time
                    if parts[1]:
                        time_str = parts[1]
                        hour = int(time_str[0:2])
                        minute = int(time_str[2:4])
                        second = float(time_str[4:])
                        today = datetime.now(timezone.utc).date()
                        gps_state.timestamp = datetime(
                            today.year, today.month, today.day,
                            hour, minute, int(second),
                            int((second % 1) * 1000000),
                            tzinfo=timezone.utc
                        )

                    # Latitude
                    if parts[2] and parts[3]:
                        lat = float(parts[2])
                        lat_deg = int(lat / 100)
                        lat_min = lat - (lat_deg * 100)
                        gps_state.latitude = lat_deg + (lat_min / 60)
                        if parts[3] == 'S':
                            gps_state.latitude = -gps_state.latitude

                    # Longitude
                    if parts[4] and parts[5]:
                        lon = float(parts[4])
                        lon_deg = int(lon / 100)
                        lon_min = lon - (lon_deg * 100)
                        gps_state.longitude = lon_deg + (lon_min / 60)
                        if parts[5] == 'W':
                            gps_state.longitude = -gps_state.longitude

                    # Fix quality
                    if parts[6]:
                        gps_state.fix_quality = int(parts[6])

                    # Satellites
                    if parts[7]:
                        gps_state.satellites = int(parts[7])

                    # Altitude
                    if parts[9]:
                        gps_state.altitude = float(parts[9])

                    gps_state.last_update = time.time()

            # $GPRMC - Recommended minimum (has speed and heading)
            elif msg_type in ['$GPRMC', '$GNRMC']:
                if len(parts) >= 8:
                    # Speed in knots
                    if parts[7]:
                        gps_state.speed_knots = float(parts[7])
                        gps_state.speed_kmh = gps_state.speed_knots * 1.852

                    # Heading/course
                    if len(parts) >= 9 and parts[8]:
                        gps_state.heading = float(parts[8])

            # $GPVTG - Course and speed
            elif msg_type in ['$GPVTG', '$GNVTG']:
                if len(parts) >= 8:
                    # True heading
                    if parts[1]:
                        gps_state.heading = float(parts[1])
                    # Speed in km/h
                    if parts[7]:
                        gps_state.speed_kmh = float(parts[7])

    except (ValueError, IndexError) as e:
        pass  # Skip malformed sentences

def gps_reader_thread():
    """Thread to continuously read GPS data."""
    print(f"[GPS] Opening {GPS_PORT} at {GPS_BAUD} baud...")

    try:
        ser = serial.Serial(GPS_PORT, GPS_BAUD, timeout=1)
        print("[GPS] Serial port opened successfully")

        buffer = ""
        while True:
            try:
                data = ser.read(ser.in_waiting or 1)
                if data:
                    buffer += data.decode('ascii', errors='ignore')

                    # Process complete sentences
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line.startswith('$'):
                            parse_nmea(line)

            except Exception as e:
                print(f"[GPS] Read error: {e}")
                time.sleep(0.1)

    except Exception as e:
        print(f"[GPS] Failed to open serial port: {e}")
        print("[GPS] Running without GPS - using system time for sync")

# ============== MQTT CLIENT ==============
mqtt_client = None

def mqtt_connect():
    """Connect to MQTT broker."""
    global mqtt_client

    mqtt_client = mqtt.Client(client_id=f"pi_camera_{int(time.time())}")
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
    mqtt_client.tls_set()

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("[MQTT] Connected to broker")
        else:
            print(f"[MQTT] Connection failed: {rc}")

    mqtt_client.on_connect = on_connect

    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        print(f"[MQTT] Connecting to {MQTT_BROKER}...")
    except Exception as e:
        print(f"[MQTT] Connection error: {e}")

def publish_gps():
    """Publish GPS data to MQTT."""
    if mqtt_client and mqtt_client.is_connected():
        data = gps_state.to_dict()
        data["source"] = "pi_gps"
        mqtt_client.publish(MQTT_TOPIC_GPS, json.dumps(data), qos=0)

# ============== CAMERA CAPTURE ==============
def camera_capture_thread():
    """Thread to capture camera frames."""
    global current_frame, frame_counter

    print(f"[CAM] Opening camera {CAMERA_DEVICE}...")

    cap = cv2.VideoCapture(CAMERA_DEVICE)
    if not cap.isOpened():
        # Try numeric device
        cap = cv2.VideoCapture(8)

    if not cap.isOpened():
        print("[CAM] Failed to open camera!")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"[CAM] Camera opened: {actual_w}x{actual_h} @ {actual_fps}fps")

    last_mqtt_time = 0
    mqtt_interval = 0.5  # Send GPS every 500ms

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[CAM] Frame capture failed")
            time.sleep(0.01)
            continue

        frame_counter += 1

        # Store frame for HTTP streaming
        with frame_lock:
            current_frame = frame.copy()

        # Publish GPS data periodically
        now = time.time()
        if now - last_mqtt_time >= mqtt_interval:
            publish_gps()
            last_mqtt_time = now

        time.sleep(0.001)  # Small delay to prevent CPU overload

# ============== HTTP MJPEG STREAM ==============
app = Flask(__name__)

def generate_mjpeg():
    """Generate MJPEG stream with GPS metadata."""
    global current_frame

    while True:
        with frame_lock:
            if current_frame is None:
                time.sleep(0.01)
                continue
            frame = current_frame.copy()

        # Get current GPS data
        gps_data = gps_state.to_dict()

        # Optionally overlay GPS info on frame (for debugging)
        # Uncomment to see GPS data on video:
        # cv2.putText(frame, f"GPS: {gps_data['latitude']:.6f}, {gps_data['longitude']:.6f}",
        #             (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        # cv2.putText(frame, f"Speed: {gps_data['speed_kmh']:.1f} km/h",
        #             (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Encode frame
        ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

@app.route('/')
def index():
    """Status page."""
    gps = gps_state.to_dict()
    return f"""
    <html>
    <head><title>PSU Racing - Pi Camera</title></head>
    <body style="font-family: monospace; background: #1a1a1a; color: #00ff88; padding: 20px;">
        <h1>PSU Racing - Pi Camera Stream</h1>
        <p>Stream URL: <a href="/stream" style="color: #ff6b35;">http://[PI_IP]:{HTTP_PORT}/stream</a></p>
        <h2>GPS Status</h2>
        <pre>{json.dumps(gps, indent=2)}</pre>
        <h2>Live Preview</h2>
        <img src="/stream" width="640" />
    </body>
    </html>
    """

@app.route('/stream')
def stream():
    """MJPEG stream endpoint."""
    return Response(
        generate_mjpeg(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/gps')
def gps_json():
    """Get current GPS data as JSON."""
    return json.dumps(gps_state.to_dict())

@app.route('/status')
def status():
    """Get full status."""
    return json.dumps({
        "camera": {
            "device": CAMERA_DEVICE,
            "frames": frame_counter
        },
        "gps": gps_state.to_dict(),
        "mqtt": {
            "connected": mqtt_client.is_connected() if mqtt_client else False,
            "broker": MQTT_BROKER
        }
    })

# ============== MAIN ==============
def main():
    print("=" * 50)
    print("  PSU Racing - GPS-Synced Camera Streamer")
    print("=" * 50)

    # Start GPS reader thread
    gps_thread = threading.Thread(target=gps_reader_thread, daemon=True)
    gps_thread.start()

    # Wait a moment for GPS to initialize
    time.sleep(1)

    # Connect to MQTT
    mqtt_connect()

    # Start camera capture thread
    cam_thread = threading.Thread(target=camera_capture_thread, daemon=True)
    cam_thread.start()

    # Start HTTP server
    print(f"\n[HTTP] Starting server on port {HTTP_PORT}...")
    print(f"[HTTP] Stream URL: http://172.20.10.4:{HTTP_PORT}/stream")
    print(f"[HTTP] Status URL: http://172.20.10.4:{HTTP_PORT}/status")
    print("\nPress Ctrl+C to stop.\n")

    app.run(host='0.0.0.0', port=HTTP_PORT, threaded=True)

if __name__ == '__main__':
    main()
