"""
PSU Racing - Racing Line Overlay API
Calculates pixel coordinates for ideal racing line overlay based on current position.

Deploy to Vercel as serverless function:
    /api/racing_line

Usage:
    POST /api/racing_line
    {
        "latitude": 25.488435,
        "longitude": 51.450190,
        "heading": 45.2,
        "speed": 32.5,
        "camera_width": 1280,
        "camera_height": 720
    }

Returns:
    {
        "overlay_points": [[x1, y1], [x2, y2], ...],
        "target_speed": 28.5,
        "deviation_m": 2.3,
        "segment": "Q2",
        "efficiency": 156.7
    }
"""

import json
import math
from http.server import BaseHTTPRequestHandler

# ============== RACING LINE DATA ==============
# This will be loaded from ideal_racing_line.json
# For now, using Lusail Short Circuit ideal line

RACING_LINE = None
SEGMENTS = None

def load_racing_line():
    """Load racing line data from JSON."""
    global RACING_LINE, SEGMENTS

    try:
        with open('ideal_racing_line.json', 'r') as f:
            data = json.load(f)
            RACING_LINE = data.get('racing_line', [])
            SEGMENTS = data.get('segments', [])
            print(f"Loaded racing line: {len(RACING_LINE)} points, {len(SEGMENTS)} segments")
    except FileNotFoundError:
        # Use default Lusail data if JSON not found
        print("Using default Lusail racing line")
        RACING_LINE = generate_default_racing_line()
        SEGMENTS = generate_default_segments()

def generate_default_racing_line():
    """Generate default racing line for Lusail Short Circuit."""
    # Based on your notebook's track outline
    outline = [
        [25.488720817, 51.450041667],
        [25.489118117, 51.449772783],
        [25.489634967, 51.4494259],
        [25.490174433, 51.4490968],
        [25.490778517, 51.448718667],
        [25.491375483, 51.4483175],
        [25.49207065, 51.447894133],
        [25.49281835, 51.447592117],
        [25.49332805, 51.44779815],
        [25.493340667, 51.4485594],
        [25.492783567, 51.4492677],
        [25.492344683, 51.4499655],
        [25.492093667, 51.4504178],
        [25.491843833, 51.450869917],
        [25.491728483, 51.451032067],
        [25.491605533, 51.451620533],
        [25.49126045, 51.45209375],
        [25.4907238, 51.452599483],
        [25.4903161, 51.4532868],
        [25.490022133, 51.454066267],
        [25.489953533, 51.454641933],
        [25.489913083, 51.455323067],
        [25.489864867, 51.4560174],
        [25.489941783, 51.456826383],
        [25.490047383, 51.457621017],
        [25.4901291, 51.458597433],
        [25.489850217, 51.4592955],
        [25.489330333, 51.459635267],
        [25.4888498, 51.459938433],
        [25.48819055, 51.459881967],
        [25.4876145, 51.459461033],
        [25.487013117, 51.458864067],
        [25.487152133, 51.4578886],
        [25.487378983, 51.456626417],
        [25.487225267, 51.455559233],
        [25.486557067, 51.45511635],
        [25.485987883, 51.454824083],
        [25.485314717, 51.454472317],
        [25.484617433, 51.45412505],
        [25.483955633, 51.453340033],
        [25.484620783, 51.452493867],
        [25.485420317, 51.45201425],
        [25.48590055, 51.451725583],
        [25.486500183, 51.451353483],
        [25.48733545, 51.4508152],
        [25.487992833, 51.4504049],
        [25.488720817, 51.450041667]
    ]

    racing_line = []
    for i, point in enumerate(outline):
        # Calculate target speed based on track section
        # Higher speed on straights, lower on turns
        segment_idx = i // (len(outline) // 4)
        target_speeds = [30, 25, 28, 32]  # Q1, Q2, Q3, Q4

        racing_line.append({
            'lat': point[0],
            'lon': point[1],
            'target_speed': target_speeds[min(segment_idx, 3)],
            'segment_name': f'Q{min(segment_idx, 3) + 1}',
            'segment_id': min(segment_idx, 3)
        })

    return racing_line

def generate_default_segments():
    """Generate default segment data."""
    return [
        {'id': 0, 'name': 'Q1', 'target_speed': 30, 'efficiency': 150.0},
        {'id': 1, 'name': 'Q2', 'target_speed': 25, 'efficiency': 145.0},
        {'id': 2, 'name': 'Q3', 'target_speed': 28, 'efficiency': 160.0},
        {'id': 3, 'name': 'Q4', 'target_speed': 32, 'efficiency': 155.0}
    ]

