#!/usr/bin/env python3
"""Fix the cloud-server.py file by removing garbage between functions"""

with open('cloud-server.py', 'r') as f:
    lines = f.readlines()

# Find where the mobile HTML function ends
mobile_end = -1
for i, line in enumerate(lines):
    if i > 1140 and '"""' in line:
        mobile_end = i
        break

# Find where the next valid decorator starts
next_decorator = -1
for i, line in enumerate(lines):
    if i > mobile_end and '@app.' in line:
        next_decorator = i
        break

print(f"Mobile function ends at line {mobile_end + 1}")
print(f"Next decorator found at line {next_decorator + 1}")

# Remove the garbage lines between
if mobile_end > 0 and next_decorator > 0:
    fixed_lines = lines[:mobile_end+1] + ['\n'] + lines[next_decorator:]
    
    with open('cloud-server-fixed.py', 'w') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Fixed file created: cloud-server-fixed.py")
    print(f"Removed {next_decorator - mobile_end - 1} lines of garbage")
else:
    print("❌ Could not identify the boundaries to fix")