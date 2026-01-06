import paho.mqtt.client as mqtt
import pandas as pd
import json
import time
import sys

# HiveMQ Broker Details (matching your dashboard configuration)
BROKER = "8fac0c92ea0a49b8b56f39536ba2fd78.s1.eu.hivemq.cloud"
PORT = 8883  # SSL port
TOPIC = "car/telemetry"
USERNAME = "ShellJM"
PASSWORD = "psuEcoteam1st"

# Load Attempt1.csv Data
file_path = "data/2025/Attempt/Attempt1.csv"

print("Loading CSV data...")
try:
    df = pd.read_csv(file_path, encoding='utf-8')
    print(f"[OK] Loaded {len(df)} rows from {file_path}")
except Exception as e:
    print(f"[ERROR] Error loading CSV: {e}")
    sys.exit(1)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[OK] Connected to MQTT Broker successfully")
    else:
        print(f"[ERROR] Connection failed with code {rc}")

def on_publish(client, userdata, mid):
    pass  # Silently handle publish confirmations

def publish_data():
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    client.on_publish = on_publish

    print(f"Connecting to {BROKER}:{PORT}...")
    try:
        client.connect(BROKER, PORT, 60)
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
        sys.exit(1)

    client.loop_start()
    time.sleep(2)  # Wait for connection to establish

    print(f"\n[START] Starting replay of Attempt1 data...")
    print(f"[INFO] Publishing to topic: {TOPIC}")
    print(f"[INFO] {len(df)} packets to send\n")

    start_time = time.time()

    for index, row in df.iterrows():
        # Convert voltage from mV to V (jm3_voltage is in millivolts)
        voltage = row["jm3_voltage"] / 1000.0 if pd.notna(row["jm3_voltage"]) else 0.0

        # Convert current from mA to A (jm3_current is in milliamps)
        current = row["jm3_current"] / 1000.0 if pd.notna(row["jm3_current"]) else 0.0

        # Calculate power (W = V * A)
        power = voltage * current

        # Calculate speed from GPS speed (already in km/h)
        speed = row["gps_speed"] if pd.notna(row["gps_speed"]) else 0.0

        # Distance in km
        distance_km = row["dist"] if pd.notna(row["dist"]) else 0.0

        # GPS coordinates
        latitude = row["gps_latitude"] if pd.notna(row["gps_latitude"]) else 0.0
        longitude = row["gps_longitude"] if pd.notna(row["gps_longitude"]) else 0.0

        # RPM calculation (estimate from speed, assuming wheel diameter and gear ratio)
        # Typical EV: RPM ≈ speed * 50
        rpm = speed * 50

        # Build payload matching dashboard expectations
        payload = {
            "voltage": voltage,
            "current": current,
            "power": power,
            "speed": speed,
            "rpm": rpm,
            "distance_km": distance_km,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": row["obc_timestamp"] if pd.notna(row["obc_timestamp"]) else 0,
            "lap": row["lap_lap"] if pd.notna(row["lap_lap"]) else 0
        }

        # Publish payload
        payload_json = json.dumps(payload)
        result = client.publish(TOPIC, payload_json)

        # Progress indicator every 100 packets
        if index % 100 == 0:
            elapsed = time.time() - start_time
            print(f"[PROGRESS] {index}/{len(df)} packets | Speed: {speed:.1f} km/h | GPS: ({latitude:.6f}, {longitude:.6f}) | Elapsed: {elapsed:.1f}s")

        # Simulate real-time playback (100ms between packets)
        time.sleep(0.1)

    print(f"\n[COMPLETE] Replay complete! Sent {len(df)} packets")
    print(f"[COMPLETE] Total time: {time.time() - start_time:.1f}s")

    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    try:
        publish_data()
    except KeyboardInterrupt:
        print("\n\n[STOP] Replay interrupted by user")
        sys.exit(0)
