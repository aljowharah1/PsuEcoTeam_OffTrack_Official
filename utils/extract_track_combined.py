import csv
import numpy as np

# Read GPS coordinates from both attempts
all_coords = []
print("Reading Attempt1 and Attempt2 data...")

# Read Attempt 1
with open('2025/Attempt/Attempt1.csv', 'r') as f:
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
                if speed_f > 0.5:  # Only include moving points
                    all_coords.append([lat_f, lon_f, speed_f, 1, i])  # 1 = attempt 1
            except:
                pass

# Read Attempt 2
with open('2025/Attempt/Attempt2.csv', 'r') as f:
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
                if speed_f > 0.5:  # Only include moving points
                    all_coords.append([lat_f, lon_f, speed_f, 2, i])  # 2 = attempt 2
            except:
                pass

print(f"Total GPS points collected: {len(all_coords)}")

# Sample points evenly around the track (about 80-100 points for smooth outline)
sample_rate = max(1, len(all_coords) // 80)
outline = all_coords[::sample_rate]

# Extract just lat/lon
outline_coords = [[pt[0], pt[1]] for pt in outline]

# Close the loop if needed
if len(outline_coords) > 0:
    first = outline_coords[0]
    last = outline_coords[-1]
    dist = np.sqrt((first[0] - last[0])**2 + (first[1] - last[1])**2)
    if dist > 0.0001:  # If not already closed
        outline_coords.append(first)

print(f"Track outline points: {len(outline_coords)}")

print("\n// Track outline from Attempt1 and Attempt2 GPS data:")
print("outline: [")
for lat, lon in outline_coords:
    print(f"    [{lat}, {lon}],")
print("]")
