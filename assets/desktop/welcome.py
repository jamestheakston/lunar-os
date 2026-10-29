#!/usr/bin/env python3
import os
import sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

MARKER = "/tmp/.lunar-welcome-dismissed"
LOGO = "/usr/share/lunar-os/welcome-icon.png"
BROWSER_CONFIG = "/home/lunar/.config/lunar-os/browser"

CSS = b"""
window.lunar-welcome { background-color: #1a1a2e; }
window.lunar-welcome label { color: #e8e8f0; }
window.lunar-welcome .heading { font-size: 24px; font-weight: bold; color: #ffffff; }
window.lunar-welcome .body { font-size: 14px; color: #c8c8d8; }
window.lunar-welcome .note { font-size: 12px; color: #9a9ab8; }
window.lunar-welcome .section-title { font-size: 16px; font-weight: bold; color: #ffffff; margin-top: 12px; }
window.lunar-welcome button.start {
    background-image: none;
    background-color: #6c5ce7;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 12px 36px;
    font-size: 15px;
    font-weight: bold;
}
window.lunar-welcome button.start:hover { background-color: #7d6ff0; }
window.lunar-welcome combobox { padding: 8px; }
"""

DESCRIPTION = (
    "\u201cYour own temporary desktop, ready to explore. Lunar OS is completely "
    "disposable: your session data, downloaded files, settings and other changes "
    "are discarded when you shut down. Every new session starts fresh.\u201d"
)

NOTES = (
    "Files you create stay available until you shut down.",
    "Disposable storage reduces persistence, but cannot remove data you copy "
    "to external drives or send over the network.",
)

BROWSERS = {
    "firefox-esr": {"name": "Firefox ESR", "command": "firefox-esr"},
    "tor-browser": {"name": "Tor Browser", "command": "torbrowser-launcher"},
}


class WelcomeWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Welcome to Lunar OS")
        self.set_default_size(520, -1)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_icon_name("lunar-os")
        self.get_style_context().add_class("lunar-welcome")
        self.connect("destroy", self.on_destroy)
        self.selected_browser = "firefox-esr"
        self.build()
        self.show_all()

    def build(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_border_width(32)
        self.add(box)

        if os.path.exists(LOGO):
            box.pack_start(Gtk.Image.new_from_file(LOGO), False, False, 0)
        else:
            moon = Gtk.Label(label="\U0001F319")
            moon.set_markup('<span size="60000">\U0001F319</span>')
            box.pack_start(moon, False, False, 0)

        heading = Gtk.Label(label="Welcome to Lunar OS")
        heading.get_style_context().add_class("heading")
        box.pack_start(heading, False, False, 0)

        body = Gtk.Label(label=DESCRIPTION)
        body.get_style_context().add_class("body")
        body.set_line_wrap(True)
        body.set_justify(Gtk.Justification.CENTER)
        body.set_max_width_chars(52)
        box.pack_start(body, False, False, 6)

        for text in NOTES:
            note = Gtk.Label(label=text)
            note.get_style_context().add_class("note")
            note.set_line_wrap(True)
            note.set_justify(Gtk.Justification.CENTER)
            note.set_max_width_chars(60)
            box.pack_start(note, False, False, 0)

        # Browser selection
        browser_label = Gtk.Label(label="Choose your browser:")
        browser_label.get_style_context().add_class("section-title")
        box.pack_start(browser_label, False, False, 0)

        browser_store = Gtk.ListStore(str, str)
        for key, info in BROWSERS.items():
            browser_store.append([key, info["name"]])

        browser_combo = Gtk.ComboBox.new_with_model(browser_store)
        renderer = Gtk.CellRendererText()
        browser_combo.pack_start(renderer, True)
        browser_combo.add_attribute(renderer, "text", 1)
        browser_combo.set_active(0)
        browser_combo.connect("changed", self.on_browser_changed)
        box.pack_start(browser_combo, False, False, 0)

        # VPN info
        vpn_label = Gtk.Label(label="Built-in VPN support (OpenVPN) is available via Network Manager")
        vpn_label.get_style_context().add_class("note")
        vpn_label.set_line_wrap(True)
        vpn_label.set_justify(Gtk.Justification.CENTER)
        vpn_label.set_max_width_chars(60)
        box.pack_start(vpn_label, False, False, 6)

        button = Gtk.Button(label="Start session")
        button.get_style_context().add_class("start")
        button.set_halign(Gtk.Align.CENTER)
        button.set_margin_top(14)
        button.connect("clicked", self.on_start)
        box.pack_start(button, False, False, 0)
        button.grab_focus()

    def on_browser_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            self.selected_browser = model[tree_iter][0]

    def on_start(self, button):
        # Save browser selection
        os.makedirs(os.path.dirname(BROWSER_CONFIG), exist_ok=True)
        with open(BROWSER_CONFIG, "w") as f:
            f.write(self.selected_browser)
        
        # Update desktop shortcut
        self.update_desktop_shortcut()
        
        self.destroy()

    def update_desktop_shortcut(self):
        desktop_dir = os.path.expanduser("~/Desktop")
        shortcut_path = os.path.join(desktop_dir, "Web Browser.desktop")
        
        browser_info = BROWSERS.get(self.selected_browser, BROWSERS["firefox-esr"])
        
        desktop_entry = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Web Browser
Comment={browser_info['name']}
Icon=web-browser
Exec={browser_info['command']}
Terminal=false
Categories=Network;WebBrowser;
"""
        
        os.makedirs(desktop_dir, exist_ok=True)
        with open(shortcut_path, "w") as f:
            f.write(desktop_entry)
        
        os.chmod(shortcut_path, 0o755)

    def on_destroy(self, _widget):
        try:
            open(MARKER, "a").close()
        except OSError:
            pass
        Gtk.main_quit()


def main():
    if os.path.exists(MARKER):
        sys.exit(0)
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    WelcomeWindow()
    Gtk.main()


if __name__ == "__main__":
    main()
