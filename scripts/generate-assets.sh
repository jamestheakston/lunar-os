#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ASSETS_DIR="$PROJECT_ROOT/assets"

if ! python3 -c "from PIL import Image" 2> /dev/null; then
    echo "Error: Pillow is required (apt-get install python3-pil)"
    exit 1
fi

echo "=== Generating Lunar OS assets ==="
cd "$ASSETS_DIR/desktop"
python3 generate-wallpaper.py
python3 generate-logo.py
python3 generate-store-icon.py
python3 generate-start-orb.py
cp logo-128x128.png welcome-icon.png
cp logo-128x128.png "$ASSETS_DIR/boot/plymouth/logo.png"

python3 "$ASSETS_DIR/boot/generate-bootsplash.py"

cat > "$ASSETS_DIR/boot/plymouth/logo.svg" << 'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
  <circle cx="128" cy="128" r="100" fill="#c0c0c0"/>
  <circle cx="100" cy="110" r="15" fill="#a0a0a0"/>
  <circle cx="160" cy="135" r="20" fill="#a0a0a0"/>
  <circle cx="115" cy="175" r="12" fill="#a0a0a0"/>
  <circle cx="145" cy="85" r="8" fill="#a0a0a0"/>
</svg>
SVG

echo "=== Assets generated ==="
