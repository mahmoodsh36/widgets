import gi
import subprocess

gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gtk, GtkLayerShell, Gdk, Gio

class PopupMenu(Gtk.Window):
    def __init__(self):
        super().__init__(title="System Menu")
        # self.set_default_size(300, 400)
        self.set_size_request(300, 400)
        self.set_border_width(10)
        self.set_type_hint(Gdk.WindowTypeHint.POPUP_MENU)
        self.get_style_context().add_class("popup")

        # make this a layer shell surface
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 10)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 10)
        GtkLayerShell.auto_exclusive_zone_enable(self)
        # ✅ Ensure the popup does not steal focus
        self.set_accept_focus(False)
        self.set_focus_on_map(False)  # Prevent auto-focusing
        self.set_skip_taskbar_hint(True)
        self.set_keep_above(True)  # Keep it above, but not block input

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.add(scrolled_window)
        scrolled_window.set_overlay_scrolling(False) # this may be better

        # close when clicking outside or pressing ESC
        self.connect("focus-out-event", self.on_focus_lost)
        self.connect("key-press-event", self.on_key_press)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        # main vertical layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scrolled_window.add(vbox)

        close_button = Gtk.Button(label="Close")
        close_button.connect("clicked", self.on_close_clicked)
        vbox.pack_start(close_button, False, False, 0)
        close_button.set_halign(Gtk.Align.CENTER)

        # wi-fi section
        self.wifi_expander = Gtk.Expander(label="Wi-Fi")
        wifi_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.wifi_expander.add(wifi_box)
        vbox.pack_start(self.wifi_expander, False, False, 0)

        # wi-fi toggle button
        self.wifi_toggle = Gtk.ToggleButton(label="Wi-Fi Off")
        self.wifi_toggle.connect("toggled", self.toggle_wifi)
        wifi_box.pack_start(self.wifi_toggle, False, False, 0)

        # refresh wi-fi networks button
        wifi_refresh = Gtk.Button(label="Refresh Wi-Fi")
        wifi_refresh.connect("clicked", self.load_wifi_networks)
        wifi_box.pack_start(wifi_refresh, False, False, 0)

        self.wifi_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        wifi_box.pack_start(self.wifi_list, False, False, 0)

        # bluetooth section
        self.bt_expander = Gtk.Expander(label="Bluetooth")
        bt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.bt_expander.add(bt_box)
        vbox.pack_start(self.bt_expander, False, False, 0)

        # refresh bluetooth devices button
        bt_refresh = Gtk.Button(label="Refresh Bluetooth")
        bt_refresh.connect("clicked", self.load_bluetooth_devices)
        bt_box.pack_start(bt_refresh, False, False, 0)

        self.bt_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        bt_box.pack_start(self.bt_list, False, False, 0)

        # apps section
        self.apps_expander = Gtk.Expander(label="Apps")
        apps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.apps_expander.add(apps_box)
        vbox.pack_start(self.apps_expander, False, False, 0)

        # app launch buttons
        apps = [("Emacs", "emacs"), ("Firefox", "firefox"), ("Xournal++", "xournalpp")]
        for name, cmd in apps:
            button = Gtk.Button(label=name)
            button.connect("clicked", self.launch_app, cmd)
            apps_box.pack_start(button, False, False, 0)

        # brightness & volume sliders
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

        # grab focus when created
        # self.grab_focus()

    def on_focus_lost(self, widget, event=None):
        self.destroy()

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()

    def on_close_clicked(self, button):
        self.destroy()

    def load_wifi_networks(self, button):
        for child in self.wifi_list.get_children():
            self.wifi_list.remove(child)

        try:
            # subprocess.run(["iwctl", "station", "wlan0", "scan"], check=True)
            output = subprocess.check_output(["iwctl", "station", "wlan0", "get-networks"], stderr=subprocess.DEVNULL)
            networks = output.decode().strip().split("\n")[1:] # skip header

            for line in networks:
                ssid = line.strip()
                if ssid:
                    label = Gtk.Label(label=ssid)
                    self.wifi_list.pack_start(label, False, False, 0)

        except Exception:
            self.wifi_list.pack_start(Gtk.Label(label="error: iwctl not found"), False, False, 0)

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
            self.bt_list.pack_start(Gtk.Label(label="error: bluetoothctl not found"), False, False, 0)

        self.bt_list.show_all()

    def toggle_wifi(self, button):
        if button.get_active():
            button.set_label("Wi-Fi On")
        else:
            button.set_label("Wi-Fi Off")

    def launch_app(self, button, command):
        """Launch the selected app."""
        subprocess.Popen(command, shell=True)

    def get_brightness(self):
        return 50

    def set_brightness(self, slider):
        pass

    def get_volume(self):
        return int(subprocess.check_output(
            r"pactl get-sink-volume @DEFAULT_SINK@ | grep -Po '\d+(?=%)' | head -n 1",
            shell=True).strip())

    def set_volume(self, slider):
        perc = slider.get_value()
        subprocess.run(
            f"pactl set-sink-volume @DEFAULT_SINK@ {perc}%",
            shell=True)

if __name__ == '__main__':
    win = PopupMenu()
    win.connect("destroy", Gtk.main_quit)
    css_provider = Gtk.CssProvider()
    css_provider.load_from_file(Gio.File.new_for_path('main.css'))
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
    )
    Gtk.main()