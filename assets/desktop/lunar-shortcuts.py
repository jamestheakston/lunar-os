#!/usr/bin/env python3
import subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

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
.category {
    background-color: #e8e8ff;
    border-radius: 6px;
    padding: 12px;
    margin: 8px;
}
.category label {
    font-weight: bold;
    color: #000000;
}
.shortcut-item {
    padding: 8px 12px;
    border-bottom: 1px solid #e0e0e0;
}
.shortcut-item:last-child {
    border-bottom: none;
}
.shortcut-key {
    color: #6c5ce7;
    font-weight: bold;
    font-family: monospace;
}
.shortcut-desc {
    color: #333;
}
"""

SHORTCUTS = {
    "System": [
        {"key": "Super+Q", "desc": "Open shutdown dialog"},
        {"key": "Super+I", "desc": "Open Lunar Settings"},
        {"key": "Super+T", "desc": "Open terminal"},
        {"key": "Super+B", "desc": "Open private browser window"},
        {"key": "Super+C", "desc": "Open calculator"},
        {"key": "Super+D", "desc": "Show desktop"},
        {"key": "Alt+F4", "desc": "Close window"},
        {"key": "Alt+Tab", "desc": "Switch between windows"},
        {"key": "Super+Tab", "desc": "Switch windows (all workspaces)"},
    ],
    "Window Management": [
        {"key": "Super+Up", "desc": "Maximize window"},
        {"key": "Super+Down", "desc": "Minimize window"},
        {"key": "Super+Left/Right", "desc": "Tile windows"},
        {"key": "Super+Shift+Left/Right", "desc": "Move window"},
        {"key": "F11", "desc": "Toggle fullscreen"},
    ],
    "File Manager": [
        {"key": "Ctrl+N", "desc": "New window"},
        {"key": "Ctrl+T", "desc": "New tab"},
        {"key": "Ctrl+W", "desc": "Close tab"},
        {"key": "Ctrl+L", "desc": "Location bar"},
        {"key": "Ctrl+H", "desc": "Toggle hidden files"},
        {"key": "Delete", "desc": "Move to trash"},
        {"key": "Shift+Delete", "desc": "Delete permanently"},
    ],
    "Terminal": [
        {"key": "Ctrl+Shift+T", "desc": "New terminal"},
        {"key": "Ctrl+Shift+C", "desc": "Copy"},
        {"key": "Ctrl+Shift+V", "desc": "Paste"},
        {"key": "Ctrl+Shift+N", "desc": "New tab"},
        {"key": "Ctrl+Shift+W", "desc": "Close tab"},
        {"key": "Ctrl+Shift+PageUp", "desc": "Previous tab"},
        {"key": "Ctrl+Shift+PageDown", "desc": "Next tab"},
    ],
}


class KeyboardShortcuts(Gtk.Window):
    def __init__(self):
        super().__init__(title="Keyboard Shortcuts")
        self.set_default_size(700, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("input-keyboard")
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
        title.set_markup('<span size="x-large" weight="bold">Keyboard Shortcuts</span>')
        header.pack_start(title, False, False, 0)
        
        subtitle = Gtk.Label(label="Learn the keyboard shortcuts for Lunar OS")
        header.pack_start(subtitle, False, False, 0)
        
        main_box.pack_start(header, False, False, 0)
        
        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.get_style_context().add_class("content")
        content.set_margin(20)
        
        for category, shortcuts in SHORTCUTS.items():
            # Category header
            cat_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            cat_box.get_style_context().add_class("category")
            
            cat_label = Gtk.Label(label=category)
            cat_box.pack_start(cat_label, False, False, 0)
            
            content.pack_start(cat_box, False, False, 0)
            
            # Shortcuts list
            for sc in shortcuts:
                item_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
                item_box.get_style_context().add_class("shortcut-item")
                
                key_label = Gtk.Label(label=sc["key"])
                key_label.get_style_context().add_class("shortcut-key")
                key_label.set_width_chars(20)
                item_box.pack_start(key_label, False, False, 0)
                
                desc_label = Gtk.Label(label=sc["desc"])
                desc_label.get_style_context().add_class("shortcut-desc")
                item_box.pack_start(desc_label, True, True, 0)
                
                content.pack_start(item_box, False, False, 0)
        
        main_box.pack_start(content, True, True, 0)


def main():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    KeyboardShortcuts()
    Gtk.main()


if __name__ == "__main__":
    main()
