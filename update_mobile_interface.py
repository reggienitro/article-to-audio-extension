#!/usr/bin/env python3
"""Script to update cloud-server.py with the enhanced mobile interface"""

# Read the enhanced HTML
with open('enhanced-mobile-interface.html', 'r') as f:
    enhanced_html = f.read()

# Read the current server file
with open('cloud-server.py', 'r') as f:
    server_content = f.read()

# Find the get_mobile_html function
import re

# Pattern to match the entire get_mobile_html function
pattern = r'(def get_mobile_html\(\):.*?""")(.*?)(""")'
match = re.search(pattern, server_content, re.DOTALL)

if match:
    # Replace the HTML content within the function
    new_function = f'{match.group(1)}\n{enhanced_html}\n{match.group(3)}'
    
    # Replace in the server content
    updated_content = server_content[:match.start()] + new_function + server_content[match.end():]
    
    # Write back to the server file
    with open('cloud-server-enhanced.py', 'w') as f:
        f.write(updated_content)
    
    print("✅ Created cloud-server-enhanced.py with the enhanced mobile interface")
    print("Review the file and rename to cloud-server.py when ready")
else:
    print("❌ Could not find get_mobile_html function")
    print("Will create a new version manually...")
    
    # Find where to insert the new function
    def_index = server_content.find('def get_mobile_html():')
    if def_index != -1:
        # Find the end of the current function (next def or end of file)
        next_def = server_content.find('\ndef ', def_index + 1)
        if next_def == -1:
            next_def = len(server_content)
        
        # Build the new function
        new_mobile_function = f'''def get_mobile_html():
    """Enhanced mobile interface with modern UI"""
    return """{enhanced_html}"""
'''
        
        # Replace the old function with the new one
        updated_content = server_content[:def_index] + new_mobile_function + server_content[next_def:]
        
        with open('cloud-server-enhanced.py', 'w') as f:
            f.write(updated_content)
        
        print("✅ Created cloud-server-enhanced.py with enhanced interface (method 2)")