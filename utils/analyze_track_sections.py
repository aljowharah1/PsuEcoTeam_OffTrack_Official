import pandas as pd
import numpy as np

# Load both attempts
df1 = pd.read_csv('data/2025/Attempt/Attempt1.csv', encoding='utf-8')

# Get the track outline points
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

# The mandatory stop should be along one of the straight sections
# Looking at the track, likely candidates are:
# 1. After the first turn section (indices 10-15)
# 2. The long straight (indices 16-22)
# 3. Near the end before start (indices 40-46)

print("Track outline sections:\n")
for i in range(0, len(outline), 5):
    end = min(i+5, len(outline))
    print(f"Points {i}-{end-1}:")
    for j in range(i, end):
        print(f"  {j}: [{outline[j][0]}, {outline[j][1]}]")
    print()

print("\nBased on the green START line at points 0-2,")
print("the mandatory STOP line should likely be:")
print("\nOption 1 (Mid-track straight): Points 13-15")
print(f"  Location: [{outline[13][0]}, {outline[13][1]}]")
print("\nOption 2 (Long straight): Points 19-21")
print(f"  Location: [{outline[19][0]}, {outline[19][1]}]")
print("\nOption 3 (Before finish): Points 43-45")
print(f"  Location: [{outline[43][0]}, {outline[43][1]}]")
