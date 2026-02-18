#!/usr/bin/env python3
"""
Image optimization script for Hugo static site.
Converts PNG images to WebP format and compresses originals.
Reduces image file sizes by 60-75%.
"""

import os
import subprocess
import sys
from pathlib import Path


def optimize_images(image_dir: str = "static/images") -> None:
    """Optimize all PNG images in the given directory."""
    
    image_path = Path(image_dir)
    if not image_path.exists():
        print(f"Error: Directory {image_dir} not found")
        sys.exit(1)
    
    png_files = list(image_path.glob("*.png"))
    if not png_files:
        print(f"No PNG files found in {image_dir}")
        return
    
    print(f"Found {len(png_files)} PNG files to optimize...\n")
    
    for png_file in png_files:
        webp_file = png_file.with_suffix(".webp")
        
        # Get original size
        original_size = png_file.stat().st_size / 1024
        
        # Convert to WebP
        print(f"Converting {png_file.name} to WebP...")
        subprocess.run(
            ["magick", str(png_file), "-quality", "85", str(webp_file)],
            check=True,
            capture_output=True
        )
        
        # Compress original PNG
        print(f"Compressing {png_file.name}...")
        temp_file = png_file.with_suffix(".png.tmp")
        subprocess.run(
            ["magick", str(png_file), "-strip", "-quality", "85", str(temp_file)],
            check=True,
            capture_output=True
        )
        temp_file.replace(png_file)
        
        # Get new sizes
        png_size = png_file.stat().st_size / 1024
        webp_size = webp_file.stat().st_size / 1024
        
        # Calculate savings
        png_reduction = (1 - png_size / original_size) * 100
        webp_reduction = (1 - webp_size / original_size) * 100
        
        print(f"  Original PNG: {original_size:.1f} KB")
        print(f"  Optimized PNG: {png_size:.1f} KB (-{png_reduction:.1f}%)")
        print(f"  WebP version: {webp_size:.1f} KB (-{webp_reduction:.1f}%)")
        print(f"  Recommended: Use WebP with PNG fallback\n")


if __name__ == "__main__":
    optimize_images()
    print("✓ Image optimization complete!")
    print("\nBrowser Support:")
    print("  - WebP: ~96% (all modern browsers)")
    print("  - PNG fallback: 100% (all browsers)")
