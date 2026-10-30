#!/usr/bin/env python3
import json
import os
import subprocess
import tempfile
from datetime import datetime

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

CURRENT_YEAR = datetime.now().year
AUTHOR = "James Theakston"
REPO = "jamestheakston/lunar-os"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"
DOWNLOAD_DIR = os.path.expanduser("~/Downloads")

CSS = b"""
window {
    background-color: #f5f5f5;
}
.header {
    background-color: #6c5ce7;
    color: white;
    padding: 24px;
}
.header label {
    color: white;
}
.content {
    background-color: #ffffff;
    border-radius: 8px;
    margin: 20px;
}
.content label {
    color: #000000;
}
.version-box {
    background-color: #e8f4ff;
    border-radius: 8px;
    padding: 16px;
    margin: 16px;
}
.check-button {
    background-color: #6c5ce7;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 12px 24px;
    margin: 16px;
}
.check-button:hover {
    background-color: #7d6ff0;
}
.download-button {
    background-color: #27ae60;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 12px 24px;
    margin: 16px;
}
.download-button:hover {
    background-color: #2ecc71;
}
.update-available {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 8px;
    padding: 16px;
    margin: 16px;
}
.update-available label {
    color: #155724;
}
.up-to-date {
    background-color: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 8px;
    padding: 16px;
    margin: 16px;
}
.up-to-date label {
    color: #856404;
}
.progress-bar {
    margin: 16px;
}
"""


