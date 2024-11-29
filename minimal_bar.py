from gi.repository import Gtk, Gdk, GtkLayerShell

class SystemBar(Gtk.Window):
    def __init__(self):
        super().__init__(title="System Bar")

        # Set window properties
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)  # Makes it a dock-like window
        self.set_decorated(False)  # Remove window decorations
        self.set_resizable(False)  # Prevent resizing
        self.set_default_size(1920, 30)  # Set the height of the bar
        self.move(0, 0)

        # Initialize gtk-layer-shell
        GtkLayerShell.init_for_window(self)

        # Set the window layer to overlay (it stays on top)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)

        # Set margins to avoid overlap
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 0)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT, 0)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 0)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, 0)

        # Anchor the window to the top of the screen
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, 1)

        # Enable auto exclusive zone for space reservation
        GtkLayerShell.auto_exclusive_zone_enable(self)

        # Add content to the system bar
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label="Wayland System Bar Example")
        box.pack_start(label, True, True, 0)
        self.add(box)

        self.show_all()

if __name__ == "__main__":
    win = SystemBar()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()
