#!/usr/bin/env python3
"""Rebuild the server file correctly"""

# Read the enhanced HTML
with open('enhanced-mobile-interface.html', 'r') as f:
    enhanced_html = f.read()

# Read the backup server
with open('cloud-server-backup.py', 'r') as f:
    backup = f.read()

# Find and replace the get_mobile_html function completely
import re

# Find the old get_mobile_html function
pattern = r'def get_mobile_html\(\):.*?(?=\n(?:def |@app\.|if __name__))'
match = re.search(pattern, backup, re.DOTALL)

if match:
    # Create the new function
    new_function = f'''def get_mobile_html():
    """Enhanced mobile interface with modern UI"""
    return """{enhanced_html}"""
'''
    
    # Replace in the backup
    fixed = backup[:match.start()] + new_function + backup[match.end():]
    
    # Write the fixed version
    with open('cloud-server.py', 'w') as f:
        f.write(fixed)
    
    print("✅ Server file rebuilt successfully!")
else:
    print("❌ Could not find function to replace")