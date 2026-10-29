#!/usr/bin/env python3
import os
import subprocess
import sys

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk

HOME = os.path.expanduser("~")

CSS = b"""
window {
    background-color: #f5f5f5;
}
.info-box {
    background-color: #e8f4ff;
    border: 1px solid #a8d0f0;
    border-radius: 8px;
    padding: 12px;
    margin: 8px;
}
.info-label {
    color: #333;
    font-size: 12px;
}
.file-item {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 12px;
    margin: 8px;
}
.file-item:hover {
    background-color: #f8f8ff;
    border-color: #a8d0f0;
}
.file-name {
    font-size: 14px;
    font-weight: bold;
}
.file-status {
    font-size: 12px;
    color: #666;
}
.strip-button {
    background-color: #6c5ce7;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
}
.strip-button:hover {
    background-color: #7d6ff0;
}
.progress-bar {
    margin-top: 8px;
}
"""


class MetadataStripper(Gtk.Window):
    def __init__(self):
        super().__init__(title="Lunar Metadata Stripper")
        self.set_default_size(700, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("lunar-os")
        self.connect("destroy", Gtk.main_quit)
        
        self.files = []
        self.processing = False
        
        self.build()
        self.show_all()
    
    def build(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_border_width(16)
        self.add(main_box)
        
        # Info box
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info_box.get_style_context().add_class("info-box")
        
        info_label = Gtk.Label()
        info_label.set_markup(
            '<span weight="bold">Metadata Stripper</span>\n'
            'Remove hidden metadata (EXIF, GPS, author info) from files.\n'
            'Supported formats: JPG, PNG, PDF, DOCX, MP3, MP4, and more.'
        )
        info_label.get_style_context().add_class("info-label")
        info_label.set_line_wrap(True)
        info_label.set_max_width_chars(70)
        info_label.set_halign(Gtk.Align.START)
        info_label.set_xalign(0)
        info_box.pack_start(info_label, False, False, 0)
        
        main_box.pack_start(info_box, False, False, 0)
        
        # File selection
        file_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        add_button = Gtk.Button(label="Add Files")
        add_button.connect("clicked", self.on_add_files)
        file_box.pack_start(add_button, False, False, 0)
        
        clear_button = Gtk.Button(label="Clear All")
        clear_button.connect("clicked", self.on_clear_files)
        file_box.pack_start(clear_button, False, False, 0)
        
        strip_all_button = Gtk.Button(label="Strip All")
        strip_all_button.get_style_context().add_class("strip-button")
        strip_all_button.connect("clicked", self.on_strip_all)
        file_box.pack_end(strip_all_button, False, False, 0)
        
        main_box.pack_start(file_box, False, False, 0)
        
        # Files list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.files_list = Gtk.ListBox()
        self.files_list.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.files_list)
        
        main_box.pack_start(scrolled, True, True, 0)
        
        # Status bar
        self.status_label = Gtk.Label(label="No files added")
        self.status_label.set_halign(Gtk.Align.START)
        main_box.pack_start(self.status_label, False, False, 0)
    
    def on_add_files(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select files to strip metadata",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Add", Gtk.ResponseType.OK)
        dialog.set_select_multiple(True)
        
        if dialog.run() == Gtk.ResponseType.OK:
            files = dialog.get_filenames()
            for filepath in files:
                self.files.append(filepath)
            self.refresh_files_list()
        
        dialog.destroy()
    
    def on_clear_files(self, button):
        self.files = []
        self.refresh_files_list()
    
    def refresh_files_list(self):
        # Clear existing
        for row in self.files_list.get_children():
            self.files_list.remove(row)
        
        for filepath in self.files:
            filename = os.path.basename(filepath)
            
            file_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            file_box.get_style_context().add_class("file-item")
            
            # Name and button row
            top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            
            name_label = Gtk.Label(label=filename)
            name_label.get_style_context().add_class("file-name")
            name_label.set_halign(Gtk.Align.START)
            top_row.pack_start(name_label, True, True, 0)
            
            strip_button = Gtk.Button(label="Strip")
            strip_button.get_style_context().add_class("strip-button")
            strip_button.connect("clicked", self.on_strip_file, filepath, strip_button)
            top_row.pack_start(strip_button, False, False, 0)
            
            remove_button = Gtk.Button(label="Remove")
            remove_button.connect("clicked", self.on_remove_file, filepath)
            top_row.pack_start(remove_button, False, False, 0)
            
            file_box.pack_start(top_row, False, False, 0)
            
            # Progress bar (hidden by default)
            progress_bar = Gtk.ProgressBar()
            progress_bar.set_show_text(True)
            progress_bar.set_visible(False)
            progress_bar.get_style_context().add_class("progress-bar")
            file_box.pack_start(progress_bar, False, False, 0)
            
            row = Gtk.ListBoxRow()
            row.add(file_box)
            self.files_list.add(row)
        
        self.files_list.show_all()
        self.status_label.set_text(f"{len(self.files)} file(s) added")
    
    def on_remove_file(self, button, filepath):
        if filepath in self.files:
            self.files.remove(filepath)
            self.refresh_files_list()
    
    def on_strip_file(self, button, filepath, strip_button):
        if self.processing:
            return
        
        self.processing = True
        strip_button.set_sensitive(False)
        strip_button.set_label("Stripping...")
        
        # Find the progress bar
        file_box = button.get_parent().get_parent()
        progress_bar = file_box.get_children()[1]
        progress_bar.set_visible(True)
        progress_bar.set_text("Processing...")
        progress_bar.set_fraction(0.0)
        
        # Strip metadata in background
        import threading
        threading.Thread(
            target=self.strip_metadata,
            args=(filepath, progress_bar, strip_button),
            daemon=True
        ).start()
    
    def on_strip_all(self, button):
        if self.processing:
            return
        
        for row in self.files_list.get_children():
            file_box = row.get_child()
            top_row = file_box.get_children()[0]
            strip_button = top_row.get_children()[1]
            # Trigger strip for each file
            # (This would need proper queueing in a real implementation)
            pass
    
    def strip_metadata(self, filepath, progress_bar, strip_button):
        try:
            # Check if mat2 is available
            if subprocess.run(["which", "mat2"], capture_output=True).returncode == 0:
                # Use mat2
                GLib.idle_add(lambda: progress_bar.set_text("Stripping with mat2..."))
                GLib.idle_add(lambda: progress_bar.set_fraction(0.5))
                
                result = subprocess.run(
                    ["mat2", "--inplace", filepath],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    GLib.idle_add(lambda: progress_bar.set_text("Complete!"))
                    GLib.idle_add(lambda: progress_bar.set_fraction(1.0))
                    GLib.idle_add(lambda: strip_button.set_label("Done"))
                    GLib.idle_add(lambda: strip_button.set_sensitive(False))
                else:
                    GLib.idle_add(lambda: progress_bar.set_text("Failed"))
                    GLib.idle_add(lambda: progress_bar.set_fraction(0.0))
                    GLib.idle_add(lambda: strip_button.set_sensitive(True))
                    GLib.idle_add(lambda: strip_button.set_label("Retry"))
            else:
                # Check if exiftool is available
                if subprocess.run(["which", "exiftool"], capture_output=True).returncode == 0:
                    GLib.idle_add(lambda: progress_bar.set_text("Stripping with exiftool..."))
                    GLib.idle_add(lambda: progress_bar.set_fraction(0.5))
                    
                    result = subprocess.run(
                        ["exiftool", "-all=", filepath],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        GLib.idle_add(lambda: progress_bar.set_text("Complete!"))
                        GLib.idle_add(lambda: progress_bar.set_fraction(1.0))
                        GLib.idle_add(lambda: strip_button.set_label("Done"))
                        GLib.idle_add(lambda: strip_button.set_sensitive(False))
                    else:
                        GLib.idle_add(lambda: progress_bar.set_text("Failed"))
                        GLib.idle_add(lambda: progress_bar.set_fraction(0.0))
                        GLib.idle_add(lambda: strip_button.set_sensitive(True))
                        GLib.idle_add(lambda: strip_button.set_label("Retry"))
                else:
                    GLib.idle_add(lambda: progress_bar.set_text("No tool available"))
                    GLib.idle_add(lambda: progress_bar.set_fraction(0.0))
                    GLib.idle_add(lambda: strip_button.set_sensitive(True))
                    GLib.idle_add(lambda: strip_button.set_label("Install mat2"))
        
        except Exception as e:
            GLib.idle_add(lambda: progress_bar.set_text("Error"))
            GLib.idle_add(lambda: progress_bar.set_fraction(0.0))
            GLib.idle_add(lambda: strip_button.set_sensitive(True))
            GLib.idle_add(lambda: strip_button.set_label("Retry"))
        
        finally:
            self.processing = False
            GLib.idle_add(lambda: progress_bar.set_visible(False))


def main():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    MetadataStripper()
    Gtk.main()


if __name__ == "__main__":
    main()
