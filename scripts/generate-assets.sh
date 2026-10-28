#!/bin/bash
# Generate Lunar OS visual assets

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ASSETS_DIR="$PROJECT_ROOT/assets"

echo "=== Generating Lunar OS Visual Assets ==="

# Check if Python 3 and PIL are available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found"
    exit 1
fi

# Check for PIL/Pillow
if ! python3 -c "from PIL import Image" 2>/dev/null; then
    echo "Installing Pillow (PIL)..."
    pip3 install Pillow --user
fi

# Generate wallpaper
echo "Generating wallpaper..."
cd "$ASSETS_DIR/desktop"
python3 generate-wallpaper.py

# Generate logos
echo "Generating logos..."
python3 generate-logo.py

# Copy logo to welcome icon
if [ -f "logo-128x128.png" ]; then
    cp logo-128x128.png welcome-icon.png
    echo "Welcome icon created"
fi

# Create a simple SVG logo for Plymouth (fallback)
echo "Creating SVG logo..."
cat > "$ASSETS_DIR/boot/plymouth/logo.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
  <circle cx="128" cy="128" r="100" fill="#c0c0c0"/>
  <circle cx="100" cy="110" r="15" fill="#a0a0a0"/>
  <circle cx="160" cy="135" r="20" fill="#a0a0a0"/>
  <circle cx="115" cy="175" r="12" fill="#a0a0a0"/>
  <circle cx="145" cy="85" r="8" fill="#a0a0a0"/>
</svg>
EOF

echo ""
echo "=== Assets generated successfully ==="
echo "Generated files:"
ls -lh "$ASSETS_DIR/desktop"/*.png 2>/dev/null || true
ls -lh "$ASSETS_DIR/boot/plymouth"/*.svg 2>/dev/null || true
