import gi
from gi.repository import Gtk, GLib
from pydbus import SystemBus

gi.require_version('Gtk', '3.0')

class WiFiWidget(Gtk.Window):
    def __init__(self):
        super().__init__(title="Wi-Fi Widget")
        self.set_default_size(400, 300)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(10)

        self.set_title("Wi-Fi Widget")

        # Layout setup
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # ComboBox for network selection
        self.network_combo = Gtk.ComboBoxText()
        self.network_combo.set_entry_text_column(0)

        # Rescan and Connect buttons
        self.rescan_button = Gtk.Button(label="Rescan")
        self.connect_button = Gtk.Button(label="Connect")
        self.toggle_wifi_button = Gtk.ToggleButton(label="Turn Wi-Fi Off")
        
        # Connect button actions
        self.rescan_button.connect("clicked", self.rescan_networks)
        self.connect_button.connect("clicked", self.on_connect_button_clicked)
        self.toggle_wifi_button.connect("toggled", self.on_wifi_toggle)

        # Pack widgets into the layout
        vbox.pack_start(self.network_combo, False, False, 0)
        vbox.pack_start(self.rescan_button, False, False, 0)
        vbox.pack_start(self.connect_button, False, False, 0)
        vbox.pack_start(self.toggle_wifi_button, False, False, 0)

        self.add(vbox)

        # Initialize DBus and NetworkManager
        self.bus = SystemBus()
        self.nm = self.bus.get("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
        self.device = None
        self.get_wifi_device()

    def get_wifi_device(self):
        """Get the wifi device and update available networks."""
        self.device = None
        # Fetch devices from NetworkManager
        devices = self.nm.GetDevices()

        for dev_path in devices:
            dev = self.bus.get("org.freedesktop.NetworkManager", dev_path)
            if dev.DeviceType == 2:  # 2 represents Wi-Fi devices
                self.device = dev
                break

        if self.device is None:
            print("No Wi-Fi device found.")
            return
        
        self.update_wifi_networks()

    def update_wifi_networks(self):
        """Update the list of available Wi-Fi networks."""
        self.network_combo.remove_all()

        # Fetch available networks
        aps = self.device.GetAccessPoints()

        for ap_path in aps:
            ap = self.bus.get("org.freedesktop.NetworkManager", ap_path)
            
            # Assuming ap.Ssid is a byte array
            ssid = "".join(chr(i) for i in ap.Ssid)  # Convert byte array to string
            
            self.network_combo.append_text(ssid)

    def on_connect_button_clicked(self, button):
        """Connect to the selected Wi-Fi network."""
        selected_network = self.network_combo.get_active_text()

        if selected_network:
            print(f"Connecting to {selected_network}...")
            self.simulate_wifi_connect(selected_network)
        else:
            print("No network selected.")

    def simulate_wifi_connect(self, ssid):
        """Simulate Wi-Fi connection."""
        print(f"Successfully connected to {ssid}")
        # You can implement actual connection logic using NetworkManager DBus API here.

    def rescan_networks(self, button):
        """Rescan for available networks."""
        print("Rescanning for Wi-Fi networks...")
        self.get_wifi_device()

    def on_wifi_toggle(self, button):
        """Toggle Wi-Fi on or off."""
        if button.get_active():
            print("Turning Wi-Fi off.")
            # Implement logic to turn off Wi-Fi
            self.toggle_wifi_button.set_label("Turn Wi-Fi On")
        else:
            print("Turning Wi-Fi on.")
            # Implement logic to turn on Wi-Fi
            self.toggle_wifi_button.set_label("Turn Wi-Fi Off")

def main():
    # Initialize and run the Wi-Fi widget
    window = WiFiWidget()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()

    Gtk.main()

if __name__ == "__main__":
    main()
