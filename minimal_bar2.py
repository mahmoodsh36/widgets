from gi.repository import Gtk, Gdk, GtkLayerShell, GLib
import datetime

class SystemBar(Gtk.Window):
    def __init__(self):
        super().__init__(title="System Bar")

        # Set window properties
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)  # Makes it a dock-like window
        self.set_decorated(False)  # Remove window decorations
        self.set_resizable(False)  # Prevent resizing
        self.set_default_size(1440, 30)  # Set the width to 1440px and height of 30px for the bar
        self.move(0, 0)  # Position at the top-left corner

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

        # Create the layout container
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box.set_homogeneous(False)

        # Left section for workspace buttons (you can dynamically add buttons)
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        left_box.set_hexpand(False)  # Do not expand to fill extra space
        # Example workspace buttons (use dynamic logic as needed)
        workspace_button1 = Gtk.Button(label="Workspace 1")
        workspace_button2 = Gtk.Button(label="Workspace 2")
        
        # Set the buttons' alignment to the left within the box
        left_box.pack_start(workspace_button1, False, False, 0)
        left_box.pack_start(workspace_button2, False, False, 0)

        # Middle section for the current window's title
        middle_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        middle_box.set_hexpand(True)  # This will make it take up the remaining space
        title_label = Gtk.Label(label="Current Window Title")  # Update dynamically
        middle_box.pack_start(title_label, True, True, 0)

        # Right section for the current date
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        right_box.set_hexpand(False)  # Do not expand to fill extra space
        date_label = Gtk.Label(label=self.get_current_date())
        right_box.pack_start(date_label, False, False, 0)

        # Add all sections to the main box
        box.pack_start(left_box, False, False, 10)
        box.pack_start(middle_box, True, True, 10)  # Expands to take remaining space
        box.pack_start(right_box, False, False, 10)

        self.add(box)

        # Update the date label every minute
        GLib.timeout_add_seconds(60, self.update_date, date_label)

        self.show_all()

    def get_current_date(self):
        """Get the current date in a readable format."""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update_date(self, label):
        """Update the date on the right side."""
        label.set_text(self.get_current_date())
        return True

if __name__ == "__main__":
    win = SystemBar()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()
