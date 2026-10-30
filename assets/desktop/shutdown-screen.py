#!/usr/bin/env python3
import os
import subprocess
import sys
import time

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

CSS = b"""
window.lunar-shutdown {
    background-color: #1a1a2e;
}
window.lunar-shutdown .spinner-box {
    background-color: #1a1a2e;
}
window.lunar-shutdown .spinner {
    color: #6c5ce7;
}
window.lunar-shutdown label {
    color: #e8e8f0;
    font-size: 24px;
}
window.lunar-shutdown .main-label {
    font-size: 28px;
    font-weight: bold;
    color: #ffffff;
}
window.lunar-shutdown .sub-label {
    font-size: 16px;
    color: #9a9ab8;
}
"""


class ShutdownScreen(Gtk.Window):
    def __init__(self, action):
        super().__init__(title="Lunar OS")
        self.set_default_size(400, 300)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.SPLASHSCREEN)
        self.get_style_context().add_class("lunar-shutdown")
        
        self.action = action
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_valign(Gtk.Align.CENTER)
        box.set_halign(Gtk.Align.CENTER)
        self.add(box)
        
        # Logo
        logo_label = Gtk.Label()
        logo_label.set_markup('<span size="xx-large">\U0001F319</span>')
        box.pack_start(logo_label, False, False, 0)
        
        # Spinner
        spinner = Gtk.Spinner()
        spinner.start()
        spinner.get_style_context().add_class("spinner")
        box.pack_start(spinner, False, False, 0)
        
        # Main label
        if action == "shutdown":
            main_text = "Powering Off"
        else:
            main_text = "Restarting"
        
        main_label = Gtk.Label(label=main_text)
        main_label.get_style_context().add_class("main-label")
        box.pack_start(main_label, False, False, 0)
        
        # Sub label
        sub_label = Gtk.Label(label="Please wait...")
        sub_label.get_style_context().add_class("sub-label")
        box.pack_start(sub_label, False, False, 0)
        
        self.show_all()
        
        # Execute the action after a short delay
        GLib.timeout_add(2000, self.execute_action)
    
    def execute_action(self):
        if self.action == "shutdown":
            subprocess.run(["systemctl", "poweroff"], check=False)
        else:
            subprocess.run(["systemctl", "reboot"], check=False)
        return False


def main():
    action = "shutdown"
    if len(sys.argv) > 1 and sys.argv[1] in ("shutdown", "restart"):
        action = sys.argv[1]
    
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    
    ShutdownScreen(action)
    Gtk.main()


if __name__ == "__main__":
    main()