# ============== GPS MATH ==============
def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points in kilometers."""
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def find_nearest_point(lat, lon):
    """Find nearest point on racing line and its index."""
    if not RACING_LINE:
        return None, 0, float('inf')

    min_dist = float('inf')
    nearest_idx = 0
    nearest_point = None

    for i, point in enumerate(RACING_LINE):
        dist = haversine(lat, lon, point['lat'], point['lon'])
        if dist < min_dist:
            min_dist = dist
            nearest_idx = i
            nearest_point = point

    return nearest_point, nearest_idx, min_dist * 1000  # Return distance in meters

# ============== CAMERA PROJECTION ==============
# GoPro / Wide angle camera settings
CAMERA_HEIGHT_M = 0.8       # Height from ground
CAMERA_FOV_H = 118          # Horizontal FOV degrees
CAMERA_FOV_V = 69           # Vertical FOV degrees
LOOKAHEAD_M = 40            # How far ahead to project

def gps_to_pixel(target_lat, target_lon, car_lat, car_lon, car_heading,
                 cam_width=1280, cam_height=720):
    """
    Project GPS point to screen pixel coordinates.
    Returns (x, y) or None if not visible.
    """
    # Calculate relative position in meters
    dx = haversine(car_lat, car_lon, car_lat, target_lon) * 1000
    if target_lon < car_lon:
        dx = -dx

    dy = haversine(car_lat, car_lon, target_lat, car_lon) * 1000
    if target_lat < car_lat:
        dy = -dy

    # Rotate by heading (car's direction)
    heading_rad = math.radians(car_heading)
    rel_x = dx * math.cos(heading_rad) + dy * math.sin(heading_rad)
    rel_y = -dx * math.sin(heading_rad) + dy * math.cos(heading_rad)

    # Check if in front of car and within range
    if rel_y <= 0.5 or rel_y > LOOKAHEAD_M:
        return None

    # Calculate angular position
    angle_h = math.degrees(math.atan2(rel_x, rel_y))
    if abs(angle_h) > CAMERA_FOV_H / 2:
        return None  # Outside horizontal FOV

    angle_v = math.degrees(math.atan2(CAMERA_HEIGHT_M, rel_y))

    # Convert angles to pixel coordinates
    px = int(cam_width / 2 + (angle_h / (CAMERA_FOV_H / 2)) * (cam_width / 2))
    py = int(cam_height / 2 + (angle_v / (CAMERA_FOV_V / 2)) * (cam_height / 2))

    # Clamp to frame bounds
    px = max(0, min(px, cam_width - 1))
    py = max(0, min(py, cam_height - 1))

    return [px, py]

def calculate_overlay(lat, lon, heading, speed, cam_width=1280, cam_height=720):
    """
    Calculate overlay points for the ideal racing line.
    Returns list of pixel coordinates to draw.
    """
    if not RACING_LINE:
        load_racing_line()

    # Find nearest point on racing line
    nearest_point, nearest_idx, deviation_m = find_nearest_point(lat, lon)

    if nearest_point is None:
        return {
            'overlay_points': [],
            'target_speed': 0,
            'deviation_m': 0,
            'segment': 'N/A',
            'efficiency': 0,
            'on_track': False
        }

    # Get next N points on racing line (lookahead)
    overlay_points = []
    num_points = min(60, len(RACING_LINE) - nearest_idx)

    for i in range(nearest_idx, nearest_idx + num_points):
        idx = i % len(RACING_LINE)  # Wrap around for closed track
        point = RACING_LINE[idx]

        pixel = gps_to_pixel(
            point['lat'], point['lon'],
            lat, lon, heading,
            cam_width, cam_height
        )

        if pixel:
            overlay_points.append(pixel)

    # Get current segment info
    segment = SEGMENTS[nearest_point['segment_id']] if SEGMENTS else {}

    return {
        'overlay_points': overlay_points,
        'target_speed': nearest_point.get('target_speed', 0),
        'deviation_m': round(deviation_m, 2),
        'segment': nearest_point.get('segment_name', 'N/A'),
        'efficiency': segment.get('efficiency', 0),
        'on_track': deviation_m < 10,  # Within 10m of racing line
        'speed_diff': round(nearest_point.get('target_speed', 0) - speed, 1)
    }

# ============== VERCEL HANDLER ==============
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode('utf-8'))

            lat = data.get('latitude', 0)
            lon = data.get('longitude', 0)
            heading = data.get('heading', 0)
            speed = data.get('speed', 0)
            cam_width = data.get('camera_width', 1280)
            cam_height = data.get('camera_height', 720)

            result = calculate_overlay(lat, lon, heading, speed, cam_width, cam_height)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_GET(self):
        """Health check and info."""
        load_racing_line()

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        info = {
            'service': 'PSU Racing Line Overlay API',
            'racing_line_points': len(RACING_LINE) if RACING_LINE else 0,
            'segments': len(SEGMENTS) if SEGMENTS else 0,
            'usage': 'POST with {latitude, longitude, heading, speed, camera_width, camera_height}'
        }
        self.wfile.write(json.dumps(info).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

# Initialize on import
load_racing_line()
