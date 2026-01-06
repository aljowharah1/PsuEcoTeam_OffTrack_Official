import pandas as pd
import numpy as np

# Load both attempts
df1 = pd.read_csv('data/2025/Attempt/Attempt1.csv', encoding='utf-8')
df2 = pd.read_csv('data/2025/Attempt/Attempt2.csv', encoding='utf-8')

def find_short_stops(df, name):
    print(f"\n{name}:")
    # Find where car is stopped or very slow
    stopped = df[df['gps_speed'] < 1.0].copy()

    if len(stopped) == 0:
        print("No stops found")
        return []

    # Group consecutive stops
    stopped['group'] = (stopped.index.to_series().diff() > 5).cumsum()

    # Find all stops
    stop_groups = stopped.groupby('group').agg({
        'gps_latitude': 'mean',
        'gps_longitude': 'mean',
        'gps_speed': 'count',
    })

    stop_groups.columns = ['lat', 'lon', 'duration']
    stop_groups['duration_sec'] = stop_groups['duration'] * 0.1  # Each row ~100ms

    # Filter for 3-10 second stops (midrace mandatory stop)
    midrace_stops = stop_groups[(stop_groups['duration_sec'] >= 3) &
                                 (stop_groups['duration_sec'] <= 15)].sort_values('duration_sec', ascending=False)

    print(f"Found {len(midrace_stops)} stops between 3-15 seconds (potential mandatory stops):")
    for idx, row in midrace_stops.iterrows():
        print(f"  [{row['lat']:.6f}, {row['lon']:.6f}] - Duration: {row['duration_sec']:.1f}s")

    return midrace_stops

stops1 = find_short_stops(df1, "Attempt1")
stops2 = find_short_stops(df2, "Attempt2")

print("\n" + "="*60)
print("MANDATORY STOP LINE LOCATION:")
print("="*60)

# Use the first midrace stop from Attempt1 or Attempt2
if len(stops1) > 0:
    stop = stops1.iloc[0]
    print(f"\nFrom Attempt1:")
    print(f"Latitude:  {stop['lat']}")
    print(f"Longitude: {stop['lon']}")
    print(f"Duration: {stop['duration_sec']:.1f}s")
    print(f"\nUpdate in script.js:")
    print(f"stopLine: [{stop['lat']}, {stop['lon']}],")
elif len(stops2) > 0:
    stop = stops2.iloc[0]
    print(f"\nFrom Attempt2:")
    print(f"Latitude:  {stop['lat']}")
    print(f"Longitude: {stop['lon']}")
    print(f"Duration: {stop['duration_sec']:.1f}s")
    print(f"\nUpdate in script.js:")
    print(f"stopLine: [{stop['lat']}, {stop['lon']}],")
