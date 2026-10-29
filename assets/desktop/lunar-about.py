#!/usr/bin/env python3
from datetime import datetime

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

CURRENT_YEAR = datetime.now().year
AUTHOR = "James Theakston"
LICENSE = "MIT"

MIT_LICENSE_TEXT = f"""MIT License

Copyright (c) {CURRENT_YEAR} {AUTHOR}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

CHANGELOG = """Version 1.0.0 (2026)
- Initial release of Lunar OS Home Edition
- Disposable session architecture with RAM-based storage
- LXDE desktop environment with Lunar OS branding
- Built-in VPN support (WireGuard)
- Browser selection (Firefox ESR, Tor Browser)
- Custom shutdown and restart dialogs
- Welcome window with session information
- Welcome Tour for first-time users
- Wallpaper Gallery with multiple options
- Keyboard Shortcuts guide
- System Sounds configuration
- Metadata Stripper for privacy
- Lunar Store for installing applications
"""

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
.changelog-box {
    background-color: #f8f8ff;
    border-radius: 8px;
    padding: 16px;
    margin: 16px;
}
.info-label {
    font-size: 14px;
    margin: 8px;
}
.action-button {
    background-color: #6c5ce7;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
    margin: 8px;
}
.action-button:hover {
    background-color: #7d6ff0;
}
"""


class AboutApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="About Lunar OS")
        self.set_default_size(500, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("help-about")
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
        title.set_markup('<span size="xx-large" weight="bold">Lunar OS Home Edition</span>')
        header.pack_start(title, False, False, 0)
        
        subtitle = Gtk.Label(label=f"Version 1.0.0 • {CURRENT_YEAR} • James Theakston")
        header.pack_start(subtitle, False, False, 0)
        
        main_box.pack_start(header, False, False, 0)
        
        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.get_style_context().add_class("content")
        
        # Version info
        version_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        version_box.get_style_context().add_class("version-box")
        
        version_label = Gtk.Label(label="You are running Lunar OS Home Edition 1.0.0")
        version_label.get_style_context().add_class("info-label")
        version_box.pack_start(version_label, False, False, 0)
        
        copyright_label = Gtk.Label(label=f"© {CURRENT_YEAR} {AUTHOR}")
        copyright_label.get_style_context().add_class("info-label")
        version_box.pack_start(copyright_label, False, False, 0)
        
        content.pack_start(version_box, False, False, 0)
        
        # License
        license_button = Gtk.Button(label="View MIT License")
        license_button.get_style_context().add_class("action-button")
        license_button.connect("clicked", self.show_license)
        content.pack_start(license_button, False, False, 0)
        
        # Changelog
        changelog_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        changelog_box.get_style_context().add_class("changelog-box")
        
        changelog_title = Gtk.Label()
        changelog_title.set_markup('<span weight="bold">Changelog</span>')
        changelog_box.pack_start(changelog_title, False, False, 0)
        
        changelog_text = Gtk.TextView()
        changelog_text.set_editable(False)
        changelog_text.set_wrap_mode(Gtk.WrapMode.WORD)
        buffer = changelog_text.get_buffer()
        buffer.set_text(CHANGELOG)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(200)
        scrolled.add(changelog_text)
        changelog_box.pack_start(scrolled, True, True, 0)
        
        content.pack_start(changelog_box, True, True, 0)
        
        main_box.pack_start(content, True, True, 0)
    
    def show_license(self, button):
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CLOSE,
            text="MIT License",
        )
        
        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        buffer = text_view.get_buffer()
        buffer.set_text(MIT_LICENSE_TEXT)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(300)
        scrolled.set_min_content_width(500)
        scrolled.add(text_view)
        
        dialog.get_content_area().pack_start(scrolled, True, True, 0)
        dialog.show_all()
        dialog.run()
        dialog.destroy()


def main():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    AboutApp()
    Gtk.main()


if __name__ == "__main__":
    main()
