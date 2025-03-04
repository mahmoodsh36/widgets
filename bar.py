#!/usr/bin/env python3
import subprocess
import re
from datetime import datetime
import random

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell, GLib, Gio

import hyprland
import pulseaudio

class VolumeSlider(Gtk.Box):
    def __init__(self):
        super(VolumeSlider, self).__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.icon = Gtk.Image.new_from_icon_name("audio-volume-high-symbolic", Gtk.IconSize.BUTTON)
        adjustment = Gtk.Adjustment(value=50, lower=0, upper=100, step_increment=1, page_increment=10, page_size=0)
        self.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment)
        self.scale.set_digits(0)
        self.scale.set_draw_value(True)
        self.scale.set_value_pos(Gtk.PositionType.LEFT)
        self.scale.set_size_request(200, -1)
        self.scale.connect(
            "value-changed",
            lambda x: pulseaudio.set_default_sink_volume(int(self.scale.get_value()))
        )
        self.pack_start(self.icon, False, False, 0)
        self.pack_start(self.scale, False, False, 0)

class BrightnessSlider(Gtk.VolumeButton):
    def __init__(self):
        super(BrightnessSlider, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        self.connect("value-changed", self.on_changed)

    def on_changed(self, volumebutton, value):
        print("value: %0.2f" % (value))

class SystemBar(Gtk.Window):
    def __init__(self):
        super().__init__()
        # screen = Gdk.Screen.get_default()
        # width = screen.get_width()
        # self.set_size_request(width, -1)
        # self.set_vexpand(False)
        # self.set_hexpand(False)
        self.set_title("bar")

        # initialize gtk layer shell
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.auto_exclusive_zone_enable(self)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)

        # create a container for the bar
        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.box.set_homogeneous(False)
        self.add(self.box)

        # workspace buttons container
        self.workspace_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.box.pack_start(self.workspace_box, False, False, 0)

        # window title label
        self.main_label = Gtk.Label(label="track")
        self.box.pack_start(self.main_label, True, True, 0)

        # initialize workspace buttons
        self.workspace_buttons = []
        self.update_workspace_buttons()

        # add date label
        self.date_label = Gtk.Label(label="Date")
        self.box.pack_end(self.date_label, False, False, 0)

        # add volume slider
        self.volume_slider = VolumeSlider()
        self.box.pack_end(self.volume_slider, False, False, 0)

        # add battery label
        self.bat_label = Gtk.Label(label="battery")
        self.box.pack_end(self.bat_label, False, False, 0)

        # brightness slider
        # self.brightness_slider = BrightnessSlider()
        # self.box.pack_end(self.brightness_slider, False, False, 0)

        # periodic updates
        GLib.timeout_add_seconds(1, self.update_date)
        GLib.timeout_add_seconds(1, self.update_battery)
        GLib.timeout_add_seconds(0.3, self.update_track_text)

        # hyprland listener for workspace changes
        def hyprland_handler(event_line):
            if event_line.startswith('workspace>>'):
                GLib.idle_add(lambda: (self.update_workspace_buttons(), self.show_all()))
        hyprland.add_listener(hyprland_handler)

        self.update_volume()
        # pulseaudio listen for volume changes
        def pulseaudio_handler(event_line):
            GLib.idle_add(lambda: self.update_volume())
        pulseaudio.add_listener(pulseaudio_handler)

    def update_volume(self):
        self.volume_slider.scale.set_value(int(pulseaudio.get_default_sink_volume()))

    def update_workspace_buttons(self):
        """fetch the current workspace information and create buttons for each workspace."""
        result = subprocess.run(["hyprctl", "workspaces"], capture_output=True, text=True)
        workspaces = self.parse_workspaces(result.stdout)

        # remove old buttons
        for button in self.workspace_buttons:
            self.workspace_box.remove(button)

        self.workspace_buttons.clear()

        # fetch the current active workspace
        current_workspace = self.get_current_workspace_from_hyprland()

        # add new buttons for each workspace
        for i, workspace in enumerate(workspaces):
            button = Gtk.Button(label=str(workspace['id']))
            button.connect("clicked", self.on_workspace_button_clicked, workspace['id'])
            self.workspace_buttons.append(button)
            self.workspace_box.pack_start(button, False, False, 0)
            if current_workspace == workspace['id']:
                button_context = button.get_style_context()
                button_context.add_class("highlighted")

        self.workspace_box.show_all()

    def parse_workspaces(self, output):
        """parse workspace information from the hyprctl output."""
        workspaces = []
        for line in output.splitlines():
            match = re.match(r'workspace ID (\d+)', line)
            if match:
                workspaces.append({'id': int(match.group(1))})
        workspaces.sort(key=lambda x: x['id'])
        return workspaces

    def on_workspace_button_clicked(self, button, workspace_id):
        """handle workspace button clicks and switch workspace."""
        subprocess.run(["hyprctl", "dispatch", "workspace", str(workspace_id)])

    def update_track_text(self):
        """update the current workspace label and button state."""
        result = subprocess.run(["current_mpv_track_more.sh"],
                                capture_output=True, text=True, shell=True)
        if result:
            self.main_label.set_text(result.stdout[:80])
        return True # keep the timeout running

    def get_current_workspace_from_hyprland(self):
        """get the current workspace using hyprland IPC."""
        result = subprocess.run(["hyprctl", "activeworkspace"], capture_output=True, text=True)
        match = re.search(r'workspace ID (\d+)', result.stdout)
        return int(match.group(1)) if match else None

    def update_date(self):
        """update the date label."""
        now = datetime.now()
        self.date_label.set_text(now.strftime("%a %H:%M:%S %Y-%m-%d"))
        return True # keep updating every second

    def update_battery(self):
        """update the battery label."""
        out = subprocess.check_output("acpi | grep -v ' 0%'", shell=True).decode()[:-1].split(', ')[1]
        self.bat_label.set_text('BAT ' + out)
        return True # keep updating every second

if __name__ == "__main__":
    window = SystemBar()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()

    css_provider = Gtk.CssProvider()
    css_provider.load_from_file(Gio.File.new_for_path('main.css'))
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
    )

    Gtk.main()