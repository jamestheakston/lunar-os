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
        
        # Check available space
        space_info = self.get_disk_space()
        space_label = Gtk.Label(label=f"Available space: {space_info}")
        space_label.set_line_wrap(True)
        complete_box.pack_start(space_label, False, False, 0)
        
        # Warning about persistence
        warning_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        warning_box.get_style_context().add_class("up-to-date")
        
        warning_title = Gtk.Label()
        warning_title.set_markup('<span weight="bold">Update Process:</span>')
        warning_box.pack_start(warning_title, False, False, 0)
        
        step1 = Gtk.Label(label="1. Enable persistence storage temporarily")
        step1.set_halign(Gtk.Align.START)
        warning_box.pack_start(step1, False, False, 0)
        
        step2 = Gtk.Label(label="2. Download and install system updates")
        step2.set_halign(Gtk.Align.START)
        warning_box.pack_start(step2, False, False, 0)
        
        step3 = Gtk.Label(label="3. Disable persistence and revert to disposable mode")
        step3.set_halign(Gtk.Align.START)
        warning_box.pack_start(step3, False, False, 0)
        
        storage_warning = Gtk.Label(label="⚠️ Requires approximately 2-4 GB of free space for updates")
        storage_warning.set_line_wrap(True)
        warning_box.pack_start(storage_warning, False, False, 0)
        
        complete_box.pack_start(warning_box, False, False, 0)
        
        # Install button
        self.install_button = Gtk.Button(label="Start Update Process")
        self.install_button.get_style_context().add_class("download-button")
        self.install_button.connect("clicked", self.on_start_update)
        complete_box.pack_start(self.install_button, False, False, 0)
        
        self.status_box.pack_start(complete_box, True, True, 0)
        self.status_box.show_all()
    
    def get_disk_space(self):
        try:
            result = subprocess.run(
                ["df", "-h", "/"],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.split("\n")
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 4:
                    return f"{parts[3]} available on /"
        except:
            pass
        return "Unknown"
    
    def on_start_update(self, button):
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Start Update Process",
        )
        dialog.format_secondary_text(
            "This will:\n"
            "• Enable persistence storage temporarily\n"
            "• Download and install system updates\n"
            "• Disable persistence and revert to disposable mode\n\n"
            "The update will require 2-4 GB of free space.\n"
            "This process may take 10-30 minutes depending on your internet speed.\n\n"
            "Continue?"
        )
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            self.run_update_process()
    
    def run_update_process(self):
        self.installing = True
        
        # Show progress
        for child in self.status_box.get_children():
            self.status_box.remove(child)
        
        progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        progress_box.get_style_context().add_class("update-available")
        
        self.progress_label = Gtk.Label(label="Starting update process...")
        progress_box.pack_start(self.progress_label, False, False, 0)
        
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Initializing...")
        self.progress_bar.get_style_context().add_class("progress-bar")
        progress_box.pack_start(self.progress_bar, False, False, 0)
        
        self.status_box.pack_start(progress_box, True, True, 0)
        self.status_box.show_all()
        
        # Run update in background
        import threading
        threading.Thread(target=self.execute_update, daemon=True).start()
    
    def execute_update(self):
        try:
            # Step 1: Create persistence file
            GLib.idle_add(lambda: self.progress_label.set_text("Creating persistence storage..."))
            GLib.idle_add(lambda: self.progress_bar.set_text("Creating 4GB persistence file..."))
            GLib.idle_add(lambda: self.progress_bar.set_fraction(0.1))
            
            persistence_file = "/tmp/lunar-persistence"
            subprocess.run(
                ["sudo", "dd", "if=/dev/zero", f"of={persistence_file}", "bs=1M", "count=4096", "status=progress"],
                capture_output=True,
                check=True
            )
            
            # Format as ext4
            GLib.idle_add(lambda: self.progress_label.set_text("Formatting persistence storage..."))
            GLib.idle_add(lambda: self.progress_bar.set_text("Formatting as ext4..."))
            GLib.idle_add(lambda: self.progress_bar.set_fraction(0.2))
            
            subprocess.run(
                ["sudo", "mkfs.ext4", "-F", persistence_file],
                capture_output=True,
                check=True
            )
            
            # Mount persistence
            GLib.idle_add(lambda: self.progress_label.set_text("Mounting persistence storage..."))
            GLib.idle_add(lambda: self.progress_bar.set_text("Mounting overlay..."))
            GLib.idle_add(lambda: self.progress_bar.set_fraction(0.3))
            
            persistence_mount = "/tmp/lunar-persistence-mount"
            os.makedirs(persistence_mount, exist_ok=True)
            subprocess.run(
                ["sudo", "mount", "-o", "loop", persistence_file, persistence_mount],
                check=True
            )
            
            # Step 2: Update system
            GLib.idle_add(lambda: self.progress_label.set_text("Updating system packages..."))
            GLib.idle_add(lambda: self.progress_bar.set_text("Running apt-get update..."))
            GLib.idle_add(lambda: self.progress_bar.set_fraction(0.4))
            
            subprocess.run(
                ["sudo", "apt-get", "update"],
                capture_output=True,
                check=True
            )
            
            GLib.idle_add(lambda: self.progress_label.set_text("Running apt-get upgrade..."))
            GLib.idle_add(lambda: self.progress_bar.set_text("Installing updates..."))
            GLib.idle_add(lambda: self.progress_bar.set_fraction(0.5))
            
            subprocess.run(
                ["sudo", "apt-get", "upgrade", "-y"],
                capture_output=True,
                check=True
            )
            
            # Step 3: Disable persistence
            GLib.idle_add(lambda: self.progress_label.set_text("Cleaning up..."))
            GLib.idle_add(lambda: self.progress_bar.set_text("Unmounting persistence..."))
            GLib.idle_add(lambda: self.progress_bar.set_fraction(0.8))
            
            subprocess.run(
                ["sudo", "umount", persistence_mount],
                check=True
            )
            
            GLib.idle_add(lambda: self.progress_label.set_text("Removing persistence file..."))
            GLib.idle_add(lambda: self.progress_bar.set_fraction(0.9))
            
            subprocess.run(
                ["sudo", "rm", "-f", persistence_file],
                check=True
            )
            
            GLib.idle_add(self.update_complete)
            
        except Exception as e:
            GLib.idle_add(lambda: self.show_error, f"Update failed: {str(e)}")
            # Cleanup on error
            try:
                subprocess.run(["sudo", "umount", "/tmp/lunar-persistence-mount"], check=False)
                subprocess.run(["sudo", "rm", "-f", "/tmp/lunar-persistence"], check=False)
            except:
                pass
    
    def update_complete(self):
        self.installing = False
        
        # Clear status box
        for child in self.status_box.get_children():
            self.status_box.remove(child)
        
        complete_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        complete_box.get_style_context().add_class("update-available")
        
        label = Gtk.Label()
        label.set_markup('<span weight="bold">Update Complete!</span>')
        complete_box.pack_start(label, False, False, 0)
        
        success_label = Gtk.Label(label="System has been updated successfully.")
        success_label.set_line_wrap(True)
        complete_box.pack_start(success_label, False, False, 0)
        
        info_label = Gtk.Label(label="Persistence has been disabled. Your system is back in disposable mode.")
        info_label.set_line_wrap(True)
        complete_box.pack_start(info_label, False, False, 0)
        
        reboot_label = Gtk.Label(label="You may want to reboot to apply all changes.")
        reboot_label.set_line_wrap(True)
        complete_box.pack_start(reboot_label, False, False, 0)
        
        # Reboot button
        reboot_button = Gtk.Button(label="Reboot Now")
        reboot_button.get_style_context().add_class("download-button")
        reboot_button.connect("clicked", self.on_reboot)
        complete_box.pack_start(reboot_button, False, False, 0)
        
        self.status_box.pack_start(complete_box, True, True, 0)
        self.status_box.show_all()
    
    
    def on_reboot(self, button):
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Reboot System",
        )
        dialog.format_secondary_text("Are you sure you want to reboot? Make sure to save any unsaved work.")
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            subprocess.run(["sudo", "reboot"], check=False)


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
