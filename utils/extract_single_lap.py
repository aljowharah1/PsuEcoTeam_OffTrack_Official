import csv
import numpy as np

# Read GPS coordinates from Attempt1 only
coords = []
print("Reading Attempt1 data...")

with open('2025/Attempt/Attempt1.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        lat = row.get('gps_latitude', '').strip()
        lon = row.get('gps_longitude', '').strip()
        speed = row.get('gps_speed', '').strip()

        if lat and lon and lat != '0' and lon != '0':
            try:
                lat_f = float(lat)
                lon_f = float(lon)
                speed_f = float(speed) if speed else 0
                if speed_f > 1.0:  # Only include moving points
                    coords.append([lat_f, lon_f, i])
            except:
                pass

print(f"Total moving GPS points: {len(coords)}")

# Starting point (center of track)
start_lat = 25.488435783
start_lon = 51.450190017

# Find when car leaves start area
leave_index = None
for i, (lat, lon, idx) in enumerate(coords):
    dist = np.sqrt((lat - start_lat)**2 + (lon - start_lon)**2)
    if dist > 0.0003:  # ~33 meters
        leave_index = i
        print(f"Car leaves start at index {i} (row {idx})")
        break

# Find when car returns to start (completing first lap)
if leave_index:
    for i in range(leave_index + 100, len(coords)):  # Skip at least 100 points
        lat, lon, idx = coords[i]
        dist = np.sqrt((lat - start_lat)**2 + (lon - start_lon)**2)
        if dist < 0.0003:  # Back at start
            lap_coords = coords[leave_index:i+1]
            print(f"First lap complete at index {i} (row {idx})")
            print(f"Lap contains {len(lap_coords)} GPS points")
            break
    else:
        # If no return detected, take first 3000 points as one lap
        lap_coords = coords[leave_index:leave_index+3000]
        print(f"Using first 3000 points as lap estimate")

# Sample to about 40-50 points for smooth outline
sample_rate = max(1, len(lap_coords) // 45)
outline = lap_coords[::sample_rate]

# Extract just lat/lon
outline_coords = [[lat, lon] for lat, lon, _ in outline]

# Close the loop
if len(outline_coords) > 0:
    first = outline_coords[0]
    last = outline_coords[-1]
    dist = np.sqrt((first[0] - last[0])**2 + (first[1] - last[1])**2)
    if dist > 0.0001:
        outline_coords.append(first)

print(f"Final outline points: {len(outline_coords)}")

print("\n// Single lap track outline from Attempt1:")
print("outline: [")
for lat, lon in outline_coords:
    print(f"        [{lat}, {lon}],")
print("    ]")
