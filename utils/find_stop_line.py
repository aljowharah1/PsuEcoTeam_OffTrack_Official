import pandas as pd
import numpy as np

# Load both attempts
df1 = pd.read_csv('data/2025/Attempt/Attempt1.csv', encoding='utf-8')
df2 = pd.read_csv('data/2025/Attempt/Attempt2.csv', encoding='utf-8')

print("Analyzing Attempt1 and Attempt2 for stop locations...\n")

# Find where car stops (speed = 0 for at least 10-15 seconds)
def find_stops(df, name):
    print(f"\n{name}:")
    stopped = df[df['gps_speed'] < 0.5].copy()  # Speed near zero

    if len(stopped) == 0:
        print("No stops found")
        return None

    # Group consecutive stops
    stopped['group'] = (stopped.index.to_series().diff() > 10).cumsum()

    # Find longest stop
    stop_groups = stopped.groupby('group').agg({
        'gps_latitude': 'mean',
        'gps_longitude': 'mean',
        'gps_speed': 'count',
        'obc_timestamp': ['min', 'max']
    })

    # Duration in rows (each row ~100ms, so 150 rows = 15 seconds)
    stop_groups.columns = ['lat', 'lon', 'duration', 'time_start', 'time_end']
    stop_groups['duration_sec'] = stop_groups['duration'] * 0.1

    # Filter stops longer than 10 seconds
    long_stops = stop_groups[stop_groups['duration_sec'] >= 10].sort_values('duration_sec', ascending=False)

    if len(long_stops) > 0:
        print(f"Found {len(long_stops)} stops longer than 10 seconds:")
        for idx, row in long_stops.head(3).iterrows():
            print(f"  Stop: ({row['lat']:.6f}, {row['lon']:.6f}) - Duration: {row['duration_sec']:.1f}s")
        return long_stops.iloc[0]
    else:
        print("No stops longer than 10 seconds found")
        return None

stop1 = find_stops(df1, "Attempt1")
stop2 = find_stops(df2, "Attempt2")

# Average stop location if both found
if stop1 is not None and stop2 is not None:
    avg_lat = (stop1['lat'] + stop2['lat']) / 2
    avg_lon = (stop1['lon'] + stop2['lon']) / 2
    print(f"\n\nMandatory STOP Line Location (average):")
    print(f"Latitude:  {avg_lat}")
    print(f"Longitude: {avg_lon}")
    print(f"\nUse in script.js:")
    print(f"const STOP_LINE = [{avg_lat}, {avg_lon}];")
elif stop1 is not None:
    print(f"\n\nMandatory STOP Line Location (from Attempt1):")
    print(f"Latitude:  {stop1['lat']}")
    print(f"Longitude: {stop1['lon']}")
    print(f"\nUse in script.js:")
    print(f"const STOP_LINE = [{stop1['lat']}, {stop1['lon']}];")
elif stop2 is not None:
    print(f"\n\nMandatory STOP Line Location (from Attempt2):")
    print(f"Latitude:  {stop2['lat']}")
    print(f"Longitude: {stop2['lon']}")
    print(f"\nUse in script.js:")
    print(f"const STOP_LINE = [{stop2['lat']}, {stop2['lon']}];")
