#!/usr/bin/env python3
"""
Generate PNG icons from SVG sources for the browser extension.
This is a fallback script in case the original PNG files aren't available.
"""

import subprocess
import os
import sys

def svg_to_png_using_system():
    """Try to convert SVG to PNG using available system tools"""
    sizes = [16, 32, 48, 128]
    
    for size in sizes:
        svg_file = f"icon-{size}.svg"
        png_file = f"icon-{size}.png"
        
        if not os.path.exists(svg_file):
            print(f"❌ {svg_file} not found")
            continue
            
        # Try different conversion methods
        methods = [
            # Method 1: rsvg-convert (if available)
            f"rsvg-convert -w {size} -h {size} {svg_file} -o {png_file}",
            # Method 2: inkscape (if available)  
            f"inkscape {svg_file} -w {size} -h {size} -o {png_file}",
            # Method 3: convert from ImageMagick (if available)
            f"convert {svg_file} -resize {size}x{size} {png_file}"
        ]
        
        success = False
        for method in methods:
            try:
                result = subprocess.run(method, shell=True, capture_output=True, text=True)
                if result.returncode == 0 and os.path.exists(png_file):
                    print(f"✅ Created {png_file} using: {method.split()[0]}")
                    success = True
                    break
            except Exception as e:
                continue
        
        if not success:
            # Fallback: copy SVG as PNG (browsers can sometimes handle this)
            try:
                with open(svg_file, 'r') as src, open(png_file, 'w') as dst:
                    dst.write(src.read())
                print(f"⚠️  Created {png_file} as SVG copy (fallback)")
            except Exception as e:
                print(f"❌ Failed to create {png_file}: {e}")

def create_simple_png_programmatically():
    """Create simple PNG files using Python PIL if available"""
    try:
        from PIL import Image, ImageDraw
        
        sizes = [16, 32, 48, 128]
        
        for size in sizes:
            # Create a new image with transparent background
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Simple headphones icon
            # Colors
            blue = (74, 144, 226, 255)
            white = (255, 255, 255, 255)
            
            # Scale factors
            pad = size // 8
            earpiece_r = size // 8
            headband_width = max(1, size // 16)
            
            # Draw headband (simplified arc)
            left_x, right_x = pad + earpiece_r, size - pad - earpiece_r
            top_y = pad
            mid_x = size // 2
            
            # Draw connecting lines (vertical lines down from headband ends)
            line_bottom = size - pad - earpiece_r * 2
            draw.line([(left_x, top_y + earpiece_r), (left_x, line_bottom)], fill=blue, width=headband_width)
            draw.line([(right_x, top_y + earpiece_r), (right_x, line_bottom)], fill=blue, width=headband_width)
            
            # Draw headband (horizontal line at top)
            draw.line([(left_x, top_y + earpiece_r), (right_x, top_y + earpiece_r)], fill=blue, width=headband_width)
            
            # Draw earpieces
            left_ear_y = size - pad - earpiece_r
            right_ear_y = left_ear_y
            
            # Outer earpiece circles
            draw.ellipse([left_x - earpiece_r, left_ear_y - earpiece_r, 
                         left_x + earpiece_r, left_ear_y + earpiece_r], fill=blue)
            draw.ellipse([right_x - earpiece_r, right_ear_y - earpiece_r,
                         right_x + earpiece_r, right_ear_y + earpiece_r], fill=blue)
            
            # Inner earpiece circles (white)
            inner_r = earpiece_r * 2 // 3
            draw.ellipse([left_x - inner_r, left_ear_y - inner_r,
                         left_x + inner_r, left_ear_y + inner_r], fill=white)
            draw.ellipse([right_x - inner_r, right_ear_y - inner_r,
                         right_x + inner_r, right_ear_y + inner_r], fill=white)
            
            # Save the image
            png_file = f"icon-{size}.png"
            img.save(png_file, "PNG")
            print(f"✅ Created {png_file} using PIL")
            
    except ImportError:
        print("❌ PIL (Python Imaging Library) not available")
        return False
    except Exception as e:
        print(f"❌ Failed to create PNG files with PIL: {e}")
        return False
    
    return True

def main():
    print("🎨 Converting SVG icons to PNG format")
    print("=" * 40)
    
    # First try system conversion tools
    print("Trying system conversion tools...")
    svg_to_png_using_system()
    
    # Check if we have all PNG files
    sizes = [16, 32, 48, 128]
    missing_pngs = [size for size in sizes if not os.path.exists(f"icon-{size}.png")]
    
    if missing_pngs:
        print(f"\n🔄 Missing PNG files for sizes: {missing_pngs}")
        print("Trying programmatic generation...")
        if not create_simple_png_programmatically():
            print("\n⚠️  PNG conversion failed. Extension will use SVG fallbacks.")
            print("For best results, manually convert SVG files to PNG using:")
            print("  - Online converter: https://convertio.co/svg-png/")
            print("  - Or install: brew install librsvg (for rsvg-convert)")
    
    print(f"\n🎉 Icon generation complete!")
    
    # List what we have
    for size in sizes:
        png_file = f"icon-{size}.png"
        if os.path.exists(png_file):
            file_size = os.path.getsize(png_file)
            print(f"✅ {png_file} ({file_size} bytes)")
        else:
            print(f"❌ {png_file} missing")

if __name__ == "__main__":
    main()