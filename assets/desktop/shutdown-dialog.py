#!/usr/bin/env python3
import os
import subprocess
import sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

ACTIONS = {
    "shutdown": {
        "label": "Shut Down and Discard Session",
        "confirm": "Shut Down Now",
        "message": (
            "The computer will power off. Every file, setting and change from "
            "this session is discarded when it powers off, and the next boot "
            "starts fresh."
        ),
        "command": ["systemctl", "poweroff"],
        "destructive": True,
    },
    "restart": {
        "label": "Restart and Start Fresh",
        "confirm": "Restart Now",
        "message": (
            "The computer will restart into a new, clean session. Every file, "
            "setting and change from this session is discarded during the restart."
        ),
        "command": ["systemctl", "reboot"],
        "destructive": True,
    },
    "logout": {
        "label": "Log Out",
        "confirm": "Log Out Now",
        "message": (
            "Your applications close and you return to a screen with a single Log In "
            "button. Session files are kept in memory until you shut down or restart."
        ),
        "command": None,
        "destructive": False,
    },
}

CSS = b"""
window.lunar-dialog { background-color: #1a1a2e; }
window.lunar-dialog label { color: #e8e8f0; }
window.lunar-dialog .heading { font-size: 20px; font-weight: bold; color: #ffffff; }
window.lunar-dialog .note { font-size: 12px; color: #9a9ab8; }
window.lunar-dialog button {
    background-image: none;
    background-color: #2a2a48;
    color: #ffffff;
    border: 1px solid #3a3a5c;
    border-radius: 10px;
    padding: 10px 18px;
}
window.lunar-dialog button:hover { background-color: #34345a; }
window.lunar-dialog button.primary { background-color: #6c5ce7; border-color: #6c5ce7; }
window.lunar-dialog button.primary:hover { background-color: #7d6ff0; }
window.lunar-dialog button.danger { background-color: #c0392b; border-color: #c0392b; }
window.lunar-dialog button.danger:hover { background-color: #d44637; }
"""

DISCLAIMER = (
    "Disposable storage reduces persistence. It cannot remove data you copied "
    "to external drives or sent over the network."
)


def log(message):
    subprocess.run(["logger", "-t", "lunar-os", message], check=False)


def run_logout():
    session = os.environ.get("XDG_SESSION_ID")
    if session:
        return subprocess.run(["loginctl", "terminate-session", session], check=False)
    return subprocess.run(["loginctl", "terminate-user", str(os.getuid())], check=False)


class ShutdownDialog(Gtk.Window):
    def __init__(self, preselect=None):
        super().__init__(title="Lunar OS")
        self.set_default_size(460, -1)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_icon_name("lunar-os")
        self.get_style_context().add_class("lunar-dialog")
        self.connect("destroy", Gtk.main_quit)
        self.connect("key-press-event", self.on_key)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(150)
        self.add(self.stack)

        self.stack.add_named(self.build_choose(), "choose")
        self.confirm_box = None
        self.show_all()

        if preselect in ACTIONS:
            self.show_confirm(preselect)

    def heading(self, text):
        label = Gtk.Label(label=text)
        label.get_style_context().add_class("heading")
        return label

    def note(self, text):
        label = Gtk.Label(label=text)
        label.get_style_context().add_class("note")
        label.set_line_wrap(True)
        label.set_justify(Gtk.Justification.CENTER)
        label.set_max_width_chars(56)
        return label

    def build_choose(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(28)
        box.pack_start(self.heading("You are in a temporary session"), False, False, 0)
        box.pack_start(
            self.note("Shutting down or restarting discards everything created in this session."),
            False, False, 6,
        )
        for key in ("shutdown", "restart", "logout"):
            button = Gtk.Button(label=ACTIONS[key]["label"])
            if key == "shutdown":
                button.get_style_context().add_class("primary")
            button.connect("clicked", lambda _b, k=key: self.show_confirm(k))
            box.pack_start(button, False, False, 0)
        cancel = Gtk.Button(label="Cancel")
        cancel.connect("clicked", lambda _b: self.destroy())
        box.pack_start(cancel, False, False, 6)
        box.pack_start(self.note(DISCLAIMER), False, False, 0)
        return box

    def show_confirm(self, key):
        action = ACTIONS[key]
        if self.confirm_box is not None:
            self.stack.remove(self.confirm_box)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_border_width(28)
        box.pack_start(self.heading(action["label"]), False, False, 0)
        message = Gtk.Label(label=action["message"])
        message.set_line_wrap(True)
        message.set_justify(Gtk.Justification.CENTER)
        message.set_max_width_chars(50)
        box.pack_start(message, False, False, 8)

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.set_homogeneous(True)
        cancel = Gtk.Button(label="Cancel")
        cancel.connect("clicked", lambda _b: self.destroy())
        confirm = Gtk.Button(label=action["confirm"])
        confirm.get_style_context().add_class("danger" if action["destructive"] else "primary")
        confirm.connect("clicked", lambda _b: self.execute(key))
        row.pack_start(cancel, True, True, 0)
        row.pack_start(confirm, True, True, 0)
        box.pack_start(row, False, False, 6)
        box.pack_start(self.note(DISCLAIMER), False, False, 0)

        self.confirm_box = box
        self.stack.add_named(box, "confirm")
        box.show_all()
        self.stack.set_visible_child_name("confirm")
        cancel.grab_focus()

    def execute(self, key):
        log("session action: " + key)
        self.hide()
        action = ACTIONS[key]
        if key == "logout":
            run_logout()
        else:
            subprocess.run(action["command"], check=False)
        Gtk.main_quit()

    def on_key(self, _widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
            return True
        return False


def main():
    preselect = None
    for arg in sys.argv[1:]:
        if arg in ("--shutdown", "--restart", "--logout"):
            preselect = arg[2:]
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    ShutdownDialog(preselect)
    Gtk.main()


if __name__ == "__main__":
    main()
