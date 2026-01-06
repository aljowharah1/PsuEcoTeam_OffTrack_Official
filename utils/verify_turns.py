import csv
import numpy as np

# Read GPS data from Attempt1
coords = []
with open('2025/Attempt/Attempt1.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        lat = row.get('gps_latitude', '').strip()
        lon = row.get('gps_longitude', '').strip()
        if lat and lon and lat != '0' and lon != '0':
            try:
                coords.append([float(lat), float(lon), i])
            except:
                pass

print(f"Total GPS points: {len(coords)}")

# Current turns from script.js
current_turns = [
    (25.488882, 51.449847, "TURN 1"),
    (25.489365, 51.449525, "TURN 2"),
    (25.489992, 51.449127, "TURN 3"),
    (25.490604, 51.448730, "TURN 4"),
    (25.491297, 51.448316, "TURN 5"),
    (25.492009, 51.447888, "TURN 6"),
    (25.492879, 51.447485, "TURN 7"),
    (25.493345, 51.447801, "TURN 8"),
    (25.493382, 51.448345, "TURN 9"),
    (25.492747, 51.449290, "TURN 10"),
    (25.492123, 51.450306, "TURN 11"),
    (25.491904, 51.450694, "TURN 12"),
    (25.491656, 51.451190, "TURN 13"),
    (25.491361, 51.451944, "TURN 14"),
    (25.490774, 51.452510, "TURN 15"),
    (25.490242, 51.453365, "TURN 16"),
    (25.489979, 51.454601, "TURN 17"),
    (25.489864, 51.455846, "TURN 18"),
    (25.490009, 51.457242, "TURN 19"),
    (25.490121, 51.458552, "TURN 20"),
    (25.489900, 51.459162, "TURN 21"),
    (25.488862, 51.459922, "TURN 22"),
    (25.488290, 51.459868, "TURN 23"),
    (25.487802, 51.459580, "TURN 24"),
    (25.487006, 51.458766, "TURN 25"),
]

# Function to calculate bearing between two points
def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculate bearing in degrees (0-360)"""
    dLon = lon2 - lon1
    y = np.sin(dLon) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dLon)
    bearing = np.arctan2(y, x)
    bearing = np.degrees(bearing)
    bearing = (bearing + 360) % 360
    return bearing

def determine_turn_direction(lat, lon, coords, window=50):
    """Determine if turn is left or right based on bearing change"""
    # Find closest point
    min_dist = float('inf')
    closest_idx = 0
    for i, (clat, clon, _) in enumerate(coords):
        dist = np.sqrt((lat - clat)**2 + (lon - clon)**2)
        if dist < min_dist:
            min_dist = dist
            closest_idx = i

    # Need points before and after
    if closest_idx < window or closest_idx + window >= len(coords):
        return "unknown"

    # Get bearings
    before_lat, before_lon, _ = coords[closest_idx - window]
    turn_lat, turn_lon, _ = coords[closest_idx]
    after_lat, after_lon, _ = coords[closest_idx + window]

    bearing_in = calculate_bearing(before_lat, before_lon, turn_lat, turn_lon)
    bearing_out = calculate_bearing(turn_lat, turn_lon, after_lat, after_lon)

    # Calculate angle change
    angle_change = (bearing_out - bearing_in + 360) % 360

    # If angle change is more than 180, it's going the other way
    if angle_change > 180:
        angle_change = angle_change - 360

    # Determine turn direction
    if angle_change > 15:  # Turning left (counter-clockwise)
        return "left"
    elif angle_change < -15:  # Turning right (clockwise)
        return "right"
    else:
        return "straight"

print("\nVerifying turn directions:\n")
print("{ lat: LAT, lon: LON, name: 'TURN X', type: 'direction' },")

for lat, lon, name in current_turns:
    direction = determine_turn_direction(lat, lon, coords)
    print(f"{{ lat: {lat}, lon: {lon}, name: \"{name}\", type: \"{direction}\" }},")
