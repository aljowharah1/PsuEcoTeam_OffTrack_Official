# PSU Racing - Raspberry Pi Setup

## Quick Setup

### 1. Copy this script to your Pi
```bash
scp gps_sync_streamer.py pi@berriespie.local:/home/pi/
```

### 2. Install dependencies on Pi
```bash
ssh pi@berriespie.local
pip3 install opencv-python paho-mqtt pyserial flask
```

### 3. Run the streamer
```bash
python3 gps_sync_streamer.py
```

## What This Script Does

1. **Captures USB camera** at `/dev/video8` (Global Shutter Camera)
2. **Reads GPS** from `/dev/serial0` (GPIO UART pins)
3. **Streams video** via HTTP MJPEG at `http://PI_IP:8001/stream`
4. **Publishes GPS** to MQTT topic `car/pi_gps` for sync with telemetry
5. **Provides status API** at `http://PI_IP:8001/status`

## Endpoints

| URL | Description |
|-----|-------------|
| `http://172.20.10.4:8001/` | Status page with live preview |
| `http://172.20.10.4:8001/stream` | MJPEG video stream |
| `http://172.20.10.4:8001/gps` | Current GPS as JSON |
| `http://172.20.10.4:8001/status` | Full system status |

## GPS Wiring (already done)

| GPS Pin | Pi GPIO |
|---------|---------|
| TX | GPIO15 (RX) |
| RX | GPIO14 (TX) |
| VCC | 3.3V |
| GND | GND |

## MQTT Topics

| Topic | Source | Data |
|-------|--------|------|
| `car/telemetry` | Joule meter | voltage, current, speed, GPS, etc. |
| `car/pi_gps` | This script | Pi GPS for video sync |

## Troubleshooting

### No GPS data
- Take Pi outdoors for satellite fix
- Check: `cat /dev/serial0` (should show NMEA sentences)

### Camera not found
- Check: `ls /dev/video*`
- Try: `v4l2-ctl --list-devices`

### Can't connect to MQTT
- Check WiFi connection
- Verify MQTT credentials in script
