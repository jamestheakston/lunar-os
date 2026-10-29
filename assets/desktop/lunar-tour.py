#!/usr/bin/env python3
import os
import subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

HOME = os.path.expanduser("~")
TOUR_COMPLETE = os.path.join(HOME, ".config", "lunar-os", "tour-complete")

CSS = b"""
window {
    background-color: #f5f5f5;
}
.welcome-box {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 24px;
    margin: 20px;
}
.step-indicator {
    background-color: #e8e8e8;
    border-radius: 12px;
    padding: 8px 16px;
    margin-bottom: 16px;
}
.current-step {
    background-color: #6c5ce7;
    color: white;
}
.content-area {
    background-color: #f8f8ff;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
}
.content-area label {
    color: #000000;
}
.navigation {
    margin-top: 16px;
}
.nav-button {
    background-color: #6c5ce7;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
}
.nav-button:hover {
    background-color: #7d6ff0;
}
.skip-button {
    background-color: #95a5a6;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
}
"""

STEPS = [
    {
        "title": "Welcome to Lunar OS",
        "content": "Lunar OS is a completely disposable operating system.\n\nAll files, settings, and downloads live in memory and are discarded when you shut down or restart.\n\nThis provides:\n• Maximum privacy\n• No traces left behind\n• A fresh start every boot\n\nClick Next to learn more.",
    },
    {
        "title": "Desktop Basics",
        "content": "The desktop includes:\n\n• **Panel**: Bottom bar with menu, apps, and system tray\n• **Menu**: Click the moon icon to access applications\n• **Taskbar**: Shows open windows\n• **System Tray**: Shows network, volume, and time\n\nTry clicking the menu button to see available applications.",
    },
    {
        "title": "File Management",
        "content": "Orbit Explorer (file manager) lets you:\n\n• Browse files and folders\n• Open, copy, move, and delete files\n• Access your Home folder, Documents, Pictures, etc.\n• Navigate to Temporary Files for session data\n\nTip: All files in your home folder are temporary.",
    },
    {
        "title": "Lunar Store",
        "content": "Lunar Store lets you install additional applications:\n\n• Open Lunar Store from the menu or desktop\n• Browse categories: Internet, Multimedia, Office, Games, etc.\n• Click Install to add applications\n• Progress bar shows installation status\n\nNote: Installed apps are discarded on reboot.",
    },
    {
        "title": "Settings",
        "content": "Lunar Settings provides:\n\n• **Appearance**: Dark mode, wallpaper\n• **Display**: Resolution and monitor setup\n• **Network**: Wi-Fi and VPN connections\n• **Session**: Shutdown, restart, logout\n• **Storage**: View RAM-based storage usage\n\nClick the gear icon in the panel to open Settings.",
    },
    {
        "title": "Shutdown",
        "content": "When you're done:\n\n• Click the shutdown button in the panel\n• Or press Super+Q\n• Or use Lunar Settings → Session → Shut Down\n\nThe system will power off and all session data will be discarded.\n\nYou can also restart to start fresh.",
    },
]


class WelcomeTour(Gtk.Window):
    def __init__(self):
        super().__init__(title="Welcome Tour")
        self.set_default_size(600, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("lunar-os")
        self.connect("destroy", Gtk.main_quit)
        
        self.current_step = 0
        self.load_progress()
        
        self.build()
        self.show_all()
    
    def load_progress(self):
        if os.path.exists(TOUR_COMPLETE):
            with open(TOUR_COMPLETE, "r") as f:
                self.current_step = int(f.read().strip())
    
    def save_progress(self):
        os.makedirs(os.path.dirname(TOUR_COMPLETE), exist_ok=True)
        with open(TOUR_COMPLETE, "w") as f:
            f.write(str(self.current_step))
    
    def build(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_border_width(20)
        self.add(main_box)
        
        # Title
        title = Gtk.Label()
        title.set_markup('<span size="x-large" weight="bold">Welcome Tour</span>')
        title.set_margin_bottom(16)
        main_box.pack_start(title, False, False, 0)
        
        # Step indicator
        indicator_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for i in range(len(STEPS)):
            step_label = Gtk.Label(label=f"{i + 1}")
            step_label.get_style_context().add_class("step-indicator")
            if i == self.current_step:
                step_label.get_style_context().add_class("current-step")
            indicator_box.pack_start(step_label, False, False, 0)
        main_box.pack_start(indicator_box, False, False, 0)
        
        # Content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content_box.get_style_context().add_class("content-area")
        
        title_label = Gtk.Label()
        title_label.set_markup(f'<span weight="bold" size="large">{STEPS[self.current_step]["title"]}</span>')
        title_label.set_halign(Gtk.Align.START)
        content_box.pack_start(title_label, False, False, 0)
        
        content_text = Gtk.Label(label=STEPS[self.current_step]["content"])
        content_text.set_halign(Gtk.Align.START)
        content_text.set_xalign(0)
        content_text.set_line_wrap(True)
        content_text.set_max_width_chars(70)
        content_box.pack_start(content_text, False, False, 0)
        
        main_box.pack_start(content_box, True, True, 0)
        
        # Navigation
        nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        nav_box.get_style_context().add_class("navigation")
        
        skip_button = Gtk.Button(label="Skip Tour")
        skip_button.get_style_context().add_class("skip-button")
        skip_button.connect("clicked", self.on_skip)
        nav_box.pack_start(skip_button, False, False, 0)
        
        nav_box.pack_start(Gtk.Box(), True, True, 0)
        
        back_button = Gtk.Button(label="Back")
        back_button.get_style_context().add_class("nav-button")
        back_button.set_sensitive(self.current_step > 0)
        back_button.connect("clicked", self.on_back)
        nav_box.pack_start(back_button, False, False, 0)
        
        next_button = Gtk.Button(label="Next")
        next_button.get_style_context().add_class("nav-button")
        next_button.set_sensitive(self.current_step < len(STEPS) - 1)
        next_button.connect("clicked", self.on_next)
        nav_box.pack_start(next_button, False, False, 0)
        
        main_box.pack_start(nav_box, False, False, 0)
    
    def on_back(self, button):
        if self.current_step > 0:
            self.current_step -= 1
            self.save_progress()
            self.update_ui()
    
    def on_next(self, button):
        if self.current_step < len(STEPS) - 1:
            self.current_step += 1
            self.save_progress()
            self.update_ui()
        else:
            self.on_complete(button)
    
    def on_skip(self, button):
        self.current_step = len(STEPS) - 1
        self.save_progress()
        self.destroy()
    
    def on_complete(self, button):
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CLOSE,
            text="Tour Complete!",
        )
        dialog.format_secondary_text("You've completed the Welcome Tour. Lunar OS is ready to use!")
        dialog.run()
        dialog.destroy()
        self.destroy()
    
    def update_ui(self):
        # Rebuild the entire UI to update step indicator and content
        for child in self.get_children():
            self.remove(child)
        self.build()


def main():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    WelcomeTour()
    Gtk.main()


if __name__ == "__main__":
    main()
