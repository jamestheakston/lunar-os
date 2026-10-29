#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("LightDM", "1")
from gi.repository import Gdk, GLib, Gtk, LightDM

USERNAME = "lunar"
FALLBACK_SESSION = "LXDE"
PASSWORD = "live"
LOGO = "/usr/share/lunar-os/welcome-icon.png"

CSS = b"""
window.lunar-greeter {
    background-color: #1a1a2e;
    background-image: url("/usr/share/backgrounds/lunar-os/wallpaper.png");
    background-size: cover;
    background-position: center;
}
window.lunar-greeter label { color: #e8e8f0; }
window.lunar-greeter .heading { font-size: 30px; font-weight: bold; color: #ffffff; }
window.lunar-greeter .note { font-size: 13px; color: #b0b0c8; }
window.lunar-greeter .error { font-size: 13px; color: #ff8a80; }
window.lunar-greeter button.login {
    background-image: none;
    background-color: #6c5ce7;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 12px 48px;
    font-size: 16px;
    font-weight: bold;
}
window.lunar-greeter button.login:hover { background-color: #7d6ff0; }
window.lunar-greeter button.login:disabled { background-color: #4a4a68; color: #a0a0b8; }
window.lunar-greeter button.power {
    background-image: none;
    background-color: rgba(26, 26, 46, 0.8);
    color: #e8e8f0;
    border: 1px solid #3a3a5c;
    border-radius: 8px;
    padding: 6px 14px;
}
window.lunar-greeter button.power:hover { background-color: #34345a; }
"""


class GreeterWindow(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.get_style_context().add_class("lunar-greeter")
        self.set_decorated(False)
        self.fullscreen()

        self.greeter = LightDM.Greeter()
        self.greeter.connect("authentication-complete", self.on_authentication_complete)
        self.greeter.connect("show-prompt", self.on_show_prompt)
        self.greeter.connect_to_daemon_sync()

        self.build()
        self.show_all()
        self.login_button.grab_focus()

    def build(self):
        overlay = Gtk.Overlay()
        self.add(overlay)

        center = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        center.set_halign(Gtk.Align.CENTER)
        center.set_valign(Gtk.Align.CENTER)
        overlay.add(center)

        try:
            center.pack_start(Gtk.Image.new_from_file(LOGO), False, False, 0)
        except GLib.Error:
            pass

        heading = Gtk.Label(label="Lunar OS")
        heading.get_style_context().add_class("heading")
        center.pack_start(heading, False, False, 0)

        note = Gtk.Label(label="You are logged out. Session files stay in memory until you shut down.")
        note.get_style_context().add_class("note")
        center.pack_start(note, False, False, 0)

        self.login_button = Gtk.Button(label="Log In")
        self.login_button.get_style_context().add_class("login")
        self.login_button.set_halign(Gtk.Align.CENTER)
        self.login_button.set_margin_top(18)
        self.login_button.set_can_default(True)
        self.login_button.connect("clicked", self.on_login)
        center.pack_start(self.login_button, False, False, 0)

        self.status = Gtk.Label(label="")
        self.status.get_style_context().add_class("error")
        center.pack_start(self.status, False, False, 0)

        power = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        power.set_halign(Gtk.Align.END)
        power.set_valign(Gtk.Align.END)
        power.set_margin_end(20)
        power.set_margin_bottom(20)
        if LightDM.get_can_restart():
            power.pack_start(self.power_button("Restart", LightDM.restart), False, False, 0)
        if LightDM.get_can_shutdown():
            power.pack_start(self.power_button("Shut Down", LightDM.shutdown), False, False, 0)
        overlay.add_overlay(power)

    def power_button(self, label, action):
        button = Gtk.Button(label=label)
        button.get_style_context().add_class("power")
        button.connect("clicked", lambda _b: self.run_power(action))
        return button

    def run_power(self, action):
        try:
            action()
        except GLib.Error as error:
            self.fail(str(error))

    def fail(self, message):
        self.status.set_text(message)
        self.login_button.set_sensitive(True)
        self.login_button.grab_focus()

    def on_login(self, _button):
        self.login_button.set_sensitive(False)
        self.status.set_text("")
        if self.greeter.get_in_authentication():
            self.greeter.cancel_authentication()
        started = False
        try:
            started = self.greeter.authenticate_autologin()
        except (AttributeError, GLib.Error):
            started = False
        if not started:
            self.greeter.authenticate(USERNAME)

    def on_show_prompt(self, greeter, _text, _prompt_type):
        greeter.respond(PASSWORD)

    def on_authentication_complete(self, greeter):
        if not greeter.get_is_authenticated():
            self.fail("Could not log in. Try again.")
            return
        session = greeter.get_default_session_hint() or FALLBACK_SESSION
        try:
            started = greeter.start_session_sync(session)
        except GLib.Error:
            started = False
        if not started:
            self.fail("Could not start the session. Try again.")


def main():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    GreeterWindow()
    Gtk.main()


if __name__ == "__main__":
    main()
