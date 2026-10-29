#!/usr/bin/env python3
import os
import subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

HOME = os.path.expanduser("~")
SOUNDS_DIR = "/usr/share/sounds/lunar-os"
CURRENT_SOUNDS = os.path.join(HOME, ".config", "lunar-os", "sounds-theme")

CSS = b"""
window {
    background-color: #f5f5f5;
}
.header {
    background-color: #6c5ce7;
    color: white;
    padding: 20px;
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
.sound-item {
    padding: 12px;
    border-bottom: 1px solid #e0e0e0;
}
.sound-item:last-child {
    border-bottom: none;
}
.sound-label {
    font-size: 14px;
}
.play-button {
    background-color: #6c5ce7;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
}
.play-button:hover {
    background-color: #7d6ff0;
}
.apply-button {
    background-color: #27ae60;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 12px 24px;
    margin: 20px;
}
.apply-button:hover {
    background-color: #2ecc71;
}
"""

SOUNDS = [
    {"name": "Startup", "file": "startup.ogg"},
    {"name": "Shutdown", "file": "shutdown.ogg"},
    {"name": "Notification", "file": "notification.ogg"},
    {"name": "Error", "file": "error.ogg"},
    {"name": "Success", "file": "success.ogg"},
]


class SystemSounds(Gtk.Window):
    def __init__(self):
        super().__init__(title="System Sounds")
        self.set_default_size(500, 400)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("audio-card")
        self.connect("destroy", Gtk.main_quit)
        
        self.build()
        self.show_all()
    
    def build(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(main_box)
        
        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        header.get_style_context().add_class("header")
        
        title = Gtk.Label()
        title.set_markup('<span size="x-large" weight="bold">System Sounds</span>')
        header.pack_start(title, False, False, 0)
        
        subtitle = Gtk.Label(label="Choose system sounds for events")
        header.pack_start(subtitle, False, False, 0)
        
        main_box.pack_start(header, False, False, 0)
        
        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.get_style_context().add_class("content")
        content.set_margin(20)
        
        info = Gtk.Label(label="Click Play to preview a sound. System sounds play for various events.")
        info.set_halign(Gtk.Align.START)
        content.pack_start(info, False, False, 8)
        
        # Sound list
        for sound in SOUNDS:
            item_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
            item_box.get_style_context().add_class("sound-item")
            
            label = Gtk.Label(label=sound["name"])
            label.get_style_context().add_class("sound-label")
            item_box.pack_start(label, True, True, 0)
            
            play_button = Gtk.Button(label="Play")
            play_button.get_style_context().add_class("play-button")
            play_button.connect("clicked", lambda b, f=sound["file"]: self.play_sound(f))
            item_box.pack_start(play_button, False, False, 0)
            
            content.pack_start(item_box, False, False, 0)
        
        main_box.pack_start(content, True, True, 0)
        
        # Apply button
        apply_button = Gtk.Button(label="Enable System Sounds")
        apply_button.get_style_context().add_class("apply-button")
        apply_button.connect("clicked", self.on_enable)
        main_box.pack_start(apply_button, False, False, 0)
    
    def play_sound(self, sound_file):
        sound_path = os.path.join(SOUNDS_DIR, sound_file)
        if os.path.exists(sound_path):
            subprocess.run(["aplay", sound_path], check=False)
    
    def on_enable(self, button):
        # Enable system sounds via dunst
        os.makedirs(os.path.dirname(CURRENT_SOUNDS), exist_ok=True)
        with open(CURRENT_SOUNDS, "w") as f:
            f.write("enabled")
        
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CLOSE,
            text="System Sounds Enabled",
        )
        dialog.format_secondary_text("Sound notifications will now play for system events.")
        dialog.run()
        dialog.destroy()


def main():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    SystemSounds()
    Gtk.main()


if __name__ == "__main__":
    main()
