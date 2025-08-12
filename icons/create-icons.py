#!/usr/bin/env python3
"""
Create simple SVG icons for the browser extension
"""

def create_svg_icon(size, filename):
    """Create a simple headphones icon SVG"""
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4a90e2;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#357abd;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Headband -->
  <path d="M{size//4} {size//3} Q{size//2} {size//6} {3*size//4} {size//3}" 
        fill="none" stroke="url(#grad1)" stroke-width="{size//16}" stroke-linecap="round"/>
  
  <!-- Left earpiece -->
  <circle cx="{size//4}" cy="{2*size//3}" r="{size//8}" fill="url(#grad1)"/>
  <circle cx="{size//4}" cy="{2*size//3}" r="{size//12}" fill="#fff"/>
  
  <!-- Right earpiece -->
  <circle cx="{3*size//4}" cy="{2*size//3}" r="{size//8}" fill="url(#grad1)"/>
  <circle cx="{3*size//4}" cy="{2*size//3}" r="{size//12}" fill="#fff"/>
  
  <!-- Connecting wires -->
  <path d="M{size//4} {size//3} L{size//4} {2*size//3 - size//8}" 
        fill="none" stroke="url(#grad1)" stroke-width="{size//20}"/>
  <path d="M{3*size//4} {size//3} L{3*size//4} {2*size//3 - size//8}" 
        fill="none" stroke="url(#grad1)" stroke-width="{size//20}"/>
  
  <!-- Audio waves (decorative) -->
  <path d="M{size//2} {size//4} Q{3*size//5} {size//3} {size//2} {2*size//5}" 
        fill="none" stroke="#28a745" stroke-width="{size//30}" opacity="0.6"/>
</svg>'''
    
    with open(f'icon-{size}.svg', 'w') as f:
        f.write(svg_content)
    
    print(f"✅ Created icon-{size}.svg")

def create_png_placeholder():
    """Create placeholder message for PNG conversion"""
    readme_content = '''# Browser Extension Icons

## SVG Icons Created
- icon-16.svg
- icon-32.svg  
- icon-48.svg
- icon-128.svg

## Converting to PNG
To convert SVG icons to PNG for the extension, you can:

### Option 1: Online Converter
1. Go to https://convertio.co/svg-png/
2. Upload each SVG file
3. Download the PNG versions

### Option 2: Command Line (if inkscape installed)
```bash
inkscape icon-16.svg -o icon-16.png
inkscape icon-32.svg -o icon-32.png
inkscape icon-48.svg -o icon-48.png
inkscape icon-128.svg -o icon-128.png
```

### Option 3: Use Chrome Extension (temporary)
For testing, Chrome will accept SVG files renamed to .png:
```bash
cp icon-16.svg icon-16.png
cp icon-32.svg icon-32.png
cp icon-48.svg icon-48.png
cp icon-128.svg icon-128.png
```

The extension is ready for testing with these placeholder icons!
'''
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    
    print("✅ Created README.md with conversion instructions")

if __name__ == "__main__":
    import os
    
    print("🎨 Creating Browser Extension Icons")
    print("=" * 40)
    
    sizes = [16, 32, 48, 128]
    
    for size in sizes:
        create_svg_icon(size, f'icon-{size}.svg')
    
    create_png_placeholder()
    
    # Create quick PNG alternatives for testing
    print(f"\n🔄 Creating PNG alternatives for testing...")
    for size in sizes:
        try:
            # Copy SVG as PNG for quick testing
            import shutil
            shutil.copy(f'icon-{size}.svg', f'icon-{size}.png')
            print(f"✅ Created icon-{size}.png (SVG copy)")
        except Exception as e:
            print(f"❌ Failed to create icon-{size}.png: {e}")
    
    print(f"\n🎉 Extension icons ready!")
    print(f"📁 Files created: 4 SVG files + 4 PNG placeholders")