#!/usr/bin/env python3
import os
import subprocess
import threading
import tempfile
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
import sys

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import Gdk, GLib, Gtk, WebKit2

HOME = os.path.expanduser("~")
BROWSER_CONFIG = os.path.join(HOME, ".config", "lunar-os/browser")

# Generate HTML for the store
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Lunar Store</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: #6c5ce7;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        .search-bar {
            padding: 12px;
            border: none;
            border-radius: 4px;
            width: 100%;
            max-width: 400px;
            font-size: 14px;
        }
        .categories {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .category {
            padding: 10px 20px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .category:hover, .category.active {
            background: #a8d0f0;
            border-color: #6c5ce7;
        }
        .apps-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 16px;
        }
        .app-card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 16px;
            cursor: pointer;
            transition: box-shadow 0.2s;
        }
        .app-card:hover {
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .app-name {
            font-weight: bold;
            margin-bottom: 8px;
        }
        .app-desc {
            font-size: 12px;
            color: #666;
            margin-bottom: 12px;
        }
        .install-btn {
            background: #6c5ce7;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
        }
        .install-btn:hover {
            background: #7d6ff0;
        }
        .install-btn.installed {
            background: #27ae60;
            cursor: default;
        }
        .progress-container {
            margin-top: 8px;
            display: none;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: #6c5ce7;
            transition: width 0.3s;
        }
        .progress-text {
            font-size: 11px;
            color: #666;
            margin-top: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Lunar Store</h1>
            <input type="text" class="search-bar" placeholder="Search applications..." id="search">
        </div>
        <div class="categories" id="categories">
            <div class="category active" data-category="all">All</div>
            <div class="category" data-category="internet">Internet</div>
            <div class="category" data-category="multimedia">Multimedia</div>
            <div class="category" data-category="graphics">Graphics</div>
            <div class="category" data-category="office">Office</div>
            <div class="category" data-category="games">Games</div>
            <div class="category" data-category="system">System</div>
            <div class="category" data-category="accessories">Accessories</div>
        </div>
        <div class="apps-grid" id="apps-grid"></div>
    </div>
    <script>
        const apps = {APPS_JSON};
        let currentCategory = 'all';
        let installing = null;

        function renderApps() {
            const grid = document.getElementById('apps-grid');
            const search = document.getElementById('search').value.toLowerCase();
            grid.innerHTML = '';
            
            apps.forEach(app => {
                if (currentCategory !== 'all' && app.category !== currentCategory) return;
                if (search && !app.name.toLowerCase().includes(search) && !app.description.toLowerCase().includes(search)) return;
                
                const card = document.createElement('div');
                card.className = 'app-card';
                card.innerHTML = `
                    <div class="app-name">${app.name}</div>
                    <div class="app-desc">${app.description}</div>
                    <button class="install-btn" onclick="install('${app.package}', this)">Install</button>
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%"></div>
                        </div>
                        <div class="progress-text">Preparing...</div>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        function install(pkg, btn) {
            if (installing) return;
            installing = pkg;
            btn.disabled = true;
            btn.textContent = 'Installing...';
            
            const progressContainer = btn.nextElementSibling;
            const progressFill = progressContainer.querySelector('.progress-fill');
            const progressText = progressContainer.querySelector('.progress-text');
            progressContainer.style.display = 'block';
            
            fetch('/install/' + pkg).then(response => response.json()).then(data => {
                if (data.success) {
                    progressFill.style.width = '100%';
                    progressText.textContent = 'Complete!';
                    btn.textContent = 'Installed';
                    btn.classList.add('installed');
                } else {
                    progressText.textContent = 'Failed';
                    btn.disabled = false;
                    btn.textContent = 'Retry';
                }
                installing = null;
            }).catch(err => {
                progressText.textContent = 'Error';
                btn.disabled = false;
                btn.textContent = 'Retry';
                installing = null;
            });
        }

        document.getElementById('categories').addEventListener('click', (e) => {
            if (e.target.classList.contains('category')) {
                document.querySelectorAll('.category').forEach(c => c.classList.remove('active'));
                e.target.classList.add('active');
                currentCategory = e.target.dataset.category;
                renderApps();
            }
        });

        document.getElementById('search').addEventListener('input', renderApps);
        
        renderApps();
    </script>
</body>
</html>
"""

PACKAGES = [
    {"name": "Firefox ESR", "package": "firefox-esr", "category": "internet", "description": "Extended Support Release web browser"},
    {"name": "Chromium", "package": "chromium", "category": "internet", "description": "Open-source web browser"},
    {"name": "Thunderbird", "package": "thunderbird", "category": "internet", "description": "Email client"},
    {"name": "Transmission", "package": "transmission-gtk", "category": "internet", "description": "BitTorrent client"},
    {"name": "FileZilla", "package": "filezilla", "category": "internet", "description": "FTP client"},
    {"name": "VLC Media Player", "package": "vlc", "category": "multimedia", "description": "Media player"},
    {"name": "Audacity", "package": "audacity", "category": "multimedia", "description": "Audio editor"},
    {"name": "GIMP", "package": "gimp", "category": "graphics", "description": "Image editor"},
    {"name": "Inkscape", "package": "inkscape", "category": "graphics", "description": "Vector graphics editor"},
    {"name": "Blender", "package": "blender", "category": "multimedia", "description": "3D creation suite"},
    {"name": "LibreOffice", "package": "libreoffice", "category": "office", "description": "Full office suite"},
    {"name": "Evince", "package": "evince", "category": "office", "description": "PDF viewer"},
    {"name": "Steam", "package": "steam-installer", "category": "games", "description": "Steam gaming platform"},
    {"name": "Lutris", "package": "lutris", "category": "games", "description": "Open gaming platform"},
    {"name": "GParted", "package": "gparted", "category": "system", "description": "Partition editor"},
    {"name": "BleachBit", "package": "bleachbit", "category": "system", "description": "System cleaner"},
    {"name": "Htop", "package": "htop", "category": "system", "description": "Process viewer"},
    {"name": "Vim", "package": "vim", "category": "accessories", "description": "Text editor"},
    {"name": "Nano", "package": "nano", "category": "accessories", "description": "Simple text editor"},
    {"name": "Geany", "package": "geany", "category": "accessories", "description": "IDE/Text editor"},
]


class InstallHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/install/'):
            package = self.path.split('/')[2]
            success = self.install_package(package)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"success": ' + str(success).lower().encode() + b'}')
        else:
            super().do_GET()
    
    def install_package(self, package):
        try:
            subprocess.run(["sudo", "apt-get", "install", "-y", package], check=True, capture_output=True)
            return True
        except:
            return False


class LunarStore(Gtk.Window):
    def __init__(self):
        super().__init__(title="Lunar Store")
        self.set_default_size(1000, 700)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("lunar-store")
        self.connect("destroy", Gtk.main_quit)
        
        # Create web view
        self.webview = WebKit2.WebView()
        self.add(self.webview)
        
        # Start HTTP server in background
        self.start_server()
        
        # Load HTML
        GLib.timeout_add(500, self.load_html)
        
        self.show_all()
    
    def start_server(self):
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        
        # Create HTML file
        import json
        html = HTML_TEMPLATE.replace('{APPS_JSON}', json.dumps(PACKAGES))
        with open('index.html', 'w') as f:
            f.write(html)
        
        # Find available port
        self.port = 8080
        while True:
            try:
                self.server = HTTPServer(('127.0.0.1', self.port), InstallHandler)
                break
            except OSError:
                self.port += 1
        
        # Start server in thread
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
    
    def load_html(self):
        self.webview.load_uri(f"http://127.0.0.1:{self.port}/index.html")


def main():
    LunarStore()
    Gtk.main()


if __name__ == "__main__":
    main()
