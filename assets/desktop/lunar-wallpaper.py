#!/usr/bin/env python3
import os
import subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

HOME = os.path.expanduser("~")
WALLPAPER_DIR = "/usr/share/backgrounds/lunar-os"
CURRENT_WALLPAPER = os.path.join(HOME, ".config", "lunar-os", "wallpaper")

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
.gallery {
    background-color: #ffffff;
    border-radius: 8px;
    margin: 20px;
}
.wallpaper-item {
    margin: 12px;
    border: 2px solid transparent;
    border-radius: 8px;
    cursor: pointer;
    transition: border-color 0.2s;
}
.wallpaper-item:hover {
    border-color: #6c5ce7;
}
.wallpaper-item.selected {
    border-color: #27ae60;
}
.wallpaper-preview {
    border-radius: 6px;
}
.wallpaper-name {
    padding: 8px;
    text-align: center;
    font-size: 12px;
}
.apply-button {
    background-color: #6c5ce7;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 12px 24px;
    margin: 20px;
}
.apply-button:hover {
    background-color: #7d6ff0;
}
"""

WALLPAPERS = [
    {"name": "Lunar Dark", "file": "wallpaper.png"},
    {"name": "Lunar Light", "file": "wallpaper-light.png"},
    {"name": "Moon Phase", "file": "wallpaper-moon.png"},
    {"name": "Nebula", "file": "wallpaper-nebula.png"},
    {"name": "Starry Night", "file": "wallpaper-stars.png"},
]


class WallpaperGallery(Gtk.Window):
    def __init__(self):
        super().__init__(title="Wallpaper Gallery")
        self.set_default_size(700, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("preferences-desktop-wallpaper")
        self.connect("destroy", Gtk.main_quit)
        
        self.selected_wallpaper = None
        self.load_current_wallpaper()
        
        self.build()
        self.show_all()
    
    def load_current_wallpaper(self):
        if os.path.exists(CURRENT_WALLPAPER):
            with open(CURRENT_WALLPAPER, "r") as f:
                self.selected_wallpaper = f.read().strip()
    
    def build(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(main_box)
        
        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        header.get_style_context().add_class("header")
        
        title = Gtk.Label()
        title.set_markup('<span size="x-large" weight="bold">Wallpaper Gallery</span>')
        header.pack_start(title, False, False, 0)
        
        subtitle = Gtk.Label(label="Choose a wallpaper to customize your desktop")
        header.pack_start(subtitle, False, False, 0)
        
        main_box.pack_start(header, False, False, 0)
        
        # Gallery
        gallery = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        gallery.get_style_context().add_class("gallery")
        
        # Check available wallpapers
        available = []
        for wp in WALLPAPERS:
            if os.path.exists(os.path.join(WALLPAPER_DIR, wp["file"])):
                available.append(wp)
        
        if not available:
            label = Gtk.Label(label="No wallpapers found")
            gallery.pack_start(label, True, True, 20)
            main_box.pack_start(gallery, True, True, 0)
            return
        
        # Grid
        grid = Gtk.Grid()
        grid.set_column_spacing(16)
        grid.set_row_spacing(16)
        grid.set_margin(16)
        
        col = 0
        row = 0
        for wp in available:
            item_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            item_box.get_style_context().add_class("wallpaper-item")
            
            if self.selected_wallpaper == wp["file"]:
                item_box.get_style_context().add_class("selected")
            
            # Preview
            preview = Gtk.Image()
            pixbuf = Gdk.Pixbuf.new_from_file_at_scale(
                os.path.join(WALLPAPER_DIR, wp["file"]),
                200, 120, True
            )
            preview.set_from_pixbuf(pixbuf)
            preview.get_style_context().add_class("wallpaper-preview")
            item_box.pack_start(preview, False, False, 0)
            
            # Name
            name = Gtk.Label(label=wp["name"])
            name.get_style_context().add_class("wallpaper-name")
            item_box.pack_start(name, False, False, 0)
            
            item_box.connect("button-press-event", lambda w, e, f=wp["file"]: self.on_select(f))
            
            grid.attach(item_box, col, row, 1, 1)
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        gallery.pack_start(grid, True, True, 0)
        main_box.pack_start(gallery, True, True, 0)
        
        # Apply button
        apply_button = Gtk.Button(label="Apply Selected Wallpaper")
        apply_button.get_style_context().add_class("apply-button")
        apply_button.connect("clicked", self.on_apply)
        apply_button.set_sensitive(self.selected_wallpaper is not None)
        main_box.pack_start(apply_button, False, False, 0)
    
    def on_select(self, wallpaper_file):
        self.selected_wallpaper = wallpaper_file
        self.update_ui()
    
    def update_ui(self):
        for child in self.get_children():
            self.remove(child)
        self.build()
    
    def on_apply(self, button):
        if self.selected_wallpaper:
            # Save selection
            os.makedirs(os.path.dirname(CURRENT_WALLPAPER), exist_ok=True)
            with open(CURRENT_WALLPAPER, "w") as f:
                f.write(self.selected_wallpaper)
            
            # Apply wallpaper
            subprocess.run([
                "pcmanfm",
                "--set-wallpaper=" + os.path.join(WALLPAPER_DIR, self.selected_wallpaper),
                "--wallpaper-mode=crop"
            ], check=False)
            
            dialog = Gtk.MessageDialog(
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.CLOSE,
                text="Wallpaper Applied",
            )
            dialog.format_secondary_text("Your wallpaper has been changed.")
            dialog.run()
            dialog.destroy()


def main():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    WallpaperGallery()
    Gtk.main()


if __name__ == "__main__":
    main()
