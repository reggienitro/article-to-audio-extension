#!/usr/bin/env python3
"""Update server to use mobile-optimized interface"""

# Read the mobile-optimized HTML
with open('mobile-optimized.html', 'r') as f:
    mobile_html = f.read()

# Read current server
with open('cloud-server.py', 'r') as f:
    server = f.read()

# Find and replace the get_mobile_html function
import re

pattern = r'(def get_mobile_html\(\):.*?return """)(.*?)(""")'
match = re.search(pattern, server, re.DOTALL)

if match:
    # Create new function with mobile-optimized HTML
    new_function = f'{match.group(1)}{mobile_html}{match.group(3)}'
    
    # Replace in server
    updated = server[:match.start()] + new_function + server[match.end():]
    
    # Write back
    with open('cloud-server.py', 'w') as f:
        f.write(updated)
    
    print("✅ Updated to mobile-optimized interface")
else:
    print("❌ Could not find function to update")