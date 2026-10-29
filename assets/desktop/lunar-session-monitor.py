#!/usr/bin/env python3
import os
import subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

OVERLAY_PATHS = ("/run/live/overlay", "/")
LOW_RAM_BYTES = 2 * 1024 ** 3
LOW_AVAILABLE_BYTES = 150 * 1024 ** 2
STORAGE_WARN_RATIO = 0.85
INTERVAL_SECONDS = 5


def read_meminfo():
    values = {}
    with open("/proc/meminfo") as handle:
        for line in handle:
            key, _, rest = line.partition(":")
            values[key] = int(rest.split()[0]) * 1024
    return values


def overlay_usage():
    for path in OVERLAY_PATHS:
        try:
            stat = os.statvfs(path)
        except OSError:
            continue
        total = stat.f_blocks * stat.f_frsize
        free = stat.f_bavail * stat.f_frsize
        if total > 0:
            return total - free, total
    return 0, 0


def human(size):
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024


def notify(title, message, urgency="normal"):
    subprocess.run(
        ["notify-send", "-u", urgency, "-i", "lunar-os", title, message],
        check=False,
    )


def launch(*command):
    subprocess.Popen(command)


class SessionMonitor:
    def __init__(self):
        self.warned_storage = False
        self.warned_memory = False
        self.icon = Gtk.StatusIcon.new_from_icon_name("lunar-os")
        self.icon.set_title("Lunar OS session")
        self.icon.connect("activate", self.on_activate)
        self.icon.connect("popup-menu", self.on_popup)
        self.refresh()
        GLib.timeout_add_seconds(INTERVAL_SECONDS, self.refresh)
        GLib.timeout_add_seconds(3, self.startup_check)

    def summary(self):
        used, total = overlay_usage()
        mem = read_meminfo()
        storage = f"Session storage: {human(used)} used of {human(total)}" if total else "Session storage: unavailable"
        memory = f"Memory available: {human(mem['MemAvailable'])} of {human(mem['MemTotal'])}"
        return storage, memory, used, total, mem

    def refresh(self):
        storage, memory, used, total, mem = self.summary()
        self.icon.set_tooltip_text(
            "Temporary session: files are discarded at shutdown\n" + storage + "\n" + memory
        )
        if total and used / total >= STORAGE_WARN_RATIO and not self.warned_storage:
            self.warned_storage = True
            notify(
                "Session storage almost full",
                "Free space in Temporary Files or Downloads. Session data lives in memory and is limited by RAM.",
                "critical",
            )
        elif total and used / total < STORAGE_WARN_RATIO - 0.1:
            self.warned_storage = False
        if mem["MemAvailable"] < LOW_AVAILABLE_BYTES and not self.warned_memory:
            self.warned_memory = True
            notify(
                "Low memory",
                "Close applications or delete session files to avoid slowdowns.",
                "critical",
            )
        elif mem["MemAvailable"] > LOW_AVAILABLE_BYTES * 2:
            self.warned_memory = False
        return True

    def startup_check(self):
        mem = read_meminfo()
        if mem["MemTotal"] < LOW_RAM_BYTES:
            notify(
                "Limited memory",
                f"This computer has {human(mem['MemTotal'])} of RAM. Session files share that memory, so keep large downloads to a minimum.",
            )
        return False

    def on_activate(self, _icon):
        storage, memory, _used, _total, _mem = self.summary()
        notify("Temporary session", storage + "\n" + memory + "\nFiles are discarded when the computer shuts down.")

    def on_popup(self, _icon, button, time):
        storage, memory, _used, _total, _mem = self.summary()
        menu = Gtk.Menu()
        for text in ("Temporary session", storage, memory):
            item = Gtk.MenuItem(label=text)
            item.set_sensitive(False)
            menu.append(item)
        menu.append(Gtk.SeparatorMenuItem())
        entries = (
            ("Open Temporary Files", ("pcmanfm", "/tmp")),
            ("Shut Down\u2026", ("/usr/local/bin/lunar-shutdown",)),
            ("Restart\u2026", ("/usr/local/bin/lunar-restart",)),
            ("Log Out\u2026", ("/usr/local/bin/lunar-logout",)),
        )
        for label, command in entries:
            item = Gtk.MenuItem(label=label)
            item.connect("activate", lambda _i, c=command: launch(*c))
            menu.append(item)
        menu.show_all()
        menu.popup(None, None, Gtk.StatusIcon.position_menu, self.icon, button, time)


def main():
    SessionMonitor()
    Gtk.main()


if __name__ == "__main__":
    main()
