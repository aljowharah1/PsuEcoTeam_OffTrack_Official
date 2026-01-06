with open('mobile-dashboard/script.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with the closing bracket of outline array
# It should be around line 136
outline_end = None
for i in range(130, 150):
    if i < len(lines) and lines[i].strip() == '],':
        outline_end = i
        break

if outline_end:
    # Find the next valid line (should start with }; or a comment)
    # Remove all the orphaned coordinate lines
    next_valid = None
    for i in range(outline_end + 1, len(lines)):
        line = lines[i].strip()
        if line.startswith('};') or line.startswith('/*') or (line and not line.startswith('[')):
            next_valid = i
            break

    if next_valid:
        # Keep everything before outline_end+1 and everything from next_valid onwards
        fixed_lines = lines[:outline_end+1] + lines[next_valid:]

        with open('mobile-dashboard/script.js', 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)

        print(f"[OK] Fixed script.js - removed orphaned lines {outline_end+2} to {next_valid}")
        print(f"[OK] Removed {next_valid - outline_end - 1} orphaned coordinate lines")
    else:
        print("[ERROR] Could not find next valid line")
else:
    print("[ERROR] Could not find outline closing bracket")