class LunarUpdater(Gtk.Window):
    def __init__(self):
        super().__init__(title="Lunar OS Updater")
        self.set_default_size(600, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("system-software-update")
        self.connect("destroy", Gtk.main_quit)
        
        self.current_version = self.get_current_version()
        self.latest_version = None
        self.download_url = None
        self.iso_path = None
        self.checking = False
        self.downloading = False
        
        self.build()
        self.show_all()
    
    def get_current_version(self):
        try:
            result = subprocess.run(
                ["git", "-C", "/usr/share/lunar-os", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "1.0.0"
    
    def build(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(main_box)
        
        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        header.get_style_context().add_class("header")
        
        title = Gtk.Label()
        title.set_markup('<span size="x-large" weight="bold">Lunar OS Updater</span>')
        header.pack_start(title, False, False, 0)
        
        subtitle = Gtk.Label(label="Download and install updates from GitHub")
        header.pack_start(subtitle, False, False, 0)
        
        main_box.pack_start(header, False, False, 0)
        
        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.get_style_context().add_class("content")
        content.set_margin(20)
        
        # Current version
        version_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        version_box.get_style_context().add_class("version-box")
        
        current_label = Gtk.Label(label=f"Current Version: {self.current_version}")
        current_label.get_style_context().add_class("info-label")
        version_box.pack_start(current_label, False, False, 0)
        
        content.pack_start(version_box, False, False, 0)
        
        # Status box
        self.status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content.pack_start(self.status_box, False, False, 0)
        
        # Check button
        self.check_button = Gtk.Button(label="Check for Updates")
        self.check_button.get_style_context().add_class("check-button")
        self.check_button.connect("clicked", self.on_check_updates)
        content.pack_start(self.check_button, False, False, 0)
        
        main_box.pack_start(content, True, True, 0)
    
    def on_check_updates(self, button):
        if self.checking or self.downloading:
            return
        
        self.checking = True
        button.set_sensitive(False)
        button.set_label("Checking...")
        
        # Check in background
        import threading
        threading.Thread(target=self.check_github, daemon=True).start()
    
    def check_github(self):
        try:
            result = subprocess.run(
                ["curl", "-s", API_URL],
                capture_output=True,
                text=True,
                check=True
            )
            data = json.loads(result.stdout)
            self.latest_version = data.get("tag_name", "unknown")
            self.release_notes = data.get("body", "No release notes available.")
            
            # Find ISO download URL
            assets = data.get("assets", [])
            for asset in assets:
                if asset.get("name", "").endswith(".iso"):
                    self.download_url = asset.get("browser_download_url")
                    self.iso_name = asset.get("name")
                    break
            
            GLib.idle_add(self.show_results)
        except Exception as e:
            GLib.idle_add(self.show_error, str(e))
    
    def show_results(self):
        self.checking = False
        self.check_button.set_sensitive(True)
        self.check_button.set_label("Check for Updates")
        
        # Clear status box
        for child in self.status_box.get_children():
            self.status_box.remove(child)
        
        if self.latest_version and self.latest_version != self.current_version:
            # Update available
            update_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            update_box.get_style_context().add_class("update-available")
            
            update_label = Gtk.Label()
            update_label.set_markup(f'<span weight="bold">Update Available!</span>')
            update_box.pack_start(update_label, False, False, 0)
            
            version_label = Gtk.Label(label=f"Latest Version: {self.latest_version}")
            update_box.pack_start(version_label, False, False, 0)
            
            if self.download_url:
                info_label = Gtk.Label(label=f"ISO: {self.iso_name}")
                update_box.pack_start(info_label, False, False, 0)
                
                # Download button
                self.download_button = Gtk.Button(label="Download Update")
                self.download_button.get_style_context().add_class("download-button")
                self.download_button.connect("clicked", self.on_download)
                update_box.pack_start(self.download_button, False, False, 0)
            else:
                no_iso_label = Gtk.Label(label="No ISO found in release assets")
                update_box.pack_start(no_iso_label, False, False, 0)
            
            # Release notes
            notes_label = Gtk.Label(label="Release Notes:")
            notes_label.set_halign(Gtk.Align.START)
            update_box.pack_start(notes_label, False, False, 0)
            
            notes_text = Gtk.TextView()
            notes_text.set_editable(False)
            notes_text.set_wrap_mode(Gtk.WrapMode.WORD)
            buffer = notes_text.get_buffer()
            buffer.set_text(self.release_notes)
            
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scrolled.set_min_content_height(150)
            scrolled.add(notes_text)
            update_box.pack_start(scrolled, True, True, 0)
            
            self.status_box.pack_start(update_box, True, True, 0)
        else:
            # Up to date
            up_to_date_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            up_to_date_box.get_style_context().add_class("up-to-date")
            
            label = Gtk.Label()
            label.set_markup('<span weight="bold">You are up to date!</span>')
            up_to_date_box.pack_start(label, False, False, 0)
            
            if self.latest_version:
                version_label = Gtk.Label(label=f"Latest Version: {self.latest_version}")
                up_to_date_box.pack_start(version_label, False, False, 0)
            
            self.status_box.pack_start(up_to_date_box, True, True, 0)
        
        self.status_box.show_all()
    
    def show_error(self, error_message):
        self.checking = False
        self.check_button.set_sensitive(True)
        self.check_button.set_label("Check for Updates")
        
        # Clear status box
        for child in self.status_box.get_children():
            self.status_box.remove(child)
        
        error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        error_box.get_style_context().add_class("up-to-date")
        
        label = Gtk.Label()
        label.set_markup(f'<span weight="bold">Error checking for updates</span>')
        error_box.pack_start(label, False, False, 0)
        
        error_label = Gtk.Label(label=error_message)
        error_label.set_line_wrap(True)
        error_box.pack_start(error_label, False, False, 0)
        
        self.status_box.pack_start(error_box, True, True, 0)
        self.status_box.show_all()
    
    def on_download(self, button):
        if not self.download_url or self.downloading:
            return
        
        self.downloading = True
        button.set_sensitive(False)
        button.set_label("Downloading...")
        
        # Clear status box and show progress
        for child in self.status_box.get_children():
            self.status_box.remove(child)
        
        progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        progress_box.get_style_context().add_class("update-available")
        
        info_label = Gtk.Label(label=f"Downloading {self.iso_name}...")
        progress_box.pack_start(info_label, False, False, 0)
        
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Starting download...")
        self.progress_bar.get_style_context().add_class("progress-bar")
        progress_box.pack_start(self.progress_bar, False, False, 0)
        
        self.status_box.pack_start(progress_box, True, True, 0)
        self.status_box.show_all()
        
        # Download in background
        import threading
        threading.Thread(target=self.download_iso, daemon=True).start()
    
    def download_iso(self):
        try:
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            self.iso_path = os.path.join(DOWNLOAD_DIR, self.iso_name)
            
            # Use curl to download with progress
            process = subprocess.Popen(
                ["curl", "-L", "-o", self.iso_path, self.download_url],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            for line in process.stdout:
                # Update progress
                GLib.idle_add(lambda: self.progress_bar.pulse())
            
            process.wait()
            
            if process.returncode == 0:
                GLib.idle_add(self.download_complete)
            else:
                GLib.idle_add(self.show_error, "Download failed")
        except Exception as e:
            GLib.idle_add(self.show_error, str(e))
    
    def download_complete(self):
        self.downloading = False
        
        # Clear status box
        for child in self.status_box.get_children():
            self.status_box.remove(child)
        
        complete_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        complete_box.get_style_context().add_class("update-available")
        
        label = Gtk.Label()
        label.set_markup('<span weight="bold">Download Complete!</span>')
        complete_box.pack_start(label, False, False, 0)
        
        path_label = Gtk.Label(label=f"ISO saved to: {self.iso_path}")
        path_label.set_line_wrap(True)
        complete_box.pack_start(path_label, False, False, 0)
        
        info_label = Gtk.Label(label="To install the update:")
        info_label.set_halign(Gtk.Align.START)
        complete_box.pack_start(info_label, False, False, 0)
        
        instructions = Gtk.Label(
            "1. Write the ISO to a USB drive using a tool like BalenaEtcher or dd\n"
            "2. Boot from the USB drive\n"
            "3. Your data will be preserved if you use the same USB device"
        )
        instructions.set_halign(Gtk.Align.START)
        instructions.set_xalign(0)
        instructions.set_line_wrap(True)
        complete_box.pack_start(instructions, False, False, 0)
        
        # Open folder button
        open_button = Gtk.Button(label="Open Downloads Folder")
        open_button.get_style_context().add_class("check-button")
        open_button.connect("clicked", self.on_open_folder)
        complete_box.pack_start(open_button, False, False, 0)
        
        self.status_box.pack_start(complete_box, True, True, 0)
        self.status_box.show_all()
    
    def on_open_folder(self, button):
        subprocess.run(["pcmanfm", DOWNLOAD_DIR], check=False)


def main():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    LunarUpdater()
    Gtk.main()


if __name__ == "__main__":
    main()
