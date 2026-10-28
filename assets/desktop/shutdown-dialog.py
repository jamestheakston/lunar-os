#!/usr/bin/env python3
"""
Lunar OS Shutdown Dialog
Custom shutdown dialog with session discard confirmation
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import sys
import subprocess

class LunarShutdownDialog(Gtk.Dialog):
    def __init__(self, restart=False):
        self.restart = restart
        title = "Restart and Start Fresh" if restart else "Shut Down and Discard Session"
        
        super().__init__(
            title=title,
            flags=0
        )
        
        self.set_default_size(450, 300)
        self.set_border_width(20)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_modal(True)
        
        # Setup UI
        self.setup_ui()
        
        # Apply styling
        self.apply_styling()
        
        self.show_all()

    def setup_ui(self):
        """Setup the shutdown dialog UI"""
        # Add main box
        box = self.get_content_area()
        box.set_spacing(20)
        
        # Icon/emoji
        icon_label = Gtk.Label()
        icon_label.set_markup('<span size="xx-large">🌙</span>')
        box.pack_start(icon_label, False, False, 0)
        
        # Title
        title_text = "Restart and Start Fresh" if self.restart else "Shut Down and Discard Session"
        title_label = Gtk.Label()
        title_label.set_markup(f'<span size="large" weight="bold">{title_text}</span>')
        box.pack_start(title_label, False, False, 0)
        
        # Warning message
        if self.restart:
            message = (
                "Your computer will restart and all session data will be discarded. "
                "When it boots again, you'll start with a fresh, clean session."
            )
        else:
            message = (
                "Your computer will shut down and all session data will be discarded. "
                "Files, settings, and changes made in this session will be lost."
            )
        
        message_label = Gtk.Label()
        message_label.set_markup(f'<span size="small">{message}</span>')
        message_label.set_line_wrap(True)
        message_label.set_max_width_chars(40)
        box.pack_start(message_label, False, False, 0)
        
        # Info box
        info_frame = Gtk.Frame(label="Session Data to be Discarded")
        info_frame.set_margin_top(10)
        box.pack_start(info_frame, False, False, 0)
        
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        info_frame.add(info_box)
        
        discard_items = [
            "• Files in your home directory",
            "• Desktop files and folders",
            "• Downloads",
            "• Application settings",
            "• Browser history and cookies",
            "• Any installed session applications"
        ]
        
        for item in discard_items:
            item_label = Gtk.Label()
            item_label.set_markup(f'<span size="small">{item}</span>')
            item_label.set_halign(Gtk.Align.START)
            item_label.set_margin_left(10)
            item_label.set_margin_right(10)
            info_box.pack_start(item_label, False, False, 0)
        
        # Spacer
        box.pack_start(Gtk.Label(), True, True, 0)
        
        # Action buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_margin_top(20)
        box.pack_start(button_box, False, False, 0)
        
        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self.on_cancel)
        button_box.pack_start(cancel_button, True, True, 0)
        
        # Confirm button
        confirm_text = "Restart Now" if self.restart else "Shut Down Now"
        confirm_button = Gtk.Button(label=confirm_text)
        confirm_button.get_style_context().add_class("destructive-action")
        confirm_button.connect("clicked", self.on_confirm)
        button_box.pack_start(confirm_button, True, True, 0)

    def apply_styling(self):
        """Apply custom styling to match Lunar OS theme"""
        css = b"""
        dialog {
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
            padding: 10px 20px;
        }
        
        button:hover {
            background-color: #5b4cdb;
        }
        
        button.destructive-action {
            background-color: #e74c3c;
        }
        
        button.destructive-action:hover {
            background-color: #c0392b;
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

    def on_cancel(self, button):
        """Handle Cancel button click"""
        self.destroy()
        Gtk.main_quit()

    def on_confirm(self, button):
        """Handle confirm button click - execute shutdown/restart"""
        self.destroy()
        
        try:
            if self.restart:
                # Restart the system
                subprocess.run(["systemctl", "reboot"], check=False)
            else:
                # Shutdown the system
                subprocess.run(["systemctl", "poweroff"], check=False)
        except Exception as e:
            print(f"Error executing shutdown/restart: {e}")
            # Fallback to traditional commands
            if self.restart:
                subprocess.run(["reboot"], check=False)
            else:
                subprocess.run(["poweroff"], check=False)
        
        Gtk.main_quit()

def main():
    """Main entry point"""
    # Check if --restart flag is passed
    restart = "--restart" in sys.argv
    
    dialog = LunarShutdownDialog(restart)
    response = dialog.run()
    
    if response == Gtk.ResponseType.DELETE_EVENT:
        # Window was closed without button click
        Gtk.main_quit()

if __name__ == "__main__":
    main()
