import pandas as pd
import numpy as np

# Load Attempt1
df = pd.read_csv('data/2025/Attempt/Attempt1.csv', encoding='utf-8')

print("Finding midrace stop (NOT at start/finish area)...\n")

# Start/finish location
START_LAT = 25.488435783
START_LON = 51.450190017

# Find where car is stopped
stopped = df[df['gps_speed'] < 1.0].copy()

# Calculate distance from start for each stopped point
stopped['dist_from_start'] = np.sqrt(
    (stopped['gps_latitude'] - START_LAT)**2 +
    (stopped['gps_longitude'] - START_LON)**2
)

# Filter out stops near start/finish (within 100m ~ 0.0009 degrees)
midrace_stopped = stopped[stopped['dist_from_start'] > 0.0009]

if len(midrace_stopped) == 0:
    print("No midrace stops found")
else:
    # Group consecutive stops
    midrace_stopped = midrace_stopped.copy()
    midrace_stopped['group'] = (midrace_stopped.index.to_series().diff() > 5).cumsum()

    # Find all midrace stops
    stop_groups = midrace_stopped.groupby('group').agg({
        'gps_latitude': 'mean',
        'gps_longitude': 'mean',
        'gps_speed': 'count',
        'dist_from_start': 'mean'
    })

    stop_groups.columns = ['lat', 'lon', 'duration', 'dist_from_start']
    stop_groups['duration_sec'] = stop_groups['duration'] * 0.1

    # Filter for stops longer than 3 seconds
    long_stops = stop_groups[stop_groups['duration_sec'] >= 3].sort_values('duration_sec', ascending=False)

    print(f"Found {len(long_stops)} midrace stops (>3 seconds, away from start/finish):\n")

    for idx, row in long_stops.iterrows():
        print(f"Location: [{row['lat']:.6f}, {row['lon']:.6f}]")
        print(f"Duration: {row['duration_sec']:.1f}s")
        print(f"Distance from start: {row['dist_from_start']*111:.0f}m")
        print()

    if len(long_stops) > 0:
        # Use the longest midrace stop
        stop = long_stops.iloc[0]
        print("="*60)
        print("MANDATORY MIDRACE STOP LINE:")
        print("="*60)
        print(f"stopLine: [{stop['lat']}, {stop['lon']}],")
        print()

        # Find which segment of the track outline this is closest to
        outline = [
            [25.488720817, 51.450041667], [25.489118117, 51.449772783],
            [25.489634967, 51.4494259], [25.490174433, 51.4490968],
            [25.490778517, 51.448718667], [25.491375483, 51.4483175],
            [25.49207065, 51.447894133], [25.49281835, 51.447592117],
            [25.49332805, 51.44779815], [25.493340667, 51.4485594],
            [25.492783567, 51.4492677], [25.492344683, 51.4499655],
            [25.492093667, 51.4504178], [25.491843833, 51.450869917],
            [25.491728483, 51.451032067], [25.491605533, 51.451620533],
            [25.49126045, 51.45209375], [25.4907238, 51.452599483],
            [25.4903161, 51.4532868], [25.490022133, 51.454066267],
            [25.489953533, 51.454641933], [25.489913083, 51.455323067],
            [25.489864867, 51.4560174], [25.489941783, 51.456826383],
            [25.490047383, 51.457621017], [25.4901291, 51.458597433],
            [25.489850217, 51.4592955], [25.489330333, 51.459635267],
            [25.4888498, 51.459938433], [25.48819055, 51.459881967],
            [25.4876145, 51.459461033], [25.487013117, 51.458864067],
            [25.487152133, 51.4578886], [25.487378983, 51.456626417],
            [25.487225267, 51.455559233], [25.486557067, 51.45511635],
            [25.485987883, 51.454824083], [25.485314717, 51.454472317],
            [25.484617433, 51.45412505], [25.483955633, 51.453340033],
            [25.484620783, 51.452493867], [25.485420317, 51.45201425],
            [25.48590055, 51.451725583], [25.486500183, 51.451353483],
            [25.48733545, 51.4508152], [25.487992833, 51.4504049],
            [25.488720817, 51.450041667]
        ]

        # Find closest segment
        min_dist = float('inf')
        closest_idx = 0
        for i, point in enumerate(outline):
            dist = np.sqrt((stop['lat'] - point[0])**2 + (stop['lon'] - point[1])**2)
            if dist < min_dist:
                min_dist = dist
                closest_idx = i

        print(f"Closest to track outline point {closest_idx}: {outline[closest_idx]}")
        print(f"Use segments {closest_idx-1} to {closest_idx+1} for red STOP line")
