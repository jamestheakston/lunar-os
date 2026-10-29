#!/usr/bin/env python3
import os
import sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

MARKER = "/tmp/.lunar-welcome-dismissed"
LOGO = "/usr/share/lunar-os/welcome-icon.png"

CSS = b"""
window.lunar-welcome { background-color: #1a1a2e; }
window.lunar-welcome label { color: #e8e8f0; }
window.lunar-welcome .heading { font-size: 24px; font-weight: bold; color: #ffffff; }
window.lunar-welcome .body { font-size: 14px; color: #c8c8d8; }
window.lunar-welcome .note { font-size: 12px; color: #9a9ab8; }
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

        button = Gtk.Button(label="Start session")
        button.get_style_context().add_class("start")
        button.set_halign(Gtk.Align.CENTER)
        button.set_margin_top(14)
        button.connect("clicked", lambda _b: self.destroy())
        box.pack_start(button, False, False, 0)
        button.grab_focus()

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
