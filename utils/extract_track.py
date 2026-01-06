import csv

# Read GPS coordinates from race data
all_coords = []
print("Reading race data...")

with open('race_data.csv', 'r') as f:
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
                all_coords.append([lat_f, lon_f, speed_f, i])
            except:
                pass

print(f"Total GPS points collected: {len(all_coords)}")

# Find where car actually starts moving (speed > 2 km/h consistently)
moving_start = 0
for i, (lat, lon, speed, idx) in enumerate(all_coords):
    if speed > 2.0:  # Car is moving
        moving_start = i
        break

print(f"Car starts moving at index {moving_start}")

# Get data from when car is moving onwards
moving_coords = all_coords[moving_start:]

# Take first 3000-4000 points (should be enough for a full lap)
lap_data = moving_coords[:4000]

# Sample to get ~50-60 points for smooth outline
sample_rate = max(1, len(lap_data) // 55)
outline = lap_data[::sample_rate]

# Close the loop by adding first point at end
if len(outline) > 0 and outline[-1][:2] != outline[0][:2]:
    outline.append(outline[0])

print(f"Track outline points: {len(outline)}")
print(f"From row {all_coords[moving_start][3]} to row {lap_data[-1][3]}")

print("\n// REAL Lusail Circuit GPS coordinates (actual driven path):")
print("outline: [")
for lat, lon, _, _ in outline:
    print(f"    [{lat}, {lon}],")
print("]")


