import gi
import subprocess

gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gtk, GtkLayerShell, Gdk

class PopupWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="System Menu")
        self.set_default_size(250, 400)
        self.set_border_width(10)

        # Make this a layer shell surface
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.auto_exclusive_zone_enable(self)

        # Close when clicking outside or pressing ESC
        self.connect("focus-out-event", self.on_focus_lost)
        self.connect("key-press-event", self.on_key_press)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        # Make sure it behaves like a popup
        self.set_type_hint(Gdk.WindowTypeHint.POPUP_MENU)

        # Main vertical layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.add(vbox)

        # Close Button
        close_button = Gtk.Button(label="Close")
        close_button.connect("clicked", self.on_close_clicked)
        vbox.pack_start(close_button, False, False, 0)

        # Wi-Fi Section
        self.wifi_expander = Gtk.Expander(label="Wi-Fi")
        wifi_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.wifi_expander.add(wifi_box)
        vbox.pack_start(self.wifi_expander, False, False, 0)

        # Wi-Fi Toggle Button
        self.wifi_toggle = Gtk.ToggleButton(label="Wi-Fi Off")
        self.wifi_toggle.connect("toggled", self.toggle_wifi)
        wifi_box.pack_start(self.wifi_toggle, False, False, 0)

        # Refresh Wi-Fi Networks Button
        wifi_refresh = Gtk.Button(label="Refresh Wi-Fi")
        wifi_refresh.connect("clicked", self.load_wifi_networks)
        wifi_box.pack_start(wifi_refresh, False, False, 0)

        self.wifi_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        wifi_box.pack_start(self.wifi_list, False, False, 0)

        # Bluetooth Section
        self.bt_expander = Gtk.Expander(label="Bluetooth")
        bt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.bt_expander.add(bt_box)
        vbox.pack_start(self.bt_expander, False, False, 0)

        # Refresh Bluetooth Devices Button
        bt_refresh = Gtk.Button(label="Refresh Bluetooth")
        bt_refresh.connect("clicked", self.load_bluetooth_devices)
        bt_box.pack_start(bt_refresh, False, False, 0)

        self.bt_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        bt_box.pack_start(self.bt_list, False, False, 0)

        # Apps Section
        self.apps_expander = Gtk.Expander(label="Apps")
        apps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.apps_expander.add(apps_box)
        vbox.pack_start(self.apps_expander, False, False, 0)

        # App launch buttons
        apps = [("Emacs", "emacs"), ("Firefox", "firefox"), ("Xournal++", "xournalpp")]
        for name, cmd in apps:
            button = Gtk.Button(label=name)
            button.connect("clicked", self.launch_app, cmd)
            apps_box.pack_start(button, False, False, 0)

        # Brightness & Volume Sliders
        self.brightness_slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self.brightness_slider.set_range(0, 100)
        self.brightness_slider.set_value(self.get_brightness())
        self.brightness_slider.connect("value-changed", self.set_brightness)

        self.volume_slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self.volume_slider.set_range(0, 100)
        self.volume_slider.set_value(self.get_volume())
        self.volume_slider.connect("value-changed", self.set_volume)

        vbox.pack_start(Gtk.Label(label="Brightness"), False, False, 0)
        vbox.pack_start(self.brightness_slider, False, False, 0)

        vbox.pack_start(Gtk.Label(label="Volume"), False, False, 0)
        vbox.pack_start(self.volume_slider, False, False, 0)

        self.show_all()

        # Grab focus when created
        self.grab_focus()
        self.grab_add()

    def on_focus_lost(self, widget, event=None):
        """Close when clicking outside the popup or losing focus."""
        self.destroy()

    def on_key_press(self, widget, event):
        """Close when pressing ESC."""
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()

    def on_close_clicked(self, button):
        """Close when clicking the close button."""
        self.destroy()

    def load_wifi_networks(self, button):
        """Load available Wi-Fi networks using iwctl."""
        for child in self.wifi_list.get_children():
            self.wifi_list.remove(child)

        try:
            subprocess.run(["iwctl", "station", "wlan0", "scan"], check=True)
            output = subprocess.check_output(["iwctl", "station", "wlan0", "get-networks"], stderr=subprocess.DEVNULL)
            networks = output.decode().strip().split("\n")[1:]  # Skip header

            for line in networks:
                ssid = line.strip()
                if ssid:
                    label = Gtk.Label(label=ssid)
                    self.wifi_list.pack_start(label, False, False, 0)

        except Exception:
            self.wifi_list.pack_start(Gtk.Label(label="Error: iwctl not found"), False, False, 0)

        self.wifi_list.show_all()

    def load_bluetooth_devices(self, button):
        """Load available Bluetooth devices using bluetoothctl."""
        for child in self.bt_list.get_children():
            self.bt_list.remove(child)

        try:
            output = subprocess.check_output("bluetoothctl devices", shell=True)
            devices = output.decode().strip().split("\n")

            for device in devices:
                if device:
                    label = Gtk.Label(label=device)
                    self.bt_list.pack_start(label, False, False, 0)

        except Exception:
            self.bt_list.pack_start(Gtk.Label(label="Error: bluetoothctl not found"), False, False, 0)

        self.bt_list.show_all()

    def toggle_wifi(self, button):
        """Turn Wi-Fi on/off using systemd service for iwd."""
        if button.get_active():
            subprocess.run(["systemctl", "start", "iwd"], check=False)
            button.set_label("Wi-Fi On")
        else:
            subprocess.run(["systemctl", "stop", "iwd"], check=False)
            button.set_label("Wi-Fi Off")

    def launch_app(self, button, command):
        """Launch the selected app."""
        subprocess.Popen(command, shell=True)

    def get_brightness(self):
        """Get screen brightness (default 50 if command fails)."""
        try:
            return int(subprocess.check_output("brightnessctl g", shell=True)) / 255 * 100
        except Exception:
            return 50

    def set_brightness(self, slider):
        """Set screen brightness using brightnessctl."""
        value = int(slider.get_value() / 100 * 255)
        subprocess.run(f"brightnessctl s {value}", shell=True)

    def get_volume(self):
        """Get volume level (default 50 if command fails)."""
        try:
            return int(subprocess.check_output("pamixer --get-volume", shell=True).strip())
        except Exception:
            return 50

    def set_volume(self, slider):
        """Set volume using pamixer."""
        value = int(slider.get_value())
        subprocess.run(f"pamixer --set-volume {value}", shell=True)

win = PopupWindow()
win.connect("destroy", Gtk.main_quit)
Gtk.main()
