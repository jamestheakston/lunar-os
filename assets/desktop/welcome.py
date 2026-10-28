#!/usr/bin/env python3
"""
Lunar OS Welcome Window
Shows automatically on every boot to introduce the disposable session concept
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import os

class LunarWelcomeWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Welcome to Lunar OS")
        
        # Set window properties
        self.set_default_size(500, 400)
        self.set_border_width(20)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_modal(True)
        
        # Set window type hint to make it a dialog
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        
        # Make it stay on top
        self.set_keep_above(True)
        
        # Setup UI
        self.setup_ui()
        
        # Connect signals
        self.connect("destroy", Gtk.main_quit)
        
        # Show all
        self.show_all()

    def setup_ui(self):
        """Setup the welcome window UI"""
        # Main vertical box
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.add(vbox)
        
        # Logo area
        logo_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.pack_start(logo_box, False, False, 10)
        
        # Try to load logo image
        logo_path = "/usr/share/lunar-os/welcome-icon.png"
        if os.path.exists(logo_path):
            try:
                logo = Gtk.Image()
                logo.set_from_file(logo_path)
                logo_box.pack_start(logo, False, False, 0)
            except:
                # If image fails, show text logo
                logo_label = Gtk.Label()
                logo_label.set_markup('<span size="xx-large">🌙</span>')
                logo_box.pack_start(logo_label, False, False, 0)
        else:
            # Fallback to emoji
            logo_label = Gtk.Label()
            logo_label.set_markup('<span size="xx-large">🌙</span>')
            logo_box.pack_start(logo_label, False, False, 0)
        
        # Title
        title_label = Gtk.Label()
        title_label.set_markup('<span size="x-large" weight="bold">Welcome to Lunar OS</span>')
        title_label.set_margin_top(10)
        logo_box.pack_start(title_label, False, False, 0)
        
        # Description
        description = (
            '"Your own temporary desktop, ready to explore. '
            'Lunar OS is completely disposable: your session data, '
            'downloaded files, settings and other changes are discarded '
            'when you shut down. Every new session starts fresh."'
        )
        
        desc_label = Gtk.Label()
        desc_label.set_markup(f'<span size="small" style="italic">{description}</span>')
        desc_label.set_line_wrap(True)
        desc_label.set_max_width_chars(50)
        desc_label.set_margin_top(20)
        desc_label.set_margin_bottom(20)
        vbox.pack_start(desc_label, False, False, 0)
        
        # Info box
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        info_frame = Gtk.Frame(label="What this means")
        info_frame.set_margin_top(10)
        info_frame.set_margin_bottom(10)
        vbox.pack_start(info_frame, False, False, 0)
        
        info_frame.add(info_box)
        
        info_items = [
            "• Files created in this session will be deleted on shutdown",
            "• Settings changes are temporary",
            "• Browser history and cookies are not saved",
            "• Installed applications are available only this session",
            "• Your data stays private and isolated"
        ]
        
        for item in info_items:
            item_label = Gtk.Label()
            item_label.set_markup(f'<span size="small">{item}</span>')
            item_label.set_halign(Gtk.Align.START)
            item_label.set_margin_left(10)
            item_label.set_margin_right(10)
            info_box.pack_start(item_label, False, False, 0)
        
        # Spacer
        vbox.pack_start(Gtk.Label(), True, True, 0)
        
        # Start Session button
        start_button = Gtk.Button(label="Start Session")
        start_button.set_margin_top(20)
        start_button.set_margin_bottom(10)
        start_button.get_style_context().add_class("suggested-action")
        start_button.connect("clicked", self.on_start_session)
        vbox.pack_start(start_button, False, False, 0)
        
        # Apply dark theme styling
        self.apply_styling()

    def apply_styling(self):
        """Apply custom styling to match Lunar OS theme"""
        css = b"""
        window {
            background-color: #1a1a2e;
        }
        
        label {
            color: #ffffff;
            font-family: Sans;
        }
        
        button {
            background-color: #6c5ce7;
            color: #ffffff;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: bold;
        }
        
        button:hover {
            background-color: #5b4cdb;
        }
        
        frame {
            color: #6c5ce7;
        }
        """
        
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_start_session(self, button):
        """Handle Start Session button click"""
        # Close the window
        self.destroy()
        # This will exit the GTK main loop
        Gtk.main_quit()

def main():
    """Main entry point"""
    win = LunarWelcomeWindow()
    Gtk.main()

if __name__ == "__main__":
    main()
